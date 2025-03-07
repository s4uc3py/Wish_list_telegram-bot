FROM python:3.9-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir .

COPY . .

CMD ["python", "wishlist-bot.py"]
