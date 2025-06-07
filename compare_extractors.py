#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地名抽出器比較テスト：GiNZA vs 正規表現ベース
"""

from bungo_map.extractors.aozora_extractor import AozoraExtractor
from bungo_map.extractors.ginza_place_extractor import GinzaPlaceExtractor
from bungo_map.extractors.simple_place_extractor import SimplePlaceExtractor


def compare_extractors():
    """地名抽出器の比較テスト"""
    print("🔍 地名抽出器比較テスト")
    print("=" * 60)
    
    # 青空文庫テキスト取得
    aozora = AozoraExtractor()
    works = aozora.get_sample_works()
    
    # 抽出器初期化
    ginza_extractor = GinzaPlaceExtractor()
    simple_extractor = SimplePlaceExtractor()
    
    for idx, work in enumerate(works, 1):
        print(f"\n📚 {idx}. {work['author_name']} - {work['title']}")
        print("-" * 50)
        
        # テキスト取得
        text = aozora.download_and_extract_text(work['text_url'])
        
        if not text:
            print("❌ テキスト取得失敗")
            continue
        
        print(f"📄 テキスト長: {len(text):,}文字")
        
        # GiNZA抽出器でテスト（一部のテキストで）
        test_text = text[:15000]  # 最初の15000文字でテスト
        print(f"🧪 テスト用テキスト: {len(test_text):,}文字")
        
        try:
            ginza_places = ginza_extractor.extract_places_from_text(
                work_id=idx, text=test_text
            )
            print(f"🔬 GiNZA抽出: {len(ginza_places)}個")
            
            ginza_names = set(p.place_name for p in ginza_places)
            
        except Exception as e:
            print(f"❌ GiNZAエラー: {e}")
            ginza_places = []
            ginza_names = set()
        
        # 正規表現抽出器でテスト
        try:
            simple_places = simple_extractor.extract_places_from_text(
                work_id=idx, text=test_text
            )
            print(f"📝 正規表現抽出: {len(simple_places)}個")
            
            simple_names = set(p.place_name for p in simple_places)
            
        except Exception as e:
            print(f"❌ 正規表現エラー: {e}")
            simple_places = []
            simple_names = set()
        
        # 結果比較
        print(f"\n📊 抽出結果比較:")
        
        # 共通して抽出された地名
        common_places = ginza_names & simple_names
        if common_places:
            print(f"  🤝 共通抽出: {len(common_places)}個")
            for place in sorted(common_places)[:5]:
                print(f"     • {place}")
            if len(common_places) > 5:
                print(f"     ... 他{len(common_places) - 5}個")
        
        # GiNZAのみ抽出
        ginza_only = ginza_names - simple_names
        if ginza_only:
            print(f"  🔬 GiNZAのみ: {len(ginza_only)}個")
            for place in sorted(ginza_only)[:3]:
                print(f"     • {place}")
            if len(ginza_only) > 3:
                print(f"     ... 他{len(ginza_only) - 3}個")
        
        # 正規表現のみ抽出
        simple_only = simple_names - ginza_names
        if simple_only:
            print(f"  📝 正規表現のみ: {len(simple_only)}個")
            for place in sorted(simple_only)[:3]:
                print(f"     • {place}")
            if len(simple_only) > 3:
                print(f"     ... 他{len(simple_only) - 3}個")
        
        print()
    
    print("🎯 比較テスト完了！")
    print("=" * 60)
    print("📋 抽出器特徴:")
    print("   🔬 GiNZA: 高精度NLP、文脈理解、テキストサイズ制限あり")
    print("   📝 正規表現: 軽量高速、パターンマッチング、制限なし")


if __name__ == "__main__":
    compare_extractors() 