FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential git curl vim && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

WORKDIR /app/hf_negotiate

ENTRYPOINT ["python", "-m", "hf_negotiate"]
CMD ["testing", "data"]







