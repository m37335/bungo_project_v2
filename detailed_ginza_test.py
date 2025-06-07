#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細なGiNZA NER + 前後文抽出テスト
"""

import spacy

def detailed_ginza_test():
    """詳細なGiNZA解析テスト"""
    print("🔬 詳細GiNZA NER + 前後文抽出テスト")
    print("=" * 60)
    
    # モデル読み込み
    nlp = spacy.load('ja_core_news_sm')
    print("✅ GiNZAモデル読み込み完了")
    
    # テストテキスト（複数文を含む）
    test_text = """
    私は夏休みに鎌倉の海岸で先生と出会った。先生は毎日同じ時刻に海に入り、同じように上がって、
    同じ場所で休んでいた。秋になって東京に戻ると、先生との文通が始まった。先生の家は本郷にあった。
    """
    
    print(f"\n📝 入力テキスト:")
    print(test_text.strip())
    
    # spaCy解析
    doc = nlp(test_text)
    
    print(f"\n📍 抽出された全固有表現:")
    print("-" * 40)
    for ent in doc.ents:
        print(f"  {ent.text:<10} -> {ent.label_:<8} (位置: {ent.start_char:3d}-{ent.end_char:3d})")
    
    print(f"\n🗾 地名のみ抽出 (GPE/LOC):")
    print("-" * 40)
    places = []
    for ent in doc.ents:
        if ent.label_ in ['GPE', 'LOC']:
            places.append(ent)
            print(f"  ✅ {ent.text} ({ent.label_})")
    
    print(f"\n📄 文分割結果:")
    print("-" * 40)
    sentences = []
    for i, sent in enumerate(doc.sents):
        sentences.append(sent.text.strip())
        print(f"  文{i+1}: {sent.text.strip()}")
    
    print(f"\n🔍 前後文抽出シミュレーション:")
    print("-" * 40)
    
    for place in places:
        # 地名が含まれる文を特定
        place_sentence = None
        sentence_index = -1
        
        for i, sent in enumerate(doc.sents):
            if place.start_char >= sent.start_char and place.end_char <= sent.end_char:
                place_sentence = sent.text.strip()
                sentence_index = i
                break
        
        if place_sentence:
            # 前後文を取得
            before_text = sentences[sentence_index-1] if sentence_index > 0 else ""
            after_text = sentences[sentence_index+1] if sentence_index < len(sentences)-1 else ""
            
            print(f"\n  📍 地名: {place.text}")
            print(f"     前文: {before_text[:50]}{'...' if len(before_text) > 50 else ''}")
            print(f"     当文: {place_sentence}")
            print(f"     後文: {after_text[:50]}{'...' if len(after_text) > 50 else ''}")
            
            # 信頼度計算例
            confidence = 0.7
            if place.text in ['東京', '京都', '鎌倉', '本郷']:
                confidence += 0.2
            if any(place.text.endswith(suffix) for suffix in ['市', '県', '区']):
                confidence += 0.15
            
            print(f"     信頼度: {min(confidence, 1.0):.2f}")

if __name__ == "__main__":
    detailed_ginza_test() 