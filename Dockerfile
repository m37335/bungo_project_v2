FROM python:3.10.5-slim

LABEL maintainer="bungo-map-dev"
LABEL description="文豪ゆかり地図システム v2.0 開発環境 (Python 3.10.5)"

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    libmecab-dev \
    mecab \
    mecab-ipadic-utf8 \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# MeCab辞書の設定
RUN echo "dicdir = /var/lib/mecab/dic/debian" > /etc/mecabrc

# Pythonの依存関係
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# GiNZAの追加インストール（Python 3.10.5対応）
RUN python -m spacy download ja_core_news_sm

# 作業ディレクトリ設定
WORKDIR /app

# ソースコード用ディレクトリ作成
RUN mkdir -p /app/bungo_map \
    /app/data \
    /app/output \
    /app/cache \
    /app/tests

# 環境変数設定
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV BUNGO_DATA_DIR="/app/data"
ENV BUNGO_OUTPUT_DIR="/app/output"
ENV BUNGO_CACHE_DIR="/app/cache"

# 非rootユーザー作成
RUN useradd -m -u 1000 developer && \
    chown -R developer:developer /app
USER developer

# デフォルトコマンド
CMD ["/bin/bash"] 