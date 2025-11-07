FROM python:3.11-slim
WORKDIR /app
COPY custom_exporter.py /app/custom_exporter.py
RUN pip install --no-cache-dir prometheus-client requests
EXPOSE 8000
CMD ["python", "custom_exporter.py"]
