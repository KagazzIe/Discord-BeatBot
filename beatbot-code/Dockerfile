# syntax=docker/dockerfile:1
FROM python:3.8-slim
# RUN mkdir /app
# WORKDIR /app
COPY . .
RUN pip install -r pythonPackages.txt && apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
CMD ["python", "src/main.py"]
EXPOSE 3000