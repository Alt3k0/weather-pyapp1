FROM python:alpine

RUN pip3 install flask redis requests

WORKDIR /app

ADD app.py app.py

ADD templates templates


CMD ["python3", "app.py"]
