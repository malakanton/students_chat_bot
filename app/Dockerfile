FROM python:3.10

WORKDIR /app/

COPY .env /app

COPY requirements.txt /app
RUN pip install --upgrade pip &&  python -m pip install -r requirements.txt

COPY . /app


CMD ["python", "/app/bot.py"]