FROM python:3.13-slim@sha256:3dd7cc108ec1493442514f5c2a871af6af0ec31d768ff6e378a93340c3b3db5f

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    FLASK_APP=company_website

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app \
    && apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --upgrade urllib3 msgpack

COPY --chown=root:app . .
RUN mkdir -p /app/data && chown app:app /app/data

USER 10001:10001
EXPOSE 7000

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7000", "--worker-tmp-dir", "/dev/shm", "--access-logfile", "-", "wsgi:app"]
