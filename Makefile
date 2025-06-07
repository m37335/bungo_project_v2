# 🌟 文豪ゆかり地図システム v2.0 Makefile
# 強くてニューゲーム版

.PHONY: help build up down shell test clean install lint format check

# デフォルトターゲット
help:
	@echo "🌟 文豪ゆかり地図システム v2.0 開発コマンド"
	@echo ""
	@echo "📦 環境構築:"
	@echo "  build    - Dockerイメージビルド"
	@echo "  up       - 開発環境起動"
	@echo "  down     - 開発環境停止"
	@echo "  shell    - 開発コンテナシェル"
	@echo ""
	@echo "🛠️ 開発:"
	@echo "  install  - 依存関係インストール"
	@echo "  test     - テスト実行"
	@echo "  lint     - リント実行"
	@echo "  format   - コードフォーマット"
	@echo "  check    - 品質チェック全実行"
	@echo ""
	@echo "🗂️ データ:"
	@echo "  collect  - サンプルデータ収集"
	@echo "  db-init  - データベース初期化"
	@echo "  export   - データエクスポート"
	@echo ""
	@echo "🚀 実行:"
	@echo "  server   - API server起動"
	@echo "  demo     - デモデータでテスト"

# === 環境構築 ===
build:
	@echo "📦 Dockerイメージビルド中..."
	docker-compose build

up:
	@echo "🚀 開発環境起動中..."
	docker-compose up -d
	@echo "✅ 開発環境が起動しました！"
	@echo "   - コンテナシェル: make shell"
	@echo "   - API server: make server"

down:
	@echo "🛑 開発環境停止中..."
	docker-compose down

shell:
	@echo "🐚 開発コンテナシェル起動..."
	docker-compose exec bungo-dev bash

# === 開発 ===
install:
	@echo "📥 依存関係インストール中..."
	pip install -e .[dev]
	python -m spacy download ja_core_news_sm

test:
	@echo "🧪 テスト実行中..."
	pytest tests/ -v --tb=short

test-cov:
	@echo "📊 カバレッジ付きテスト実行中..."
	pytest tests/ --cov=bungo_map --cov-report=html --cov-report=term

lint:
	@echo "🔍 リント実行中..."
	flake8 bungo_map/ tests/
	# mypy bungo_map/  # mypy未インストールの場合はコメントアウト

format:
	@echo "🎨 コードフォーマット中..."
	black bungo_map/ tests/
	isort bungo_map/ tests/

check: lint test
	@echo "✅ 品質チェック完了！"

# === CI/CD Pipeline ===
ci: install lint test-cov integration-test performance-test
	@echo "🚀 CI/CD パイプライン完了！"

integration-test:
	@echo "🔗 統合テスト実行中..."
	python -m bungo_map.cli.main collect --demo
	python -m bungo_map.cli.search stats --db data/bungo_production.db
	python -m bungo_map.cli.search author "夏目" --db data/bungo_production.db
	python -m bungo_map.cli.main export --format geojson --preview

performance-test:
	@python performance_test.py

# === データ操作 ===
db-init:
	@echo "🗄️ データベース初期化中..."
	python -c "from bungo_map.core.database import init_db; init_db()"

collect:
	@echo "📚 サンプルデータ収集中..."
	bungo collect --author "夏目漱石" --limit 3

export:
	@echo "📤 データエクスポート中..."
	bungo export geojson
	bungo export csv

# === 実行 ===
server:
	@echo "🌐 API server起動中..."
	bungo-server --host 0.0.0.0 --port 8000

demo: db-init collect
	@echo "🎭 デモ環境セットアップ完了！"
	@echo "   - API: http://localhost:8000/docs"
	@echo "   - 検索テスト: bungo search work 坊っちゃん"

# === ユーティリティ ===
clean:
	@echo "🧹 キャッシュクリア中..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +

logs:
	@echo "📜 ログ表示..."
	docker-compose logs -f bungo-dev

ps:
	@echo "📋 コンテナ状況:"
	docker-compose ps

# === 本番環境 ===
prod-build:
	@echo "🏭 本番用ビルド..."
	docker build -f Dockerfile.prod -t bungo-map:prod .

# === 開発支援 ===
jupyter:
	@echo "📓 Jupyter Lab起動..."
	docker-compose exec bungo-dev jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root

# === プロジェクト管理 ===
status:
	@echo "📊 プロジェクト状況:"
	@echo "  - Git: $(shell git branch --show-current)"
	@echo "  - Docker: $(shell docker-compose ps --format table)"
	@echo "  - Python: $(shell python --version 2>/dev/null || echo 'Not available')" 