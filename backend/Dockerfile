FROM python:3.13-slim

# Astral uv এর অফিসিয়াল ইমেজ থেকে বাইনারি কপি করে আনা (Fastest approach)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /workspace

# সিস্টেম ডিপেন্ডেন্সি ইনস্টল (PostgreSQL ড্রাইভার কম্পাইল করার জন্য)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ডিপেন্ডেন্সি ফাইল কপি করে সিঙ্ক করা (Docker Layer Cache কাজে লাগানোর জন্য)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

# সোর্স কোড কপি করা
COPY . .

# uv এনভায়রনমেন্টের ভার্চুয়াল পাথ পাথ-এ যুক্ত করা
ENV PATH="/workspace/.venv/bin:$PATH"

EXPOSE 8000
