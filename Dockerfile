FROM python:3-slim

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app

COPY ./ ./

CMD ["python", "./app.py"]
