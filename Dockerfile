FROM python:3.13-slim@sha256:3dd7cc108ec1493442514f5c2a871af6af0ec31d768ff6e378a93340c3b3db5f

RUN groupadd --system app \
    && useradd --system --gid app --create-home app

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=app:app requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --upgrade urllib3 msgpack

COPY --chown=app:app . .

ENV PYTHONPATH=/app/src
ENV FLASK_APP=company_website

USER app

EXPOSE 7000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7000", "--access-logfile", "-", "wsgi:app"]
