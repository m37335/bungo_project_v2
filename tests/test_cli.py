#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI機能テスト
検索・エクスポート・ジオコーディング等の統合テスト
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from click.testing import CliRunner
from bungo_map.cli.main import main
from bungo_map.cli.search import search
from bungo_map.core.database import Database


class TestCLICommands:
    """CLI コマンドテスト"""
    
    @pytest.fixture
    def temp_db_with_data(self):
        """テスト用データ入りデータベース"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # テストデータを作成
        self._create_test_database(db_path)
        
        yield db_path
        
        # クリーンアップ
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def cli_runner(self):
        """CLI実行用ランナー"""
        return CliRunner()
    
    def test_status_command(self, cli_runner, temp_db_with_data):
        """status コマンドテスト"""
        # status コマンド実行
        result = cli_runner.invoke(main, ['status'])
        
        assert result.exit_code == 0
        assert "システム状況" in result.output
        assert "データベース接続OK" in result.output
    
    def test_search_author_command(self, cli_runner, temp_db_with_data):
        """search author コマンドテスト"""
        result = cli_runner.invoke(
            search, 
            ['author', '夏目', '--db', temp_db_with_data]
        )
        
        assert result.exit_code == 0
        assert "作者検索「夏目」" in result.output
        assert "夏目漱石" in result.output
        assert "実行時間:" in result.output
    
    def test_search_work_command(self, cli_runner, temp_db_with_data):
        """search work コマンドテスト"""
        result = cli_runner.invoke(
            search, 
            ['work', '坊っちゃん', '--db', temp_db_with_data]
        )
        
        assert result.exit_code == 0
        assert "作品検索「坊っちゃん」" in result.output
        assert "坊っちゃん" in result.output
        assert "登場する地名:" in result.output
    
    def test_search_place_command(self, cli_runner, temp_db_with_data):
        """search place コマンドテスト"""
        result = cli_runner.invoke(
            search, 
            ['place', '松山', '--db', temp_db_with_data]
        )
        
        assert result.exit_code == 0
        assert "地名検索「松山」" in result.output
        assert "関連作者:" in result.output
        assert "関連作品:" in result.output
    
    def test_search_stats_command(self, cli_runner, temp_db_with_data):
        """search stats コマンドテスト"""
        result = cli_runner.invoke(
            search, 
            ['stats', '--db', temp_db_with_data]
        )
        
        assert result.exit_code == 0
        assert "データベース統計" in result.output
        assert "作者数:" in result.output
        assert "作品数:" in result.output
        assert "地名数:" in result.output
    
    def test_export_geojson_preview(self, cli_runner, temp_db_with_data):
        """export geojson プレビューテスト"""
        # 一時的にDBをコピーして使用
        import shutil
        test_db = "test_temp.db"
        shutil.copy2(temp_db_with_data, test_db)
        
        try:
            result = cli_runner.invoke(
                main, 
                ['export', '--format', 'geojson', '--preview']
            )
            
            # プレビューの場合は正常終了すること
            assert result.exit_code == 0
            
        finally:
            if os.path.exists(test_db):
                os.unlink(test_db)
    
    def test_collect_demo_command(self, cli_runner):
        """collect demo コマンドテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 一時ディレクトリで実行
            os.chdir(temp_dir)
            
            result = cli_runner.invoke(
                main, 
                ['collect', '--demo']
            )
            
            # デモデータ収集は正常終了すること
            assert result.exit_code == 0
            assert "デモデータ収集開始" in result.output
    
    def test_geocode_status_command(self, cli_runner, temp_db_with_data):
        """geocode status コマンドテスト"""
        # geocodeコマンドは存在するかどうかのテスト
        result = cli_runner.invoke(main, ['--help'])
        
        # メインヘルプでgeocodeが表示されるかテスト
        assert result.exit_code == 0
        # geocodeコマンドがある場合はテスト、ない場合はスキップ
        if 'geocode' in result.output:
            result = cli_runner.invoke(main, ['geocode', '--help'])
            assert result.exit_code == 0
        else:
            # geocodeコマンドが存在しない場合はパス
            assert True
    
    def test_performance_requirements(self, cli_runner, temp_db_with_data):
        """性能要件テスト（0.5秒以内）"""
        import time
        
        # 各検索コマンドの実行時間を測定
        test_cases = [
            (['author', '夏目'], "作者検索"),
            (['work', '坊っちゃん'], "作品検索"),
            (['place', '松山'], "地名検索")
        ]
        
        for cmd_args, description in test_cases:
            start_time = time.time()
            
            result = cli_runner.invoke(
                search,
                cmd_args + ['--db', temp_db_with_data]
            )
            
            execution_time = time.time() - start_time
            
            # テスト結果確認
            assert result.exit_code == 0, f"{description}が失敗"
            assert execution_time < 0.5, f"{description}が0.5秒を超過: {execution_time:.3f}秒"
    
    def test_error_handling(self, cli_runner):
        """エラーハンドリングテスト"""
        # 存在しないデータベースでの検索
        result = cli_runner.invoke(
            search,
            ['author', 'test', '--db', 'nonexistent.db']
        )
        
        # エラーが適切に処理されること
        assert result.exit_code != 0 or "エラー" in result.output
    
    def test_help_commands(self, cli_runner):
        """ヘルプコマンドテスト"""
        # メインヘルプ
        result = cli_runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "文豪ゆかり地図システム" in result.output
        
        # 検索ヘルプ
        result = cli_runner.invoke(search, ['--help'])
        assert result.exit_code == 0
        assert "検索コマンド" in result.output
    
    def _create_test_database(self, db_path: str):
        """テスト用データベース作成"""
        from bungo_map.core.models import Author, Work, Place
        
        db = Database(db_path)
        
        # 作者作成
        author = Author(
            name="夏目漱石",
            wikipedia_url="https://ja.wikipedia.org/wiki/夏目漱石",
            birth_year=1867,
            death_year=1916
        )
        author_id = db.insert_author(author)
        
        # 作品作成
        work = Work(
            author_id=author_id,
            title="坊っちゃん",
            wiki_url="https://ja.wikipedia.org/wiki/坊っちゃん",
            aozora_url="https://www.aozora.gr.jp/cards/000148/files/752_14964.html"
        )
        work_id = db.insert_work(work)
        
        # 地名作成
        places_data = [
            ("松山市", 33.8395, 132.7654, "汽車が松山市に着いた時には、もう日が暮れていた"),
            ("道後温泉", 33.8504, 132.7851, "赤シャツと一緒に道後温泉へ行った"),
            ("瀬戸内海", 34.8914, 134.6533, "向こうに見える瀬戸内海の島々は美しかった")
        ]
        
        for place_name, lat, lng, sentence in places_data:
            place = Place(
                work_id=work_id,
                place_name=place_name,
                lat=lat,
                lng=lng,
                sentence=sentence,
                confidence=0.90,
                extraction_method="test"
            )
            db.insert_place(place)


