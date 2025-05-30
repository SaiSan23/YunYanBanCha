FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY seed_all.py .

CMD ["python", "seed_all.py"]