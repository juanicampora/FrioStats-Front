FROM python:3.11.3-slim-buster

COPY . /usr/src/app

WORKDIR /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt


CMD ["python", "run.py"]
