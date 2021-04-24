FROM python:3.9-slim-buster
LABEL maintainer="bomzheg <bomzheg@gmail.com>" \
      description="Karma Telegram Bot"
COPY requirements.txt requirements.txt
RUN apt update -y \
    && apt install -y gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt purge -y gcc \
    && apt autoclean -y \
    && apt autoremove -y \
    && rm -rf /var/lib/apt/lists/*
VOLUME /log
VOLUME /db_data
VOLUME /jsons
WORKDIR "."
EXPOSE 3000
COPY config config
COPY app app
ENTRYPOINT ["python3", "-m", "app", "-p"]
