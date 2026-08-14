FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OPERATIONAL_AGENTS_ROOT=/app OPERATIONAL_AGENTS_ALLOW_REMOTE_BIND=1
WORKDIR /app
COPY . /app
RUN python -m pip install --no-cache-dir . && useradd --create-home --uid 10001 agentuser
USER agentuser
EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/healthz', timeout=2)"
CMD ["operational-agents", "serve", "--host", "0.0.0.0", "--port", "8765"]
