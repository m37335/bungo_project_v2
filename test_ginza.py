#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GiNZA地名抽出テスト
"""

import spacy

def test_ginza():
    """GiNZAによる地名抽出テスト"""
    print("🔧 GiNZAセットアップテスト開始...")
    
    # モデル読み込み
    nlp = spacy.load('ja_core_news_sm')
    print("✅ ja_core_news_sm モデル読み込み成功")
    
    # テストテキスト
    test_texts = [
        "私は夏休みに鎌倉の海岸で先生と出会った。",
        "汽車が松山市に着いた時には、もう日が暮れていた。",
        "一人の下人が京都の羅生門の下で雨やみを待っていた。",
        "やがて東京の学校に入学することになった。",
        "メロスはシラクスの市に出て来て、王の不信を確信した。"
    ]
    
    print("\n🔍 地名抽出テスト結果:")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. テキスト: {text}")
        doc = nlp(text)
        
        # 固有表現を抽出
        places_found = []
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC']:  # 地政学的実体、場所
                places_found.append(f"{ent.text} ({ent.label_})")
        
        if places_found:
            print(f"   📍 抽出された地名: {', '.join(places_found)}")
        else:
            print("   ⚠️ 地名が抽出されませんでした")
        
        # 全固有表現表示
        all_entities = [f"{ent.text}({ent.label_})" for ent in doc.ents]
        if all_entities:
            print(f"   🔍 全固有表現: {', '.join(all_entities)}")
    
    print("\n" + "=" * 50)
    print("✅ GiNZAテスト完了！")

if __name__ == "__main__":
    test_ginza() 