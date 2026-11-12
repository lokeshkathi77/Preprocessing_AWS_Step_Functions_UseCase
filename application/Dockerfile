FROM public.ecr.aws/amazonlinux/amazonlinux:2023

RUN dnf install -y python3-pip && \
    pip3 install --no-cache-dir boto3 && \
    dnf clean all

WORKDIR /app
COPY worker.py .

ENTRYPOINT ["python3", "/app/worker.py"]
