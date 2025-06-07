#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベース機能テスト
仕様書Done Criteria対応
"""

import pytest
import tempfile
import os
from pathlib import Path
from bungo_map.core.database import Database, BungoDatabase
from bungo_map.core.models import Author, Work, Place


class TestDatabase:
    """データベース機能テスト"""
    
    @pytest.fixture
    def temp_db(self):
        """テスト用一時データベース"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = Database(db_path)
        yield db
        
        # クリーンアップ
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_database_initialization(self, temp_db):
        """データベース初期化テスト"""
        assert temp_db is not None
        
        # テーブル存在確認
        with temp_db.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'authors' in tables
            assert 'works' in tables
            assert 'places' in tables
    
    def test_author_operations(self, temp_db):
        """作者操作テスト（CRUD）"""
        # 作者作成
        author = Author(
            name="夏目漱石",
            wikipedia_url="https://ja.wikipedia.org/wiki/夏目漱石",
            birth_year=1867,
            death_year=1916
        )
        
        # 作者挿入
        author_id = temp_db.insert_author(author)
        assert author_id is not None
        assert author_id > 0
        
        # 作者検索
        found_author = temp_db.get_author_by_name("夏目漱石")
        assert found_author is not None
        assert found_author.name == "夏目漱石"
        assert found_author.birth_year == 1867
        
        # 重複挿入テスト（既存作者）
        duplicate_id = temp_db.insert_author(author)
        assert duplicate_id == author_id  # 同じIDが返される
    
    def test_work_operations(self, temp_db):
        """作品操作テスト"""
        # 前提：作者を先に作成
        author = Author(name="芥川龍之介", birth_year=1892, death_year=1927)
        author_id = temp_db.insert_author(author)
        
        # 作品作成
        work = Work(
            author_id=author_id,
            title="羅生門",
            wiki_url="https://ja.wikipedia.org/wiki/羅生門",
            aozora_url="https://www.aozora.gr.jp/cards/000879/files/127_15260.html"
        )
        
        # 作品挿入
        work_id = temp_db.insert_work(work)
        assert work_id is not None
        assert work_id > 0
        
        # 作品検索
        works = temp_db.search_works("羅生門")
        assert len(works) == 1
        assert works[0]['title'] == "羅生門"
        assert works[0]['author_name'] == "芥川龍之介"
    
    def test_place_operations(self, temp_db):
        """地名操作テスト"""
        # 前提：作者・作品を作成
        author = Author(name="太宰治")
        author_id = temp_db.insert_author(author)
        
        work = Work(author_id=author_id, title="走れメロス")
        work_id = temp_db.insert_work(work)
        
        # 地名作成
        place = Place(
            work_id=work_id,
            place_name="シラクス",
            lat=37.0755,
            lng=15.2866,
            sentence="メロスはシラクスの市に出て来た",
            confidence=0.95,
            extraction_method="test"
        )
        
        # 地名挿入
        place_id = temp_db.insert_place(place)
        assert place_id is not None
        assert place_id > 0
        
        # 地名検索
        places = temp_db.search_places("シラクス")
        assert len(places) >= 1
        found_place = places[0]
        assert found_place['place_name'] == "シラクス"
        assert found_place['author_name'] == "太宰治"
        assert found_place['work_title'] == "走れメロス"
    
    def test_search_functionality(self, temp_db):
        """検索機能テスト（双方向検索）"""
        # テストデータ作成
        self._create_test_data(temp_db)
        
        # 1. 作者検索
        authors = temp_db.search_authors("夏目")
        assert len(authors) >= 1
        assert any(a['name'] == "夏目漱石" for a in authors)
        
        # 2. 作品検索
        works = temp_db.search_works("坊っちゃん")
        assert len(works) >= 1
        assert any(w['title'] == "坊っちゃん" for w in works)
        
        # 3. 地名検索
        places = temp_db.search_places("松山")
        assert len(places) >= 1
        assert any(p['place_name'] == "松山市" for p in places)
        
        # 4. 双方向検索確認
        # 作者→作品→地名→逆引き
        author_works = temp_db.get_works_by_author(1)  # 夏目漱石のID=1と仮定
        assert len(author_works) >= 1
        
        if author_works:
            work_places = temp_db.get_places_by_work(author_works[0]['work_id'])
            # 地名が存在すれば双方向検索成功
            if work_places:
                reverse_places = temp_db.search_places(work_places[0]['place_name'])
                assert len(reverse_places) >= 1
    
    def test_statistics(self, temp_db):
        """統計機能テスト"""
        # テストデータ作成
        self._create_test_data(temp_db)
        
        # 統計取得
        stats = temp_db.get_statistics()
        
        assert 'authors_count' in stats
        assert 'works_count' in stats
        assert 'places_count' in stats
        assert 'geocoded_count' in stats
        assert 'geocoded_rate' in stats
        
        assert stats['authors_count'] >= 1
        assert stats['works_count'] >= 1
        assert stats['places_count'] >= 1
        assert 0 <= stats['geocoded_rate'] <= 100
    
    def test_performance(self, temp_db):
        """性能テスト（0.5秒以内）"""
        import time
        
        # テストデータ作成
        self._create_test_data(temp_db)
        
        # 検索性能テスト
        test_cases = [
            ("search_authors", "夏目"),
            ("search_works", "坊っちゃん"),
            ("search_places", "松山")
        ]
        
        for method_name, query in test_cases:
            start_time = time.time()
            method = getattr(temp_db, method_name)
            result = method(query)
            execution_time = time.time() - start_time
            
            # 仕様書要件：0.5秒以内
            assert execution_time < 0.5, f"{method_name}が0.5秒を超過: {execution_time:.3f}秒"
            assert len(result) >= 0  # 結果は0件以上
    
    def _create_test_data(self, db):
        """テスト用データ作成"""
        # 作者
        author = Author(name="夏目漱石", birth_year=1867, death_year=1916)
        author_id = db.insert_author(author)
        
        # 作品
        work = Work(author_id=author_id, title="坊っちゃん")
        work_id = db.insert_work(work)
        
        # 地名
        place = Place(
            work_id=work_id,
            place_name="松山市",
            lat=33.8395,
            lng=132.7654,
            sentence="汽車が松山市に着いた時には、もう日が暮れていた",
            confidence=0.90,
            extraction_method="test"
        )
        db.insert_place(place)


