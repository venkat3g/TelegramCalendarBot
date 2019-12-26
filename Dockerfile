FROM python

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app

COPY token.json ./
COPY client_secret.json ./
COPY ./ ./

CMD ["python", "./app.py"]