FROM python:3.13-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

LABEL authors="Pham Le Gia Dai <daipham.32132@gmail.com>"
LABEL description="A bot for getting stories from Hacker News"

WORKDIR /app/hackernews.bot

COPY . .
RUN uv sync --frozen

CMD ["hackernews-bot"]