class TestBungoDatabase:
    """BungoDatabase互換性テスト"""
    
    def test_bungo_database_compatibility(self):
        """BungoDatabaseクラスの互換性テスト"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            # BungoDatabaseインスタンス作成
            bungo_db = BungoDatabase(db_path)
            
            # 基本機能テスト
            stats = bungo_db.get_statistics()
            assert isinstance(stats, dict)
            
            # close()メソッドテスト（エラーが出ないこと）
            bungo_db.close()
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestDataIntegrity:
    """データ整合性テスト"""
    
    @pytest.fixture
    def populated_db(self):
        """データが入った一時データベース"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = Database(db_path)
        
        # テストデータ作成
        author = Author(name="宮沢賢治", birth_year=1896, death_year=1933)
        author_id = db.insert_author(author)
        
        work = Work(author_id=author_id, title="銀河鉄道の夜")
        work_id = db.insert_work(work)
        
        place = Place(
            work_id=work_id,
            place_name="岩手県",
            sentence="岩手県の美しい風景",
            confidence=0.85
        )
        db.insert_place(place)
        
        yield db
        
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_foreign_key_integrity(self, populated_db):
        """外部キー整合性テスト"""
        with populated_db.get_connection() as conn:
            # 作品は必ず作者に紐づく
            cursor = conn.execute("""
                SELECT COUNT(*) FROM works w 
                LEFT JOIN authors a ON w.author_id = a.author_id 
                WHERE a.author_id IS NULL
            """)
            orphaned_works = cursor.fetchone()[0]
            assert orphaned_works == 0
            
            # 地名は必ず作品に紐づく
            cursor = conn.execute("""
                SELECT COUNT(*) FROM places p 
                LEFT JOIN works w ON p.work_id = w.work_id 
                WHERE w.work_id IS NULL
            """)
            orphaned_places = cursor.fetchone()[0]
            assert orphaned_places == 0
    
    def test_data_consistency(self, populated_db):
        """データ一貫性テスト"""
        # 検索結果の一貫性
        authors = populated_db.search_authors("宮沢")
        assert len(authors) == 1
        
        author_id = authors[0]['author_id']
        works = populated_db.get_works_by_author(author_id)
        assert len(works) >= 1
        
        work_id = works[0]['work_id']
        places = populated_db.get_places_by_work(work_id)
        assert len(places) >= 1
        
        # 逆引き確認
        place_name = places[0]['place_name']
        reverse_places = populated_db.search_places(place_name)
        assert len(reverse_places) >= 1
        assert reverse_places[0]['author_name'] == "宮沢賢治" 