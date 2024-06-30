FROM python:3.10

WORKDIR /app/

COPY requirements.txt /app
RUN pip install --upgrade pip &&  python -m pip install -r requirements.txt

COPY . /app
COPY . .env

CMD ["python", "/app/bot.py"]