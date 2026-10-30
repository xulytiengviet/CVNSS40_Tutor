# CVNSS4.0 standalone MCP only. Does NOT build or replace the full DeepTutor app.
FROM node:22-bookworm-slim AS nodejs

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates libstdc++6 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=nodejs /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
RUN python -m pip install --no-cache-dir "mcp>=1.26.0,<2.0.0" "uvicorn>=0.30,<1.0"
COPY cvnss_hub/ /app/cvnss_hub/
RUN python -c "from cvnss_hub.service import execute; r=execute('self_test'); assert r['ok'] and r['tests']==23"
RUN useradd --create-home --uid 10001 appuser
USER appuser
EXPOSE 10000
# A single worker is intentional: the in-process rate limiter is per worker.
CMD ["sh", "-c", "exec uvicorn cvnss_hub.hosted:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1 --no-access-log"]
