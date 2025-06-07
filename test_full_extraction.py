#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青空文庫テキスト抽出と地名抽出の統合テスト
"""

from bungo_map.extractors.aozora_extractor import AozoraExtractor
from bungo_map.extractors.simple_place_extractor import SimplePlaceExtractor


def test_full_extraction():
    """青空文庫から地名抽出まで一通りのテスト"""
    print("🧪 青空文庫→地名抽出 統合テスト")
    print("=" * 50)
    
    # 抽出器初期化
    aozora = AozoraExtractor()
    place_extractor = SimplePlaceExtractor()
    
    # テスト作品取得
    works = aozora.get_sample_works()
    
    total_places = 0
    
    for idx, work in enumerate(works, 1):
        print(f"\n📚 {idx}. {work['author_name']} - {work['title']}")
        print("-" * 40)
        
        try:
            # テキスト取得
            text = aozora.download_and_extract_text(work['text_url'])
            
            if not text:
                print("❌ テキスト取得失敗")
                continue
            
            # 地名抽出
            places = place_extractor.extract_places_from_text(
                work_id=idx, 
                text=text, 
                aozora_url=work['text_url']
            )
            
            print(f"   📄 テキスト長: {len(text):,}文字")
            print(f"   🏞️ 地名数: {len(places)}個")
            
            # 上位5個の地名を表示
            if places:
                print("   📍 抽出地名:")
                for place in places[:5]:
                    print(f"      {place.place_name} (信頼度: {place.confidence:.2f})")
                
                if len(places) > 5:
                    print(f"      ... 他{len(places) - 5}個")
            
            total_places += len(places)
            
        except Exception as e:
            print(f"❌ エラー: {e}")
    
    print(f"\n🎉 テスト完了！")
    print(f"   総地名数: {total_places}個")
    print(f"   平均: {total_places / len(works):.1f}個/作品")


if __name__ == "__main__":
    test_full_extraction() 