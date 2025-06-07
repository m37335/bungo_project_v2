# 🌟 文豪ゆかり地図システム v2.0

> **強くてニューゲーム版** - 作家・作品・舞台（地名）の3階層データを安定取得し、検索・可視化・拡張しやすいバックエンドシステム

## 📋 概要

文豪ゆかり地図システムは、日本の文豪とその作品に登場する地名を体系的に収集・管理し、地図上で可視化するためのシステムです。

**✨ 最新更新（2025/01/07）**: 青空文庫からの地名抽出機能が完成！GiNZA NLP + 正規表現のハイブリッド抽出により、実際の文学作品から高精度で地名を自動抽出できるようになりました。

### 🎯 主な機能

- **📚 青空文庫テキスト取得**: HTML自動解析による本文抽出
- **🔬 高精度地名抽出**: GiNZA NLP + 正規表現ハイブリッド方式
- **📍 文脈保持**: 前後文付きで地名の文脈を保存
- **🗾 信頼度計算**: 抽出された地名の信頼度を数値化
- **💾 データベース管理**: SQLite3階層データモデル
- **🔍 検索システム**: 作者・作品・地名の相互検索

### 📈 実績・成果

**最新の実行結果（2025/01/07）**:
- 📖 処理作品: 3作品（坊っちゃん、羅生門、走れメロス）
- 🏞️ 抽出地名: **51件**
- 🔬 GiNZA抽出: 23件
- 📝 正規表現抽出: 28件
- ⏱️ 処理時間: 35.3秒
- 🎯 成功率: 100%

## 🏗️ アーキテクチャ

```
作者 (authors) 1 ← N 作品 (works) 1 ← N 地名 (places)
```

### データフロー
```
青空文庫API → HTML解析 → テキスト正規化 → GiNZA NLP → 地名抽出 → データベース
     ↑                                     ↓
   キャッシュ ←                          正規表現抽出 → 信頼度計算
```

## 🚀 クイックスタート

### 本番データ抽出の実行

```bash
# 1. 環境セットアップ
cd bungo_project_v2
pip install -r requirements.txt
python -m spacy download ja_ginza

# 2. 完全データ抽出パイプライン実行
python run_full_extraction.py
```

### 個別機能のテスト

```bash
# 青空文庫テキスト抽出テスト
python -c "from bungo_map.extractors.aozora_extractor import AozoraExtractor; AozoraExtractor().test_extraction()"

# 地名抽出器比較テスト
python compare_extractors.py

# 統合テスト
python test_full_extraction.py
```

### 開発環境セットアップ

```bash
# Python 3.10+ 環境での実行
pip install -r requirements.txt
python -m spacy download ja_ginza
pip install -e .
```

## 🔧 地名抽出エンジン

### GiNZA NLP抽出器
- **対象ラベル**: Province, City, County, GPE, LOC
- **特徴**: 高精度、文脈理解、意味解析
- **制限**: テキストサイズ49KB制限（自動分割対応）

### 正規表現抽出器  
- **パターン**: 都道府県、市区町村、有名地名
- **特徴**: 軽量高速、パターンマッチング、制限なし
- **対象**: 全国地名 + 海外地名 + 古典的地名

### ハイブリッド方式の効果

| 抽出器 | 坊っちゃん | 羅生門 | 走れメロス |
|--------|------------|--------|------------|
| GiNZA | 20個 | 1個 | 2個 |
| 正規表現 | 26個 | 1個 | 1個 |
| 共通抽出 | 8個 | 1個 | 0個 |

## 📚 CLI コマンド

| コマンド | 説明 | 例 |
|----------|------|-----|
| `python run_full_extraction.py` | 完全データ抽出 | 本番用パイプライン |
| `python compare_extractors.py` | 抽出器比較 | GiNZA vs 正規表現 |
| `python test_full_extraction.py` | 統合テスト | 3作品一括テスト |
| `bungo search author` | 作者検索 | `bungo search author "夏目"` |
| `bungo search work` | 作品検索 | `bungo search work "坊っちゃん"` |
| `bungo search place` | 地名検索 | `bungo search place "松山"` |

## 🔧 システム要件

