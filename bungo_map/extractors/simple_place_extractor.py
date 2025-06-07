#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
軽量地名抽出器 (正規表現ベース)
GiNZAが利用できない環境でも動作する地名抽出機能
"""

import re
from typing import List, Dict, Optional, Tuple
from bungo_map.core.models import Place


class SimplePlaceExtractor:
    """正規表現ベースの軽量地名抽出器"""
    
    def __init__(self):
        self.place_patterns = self._build_place_patterns()
        print("✅ 軽量地名抽出器 初期化完了")
    
    def _build_place_patterns(self) -> List[Dict]:
        """地名抽出用のパターンを構築"""
        return [
            # 都道府県
            {
                'pattern': r'[北海青森岩手宮城秋田山形福島茨城栃木群馬埼玉千葉東京神奈川新潟富山石川福井山梨長野岐阜静岡愛知三重滋賀京都大阪兵庫奈良和歌山鳥取島根岡山広島山口徳島香川愛媛高知福岡佐賀長崎熊本大分宮崎鹿児島沖縄][都道府県]',
                'category': '都道府県',
                'confidence': 0.9
            },
            # 市区町村
            {
                'pattern': r'[一-龯]{2,8}[市区町村]',
                'category': '市区町村',
                'confidence': 0.8
            },
            # 郡
            {
                'pattern': r'[一-龯]{2,6}[郡]',
                'category': '郡',
                'confidence': 0.7
            },
            # 有名な地名・駅名・観光地
            {
                'pattern': r'(?:' + '|'.join([
                    # 東京エリア
                    '銀座', '新宿', '渋谷', '上野', '浅草', '品川', '池袋', '新橋', '有楽町', '丸の内',
                    '表参道', '原宿', '恵比寿', '六本木', '赤坂', '青山', '麻布', '目黒', '世田谷',
                    '江戸', '本郷', '神田', '日本橋', '築地', '月島', '両国', '浅草橋', '秋葉原',
                    
                    # 関東エリア
                    '横浜', '川崎', '千葉', '埼玉', '大宮', '浦和', '船橋', '柏', '所沢', '川越',
                    '鎌倉', '湘南', '箱根', '熱海', '軽井沢', '日光', '那須', '草津', '伊香保',
                    
                    # 関西エリア
                    '京都', '大阪', '神戸', '奈良', '和歌山', '滋賀', '比叡山', '嵐山', '祇園',
                    '清水', '金閣寺', '銀閣寺', '伏見', '宇治', '平安京', '難波', '梅田', '心斎橋',
                    
                    # 中部エリア
                    '名古屋', '金沢', '富山', '新潟', '長野', '松本', '諏訪', '上高地', '立山',
                    
                    # 東北エリア
                    '仙台', '青森', '盛岡', '秋田', '山形', '福島', '会津', '松島',
                    
                    # 北海道
                    '札幌', '函館', '小樽', '旭川', '釧路', '帯広', '北見',
                    
                    # 中国・四国
                    '広島', '岡山', '山口', '鳥取', '島根', '高松', '松山', '高知', '徳島',
                    
                    # 九州・沖縄
                    '福岡', '博多', '北九州', '佐賀', '長崎', '熊本', '大分', '宮崎', '鹿児島', '沖縄', '那覇',
                    
                    # 古典的・文学的地名
                    '平安京', '江戸', '駿河', '甲斐', '信濃', '越後', '陸奥', '出羽', '薩摩', '土佐',
                    '伊豆', '伊勢', '山城', '大和', '河内', '和泉', '摂津', '近江', '美濃', '尾張',
                    
                    # 海外地名（文学作品によく出る）
                    'パリ', 'ロンドン', 'ベルリン', 'ローマ', 'ウィーン', 'モスクワ', 'ペテルブルク',
                    'ニューヨーク', 'シカゴ', 'サンフランシスコ', 'ロサンゼルス',
                    '上海', '北京', '香港', 'ソウル', 'バンコク', 'マニラ',
                    
                    # 地理的特徴
                    '富士山', '阿蘇山', '霧島', '筑波山', '比叡山', '高野山',
                    '琵琶湖', '中禅寺湖', '芦ノ湖', '十和田湖',
                    '瀬戸内海', '日本海', '太平洋', '東京湾', '大阪湾', '駿河湾',
                    '利根川', '信濃川', '石狩川', '筑後川', '吉野川'
                ]) + r')',
                'category': '有名地名',
                'confidence': 0.85
            }
        ]
    
    def extract_places_from_text(self, work_id: int, text: str, aozora_url: str = None) -> List[Place]:
        """テキストから地名を抽出してPlaceオブジェクトのリストを返す"""
        places = []
        
        # テキストを文に分割
        sentences = self._split_into_sentences(text)
        
        for sentence_idx, sentence in enumerate(sentences):
            # 各パターンで地名を検索
            for pattern_info in self.place_patterns:
                pattern = pattern_info['pattern']
                category = pattern_info['category']
                base_confidence = pattern_info['confidence']
                
                matches = list(re.finditer(pattern, sentence))
                
                for match in matches:
                    place_name = match.group(0)
                    
                    # 前後の文脈を取得
                    before_text = sentences[sentence_idx - 1] if sentence_idx > 0 else ""
                    after_text = sentences[sentence_idx + 1] if sentence_idx < len(sentences) - 1 else ""
                    
                    # 信頼度を調整
                    confidence = self._adjust_confidence(place_name, sentence, base_confidence)
                    
                    place = Place(
                        work_id=work_id,
                        place_name=place_name,
                        before_text=before_text[:500],  # 500文字制限
                        sentence=sentence,
                        after_text=after_text[:500],   # 500文字制限
                        aozora_url=aozora_url,
                        confidence=confidence,
                        extraction_method=f"regex_{category}"
                    )
                    places.append(place)
        
        return self._deduplicate_places(places)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """テキストを文に分割"""
        # 句読点で分割
        sentences = re.split(r'[。！？]', text)
        
        # 空文字列を除去し、前後の空白をトリム
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _adjust_confidence(self, place_name: str, sentence: str, base_confidence: float) -> float:
        """文脈に基づいて信頼度を調整"""
        confidence = base_confidence
        
        # 地名らしい文脈かチェック
        location_contexts = [
            r'[から|より|への|へと|にて|にいる|にある|を通り|を経て]',
            r'[行く|来る|向かう|着く|発つ|出発|到着]',
            r'[住む|滞在|訪問|旅行|見物]'
        ]
        
        for context_pattern in location_contexts:
            if re.search(context_pattern, sentence):
                confidence += 0.1
                break
        
        # 人名と混同しやすい場合は信頼度を下げる
        person_contexts = [
            r'[さん|君|氏|先生|様]',
            r'[は|が][話す|言う|思う|考える]'
        ]
        
        for person_pattern in person_contexts:
            if re.search(person_pattern, sentence):
                confidence -= 0.2
                break
        
        # 長さによる調整（短すぎる地名は信頼度を下げる）
        if len(place_name) == 1:
            confidence -= 0.3
        elif len(place_name) == 2:
            confidence -= 0.1
        
        return max(0.1, min(confidence, 1.0))
    
    def _deduplicate_places(self, places: List[Place]) -> List[Place]:
        """重複する地名を除去（同じ作品内の同じ地名）"""
        seen = set()
        unique_places = []
        
        for place in places:
            # 作品ID + 地名 で重複チェック
            key = (place.work_id, place.place_name)
            if key not in seen:
                seen.add(key)
                unique_places.append(place)
        
        return unique_places
    
    def extract_places_with_context(self, text: str, work_id: int, aozora_url: str) -> List[Place]:
        """既存のGiNZA抽出器と互換性のあるインターフェース"""
        return self.extract_places_from_text(work_id, text, aozora_url)
    
    def test_extraction(self, test_text: str = None) -> Dict:
        """抽出機能のテスト"""
        if not test_text:
            test_text = """
            親譲りの無鉄砲で小供の時から損ばかりしている。東京の学校を卒業してから、
            四国の松山に赴任した。瀬戸内海の風景は美しく、道後温泉も有名である。
            京都の金閣寺や奈良の東大寺も見てみたい。鎌倉の大仏も素晴らしいらしい。
            """
        
        places = self.extract_places_from_text(work_id=999, text=test_text)
        
        result = {
            'test_text': test_text[:100] + "..." if len(test_text) > 100 else test_text,
            'places_found': len(places),
            'places': [
                {
                    'name': place.place_name,
                    'confidence': place.confidence,
                    'method': place.extraction_method,
                    'sentence': place.sentence[:50] + "..." if len(place.sentence) > 50 else place.sentence
                }
                for place in places
            ],
            'success': len(places) > 0
        }
        
        return result 