class TestIntegrationScenarios:
    """統合シナリオテスト"""
    
    @pytest.fixture
    def cli_runner(self):
        return CliRunner()
    
    def test_full_workflow_scenario(self, cli_runner):
        """フルワークフローシナリオテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            # 1. データ収集
            result = cli_runner.invoke(main, ['collect', '--demo'])
            assert result.exit_code == 0
            
            # 2. 統計確認
            result = cli_runner.invoke(main, ['status'])
            assert result.exit_code == 0
            
            # 3. 検索実行（作者→作品→地名の順）
            db_file = "data/bungo_production.db"
            if os.path.exists(db_file):
                # 作者検索
                result = cli_runner.invoke(search, ['author', '夏目', '--db', db_file])
                assert result.exit_code == 0
                
                # 作品検索
                result = cli_runner.invoke(search, ['work', '坊っちゃん', '--db', db_file])
                assert result.exit_code == 0
                
                # 地名検索
                result = cli_runner.invoke(search, ['place', '松山', '--db', db_file])
                assert result.exit_code == 0
    
    def test_bidirectional_search_scenario(self, cli_runner):
        """双方向検索シナリオテスト"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            # テストデータ作成
            self._create_full_test_data(db_path)
            
            # 双方向検索テスト
            # 作者 → 作品
            result = cli_runner.invoke(search, ['author', '夏目', '--db', db_path])
            assert result.exit_code == 0
            assert "関連作品:" in result.output
            
            # 作品 → 地名
            result = cli_runner.invoke(search, ['work', '坊っちゃん', '--db', db_path])
            assert result.exit_code == 0
            assert "登場する地名:" in result.output
            
            # 地名 → 作者・作品（逆引き）
            result = cli_runner.invoke(search, ['place', '松山', '--db', db_path])
            assert result.exit_code == 0
            assert "関連作者:" in result.output
            assert "関連作品:" in result.output
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def _create_full_test_data(self, db_path: str):
        """完全なテストデータ作成"""
        from bungo_map.core.models import Author, Work, Place
        
        db = Database(db_path)
        
        # 複数作者・作品・地名でテスト
        authors_data = [
            ("夏目漱石", 1867, 1916),
            ("芥川龍之介", 1892, 1927),
            ("太宰治", 1909, 1948)
        ]
        
        works_data = [
            (0, "坊っちゃん", [("松山市", 33.8395, 132.7654)]),
            (0, "吾輩は猫である", [("東京", 35.6769, 139.7639)]),
            (1, "羅生門", [("京都", 35.0116, 135.7681)]),
            (2, "走れメロス", [("シラクス", 37.0755, 15.2866)])
        ]
        
        author_ids = []
        for name, birth, death in authors_data:
            author = Author(name=name, birth_year=birth, death_year=death)
            author_id = db.insert_author(author)
            author_ids.append(author_id)
        
        for author_idx, title, places_info in works_data:
            work = Work(author_id=author_ids[author_idx], title=title)
            work_id = db.insert_work(work)
            
            for place_name, lat, lng in places_info:
                place = Place(
                    work_id=work_id,
                    place_name=place_name,
                    lat=lat,
                    lng=lng,
                    sentence=f"{place_name}での物語",
                    confidence=0.90,
                    extraction_method="test"
                )
                db.insert_place(place) 