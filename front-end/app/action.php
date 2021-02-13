<?php

require('rpc_client.php');

$action = $_POST['action'];
$data = $_POST['data'];

echo "Establishing connection to messaging service... ";
$rpc = new RpcClient();
echo "[SUCCESS]<br>";

echo "Sending {action: \"$action\", data: \"$data\"} to the send procedure and waiting for response...";
$response = $rpc->send($action, $data);
echo "[SUCCESS]<br>";
echo "Response: <br>";
echo "<pre>";
print_r($response);
echo "</pre>";

?>