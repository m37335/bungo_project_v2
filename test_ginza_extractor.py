#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GiNZA地名抽出器テスト
"""

from bungo_map.extractors.ginza_place_extractor import GinzaPlaceExtractor


def test_ginza_extractor():
    """GiNZA地名抽出器のテスト"""
    print("🧪 GiNZA地名抽出器テスト開始...")
    
    # 抽出器初期化
    extractor = GinzaPlaceExtractor()
    
    # テスト用の文学テキスト（より長文）
    test_texts = [
        """
        私は夏休みに鎌倉の海岸で先生と出会った。先生は毎日同じ時刻に海に入り、
        同じように上がって、同じ場所で休んでいた。私はその先生の習慣を観察していた。
        秋になって東京に戻ると、先生との文通が始まった。
        """,
        
        """
        汽車が松山市に着いた時には、もう日が暮れていた。プラットホームには赤シャツが
        迎えに来ていて、おれを宿屋まで案内してくれた。翌日、道後温泉に連れて行かれた。
        湯は思ったより熱く、瀬戸内海を望む風景は美しかった。
        """,
        
        """
        ある日の暮方の事である。一人の下人が京都の羅生門の下で雨やみを待っていた。
        羅生門から朱雀大路を見下ろすと人影はない。ただ、ところどころに夕日が
        照っているだけである。下人は二、三度舌打ちをして、大きな円柱の下に
        身を寄せた。
        """,
        
        """
        メロスは激怒した。必ず、かの邪智暴虐の王を除かなければならぬと決意した。
        メロスには政治がわからぬ。メロスは、村の牧人である。きょう未明シラクスの市に
        出て来て、王の不信を確信した。メロスは単純な男であった。
        """
    ]
    
    print("=" * 70)
    
    # 各テキストから地名を抽出
    for i, text in enumerate(test_texts, 1):
        print(f"\n📖 テストテキスト {i}:")
        print(f"   {text.strip()[:80]}...")
        
        # 地名抽出実行
        places = extractor.extract_places_from_text(work_id=i, text=text.strip())
        
        print(f"\n   📍 抽出された地名 ({len(places)}箇所):")
        for place in places:
            print(f"     • {place.place_name} (信頼度: {place.confidence:.2f})")
            print(f"       文脈: {place.sentence[:60]}...")
            if place.before_text:
                print(f"       前文: {place.before_text[:40]}...")
            if place.after_text:
                print(f"       後文: {place.after_text[:40]}...")
            print()
    
    print("=" * 70)
    
    # 統計情報
    total_places = sum(len(extractor.extract_places_from_text(i, text.strip())) 
                      for i, text in enumerate(test_texts, 1))
    
    print(f"\n📊 テスト結果統計:")
    print(f"   - テストテキスト数: {len(test_texts)}")
    print(f"   - 抽出された地名総数: {total_places}")
    print(f"   - 平均地名数/テキスト: {total_places/len(test_texts):.1f}")
    
    print("\n✅ GiNZA地名抽出器テスト完了！")


if __name__ == "__main__":
    test_ginza_extractor() 