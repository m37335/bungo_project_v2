#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
個別地名検出テスト
"""

import spacy

def test_individual_places():
    """個別地名の検出テスト"""
    print("🔬 個別地名検出テスト")
    print("=" * 40)
    
    nlp = spacy.load('ja_core_news_sm')
    
    test_cases = [
        "私は夏休みに鎌倉の海岸で先生と出会った。",
        "先生の家は本郷にあった。",
        "汽車が松山市に着いた。",
        "京都の羅生門の下で雨やみを待っていた。",
        "東京に戻ると、先生との文通が始まった。",
        "シラクスの市に出て来て、王の不信を確信した。"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. テスト: {text}")
        doc = nlp(text)
        
        # 全固有表現
        all_entities = [(ent.text, ent.label_) for ent in doc.ents]
        print(f"   全固有表現: {all_entities}")
        
        # 地名のみ
        places = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in ['GPE', 'LOC']]
        if places:
            print(f"   ✅ 地名: {places}")
        else:
            print("   ❌ 地名検出なし")
        
        # トークン分析
        tokens = [(token.text, token.pos_, token.tag_) for token in doc]
        print(f"   トークン: {tokens}")

if __name__ == "__main__":
    test_individual_places() 