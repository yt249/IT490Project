FROM python
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENV FLASK_APP=app.py
CMD ["./wait-for-it.sh", "messaging:5672", "--", \
     "flask", "run", "--host=0.0.0.0"]