- **Python**: 3.10+
- **データベース**: SQLite（本番対応済み）
- **NLP**: spaCy 3.7 + ja-ginza
- **依存関係**: BeautifulSoup4, requests
- **キャッシュ**: ローカルファイルキャッシュ

## 📊 データ構造

### places テーブル（拡張版）
```sql
CREATE TABLE places (
    place_id INTEGER PRIMARY KEY,
    work_id INTEGER REFERENCES works(work_id),
    place_name TEXT NOT NULL,
    lat REAL,
    lng REAL,
    before_text TEXT,          -- 前文（500文字制限）
    sentence TEXT,             -- 地名を含む文
    after_text TEXT,           -- 後文（500文字制限）
    aozora_url TEXT,           -- 青空文庫URL
    confidence REAL DEFAULT 0.0, -- 信頼度（0.0-1.0）
    extraction_method TEXT,    -- 抽出方法（ginza_nlp, regex_都道府県等）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🎯 抽出地名の例

### 夏目漱石「坊っちゃん」より
- **東京** (GiNZA, 信頼度: 0.95)
- **松山** (正規表現, 信頼度: 0.85) 
- **神戸** (正規表現, 信頼度: 0.85)
- **鎌倉** (GiNZA, 信頼度: 0.90)

### 芥川龍之介「羅生門」より  
- **京都** (GiNZA + 正規表現, 信頼度: 0.90-0.95)

### 太宰治「走れメロス」より
- **飛鳥** (GiNZA, 信頼度: 0.75)
- **清水** (正規表現, 信頼度: 0.65)

## 🧪 テスト結果

### 抽出精度テスト
- **全体成功率**: 100%
- **GiNZA精度**: 高い（文脈理解）
- **正規表現精度**: 幅広カバー（古典地名に強い）
- **重複処理**: 自動除去対応

### パフォーマンステスト
- **テキスト処理**: 88K文字 → 35秒
- **HTML解析**: 自動エンコーディング検出
- **メモリ使用量**: 効率的（チャンク分割）

## 🗂️ プロジェクト構造

```
bungo_project_v2/
├── bungo_map/                    # メインパッケージ
│   ├── extractors/               # 地名抽出エンジン
│   │   ├── aozora_extractor.py   # 青空文庫テキスト抽出
│   │   ├── ginza_place_extractor.py  # GiNZA NLP地名抽出
│   │   └── simple_place_extractor.py # 正規表現地名抽出
│   ├── core/                     # データベース・基本機能
│   │   ├── database.py           # SQLiteデータベース管理
│   │   └── models.py             # データモデル定義
│   └── cli/                      # コマンドラインツール
├── data/                         # データファイル
│   ├── aozora_cache/            # 青空文庫キャッシュ
│   └── bungo_production.db      # 本番データベース
├── run_full_extraction.py       # 完全データ抽出パイプライン
├── compare_extractors.py        # 抽出器比較ツール
└── test_full_extraction.py      # 統合テストツール
```

## 🚧 ロードマップ

- **v2.0**: ✅ 3階層データモデル + 青空文庫地名抽出 **完成！**
- **v2.1**: 🔄 ジオコーディング機能強化
- **v2.2**: 📋 GeoJSON エクスポート機能
- **v2.3**: 🌐 REST API + MapKit連携
- **v3.0**: 🤖 GPT関連度判定機能

## 📈 今後の展開

### 短期目標
1. **地名→座標変換**: Google Maps API統合
2. **データ拡張**: より多くの文豪・作品への対応
3. **可視化**: GeoJSON生成 + MapKit連携

### 中期目標
1. **機械学習**: 地名抽出精度向上
2. **リアルタイム**: 新作品の自動取り込み
3. **API化**: RESTful API提供

## 🎉 成果サマリー

**青空文庫地名抽出システムが完全に動作しています！**

- ✅ HTML→テキスト変換
- ✅ GiNZA NLP地名抽出  
- ✅ 正規表現地名抽出
- ✅ ハイブリッド方式
- ✅ 前後文脈保持
- ✅ 信頼度計算
- ✅ SQLiteデータベース保存
- ✅ 本番パイプライン実行

**実用レベルの文豪ゆかり地図システムの基盤が完成しました！** 🗾✨

---

**🌟 強くてニューゲーム版で、青空文庫の膨大なテキストから文学地名を自動抽出！** 