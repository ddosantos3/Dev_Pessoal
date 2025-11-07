FROM node:20-slim AS frontend-builder
WORKDIR /frontend
COPY src/app/frontend/quest-talk-gui/package.json ./
COPY src/app/frontend/quest-talk-gui/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY src/app/frontend/quest-talk-gui ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY --from=frontend-builder /frontend/dist ./src/app/frontend/quest-talk-gui/dist
ENV PYTHONPATH=/app/src
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
