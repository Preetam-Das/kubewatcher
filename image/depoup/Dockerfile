FROM python:slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py lib.py .
CMD ["python", "-u", "main.py"]
