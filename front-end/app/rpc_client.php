<?php

require_once __DIR__ . '/vendor/autoload.php';
use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

class RpcClient
{
    private $connection;
    private $channel;
    private $callback_queue;
    private $response;
    private $corr_id;

    public $timeout = 10;
    public $hostname = 'messaging';

    public function __construct()
    {
        $user = $_ENV['MSG_USER'];
        $pass = $_ENV['MSG_PASS'];

        $this->connection = new AMQPStreamConnection(
            $this->hostname,
            5672,
            $user,
            $pass
        );
        $this->channel = $this->connection->channel();
        list($this->callback_queue, ,) = $this->channel->queue_declare(
            "",
            false,
            false,
            true,
            false
        );
        $this->channel->basic_consume(
            $this->callback_queue,
            '',
            false,
            true,
            false,
            false,
            array(
                $this,
                'onResponse'
            )
        );
    }

    public function onResponse($rep)
    {
        if ($rep->get('correlation_id') == $this->corr_id) {
            $this->response = json_decode($rep->body);
        }
    }

    public function send($action, $data)
    {
        $this->response = null;
        $this->corr_id = uniqid();
        $json = json_encode(array('action'=>$action, 'data'=>$data));

        $msg = new AMQPMessage(
            $json,
            array(
                'correlation_id' => $this->corr_id,
                'reply_to' => $this->callback_queue
            )
        );
        $this->channel->basic_publish($msg, '', 'requests');
        while (!$this->response) {
            $this->channel->wait(null, false, $this->timeout);
        }
        return $this->response;
    }
}

?>