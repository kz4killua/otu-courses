FROM python:3.11.1

# Install netcat for TCP health checks
RUN apt-get update && apt-get install -y netcat

COPY . /app
WORKDIR /app

RUN pip install pip --upgrade && \
    pip install -r requirements.txt && \
    chmod +x entrypoint.sh

CMD ["/app/entrypoint.sh"]