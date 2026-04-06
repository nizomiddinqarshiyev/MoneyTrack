FROM python:3.12-slim

WORKDIR /app

COPY antifraud_requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir numpy==1.26.4

COPY . .

CMD ["uvicorn", "antifraud.main:app", "--host", "0.0.0.0", "--port", "8000"]
