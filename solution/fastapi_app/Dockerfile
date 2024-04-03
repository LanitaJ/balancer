FROM python:3.8.18

WORKDIR /app

COPY . .

RUN python3 -m pip install -r requirements.txt

EXPOSE 8000

CMD python main.py
