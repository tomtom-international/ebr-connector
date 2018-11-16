FROM python:3.6.7-alpine3.7
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
