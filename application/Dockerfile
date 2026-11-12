FROM public.ecr.aws/docker/library/python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY processor.py .

RUN useradd --create-home appuser
USER appuser

ENV PYTHONUNBUFFERED=1
ENV RUN_MODE=s3

ENTRYPOINT ["python", "processor.py"]
