FROM python:3.12-bookworm as builder
ENV VIRTUAL_ENV=/opt/venv
COPY pyproject.toml pyproject.toml
RUN mkdir app
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install .

FROM python:3.12-slim-bookworm
LABEL maintainer="bomzheg <bomzheg@gmail.com>" \
      description="Karma Telegram Bot"
ENV VIRTUAL_ENV=/opt/venv
COPY --from=builder $VIRTUAL_ENV $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
VOLUME /log
VOLUME /db_data
VOLUME /config
WORKDIR "."
EXPOSE 3000
VOLUME /config
COPY app app
COPY migrations migrations
ENTRYPOINT ["python3", "-m", "app", "-p"]
