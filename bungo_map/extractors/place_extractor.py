#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地名抽出器（サンプルデータ版）
"""

from typing import List, Dict
from bungo_map.core.models import Place


class PlaceExtractor:
    """文学作品から地名を抽出"""
    
    def __init__(self):
        # 作品別の有名な地名データ（サンプル）
        self.sample_places = {
            "坊っちゃん": [
                {
                    "place_name": "松山市",
                    "before_text": "汽車が",
                    "sentence": "汽車が松山市に着いた時には、もう日が暮れていた",
                    "after_text": "。プラットホームには",
                    "confidence": 0.9
                },
                {
                    "place_name": "道後温泉",
                    "before_text": "赤シャツと一緒に",
                    "sentence": "赤シャツと一緒に道後温泉へ行った",
                    "after_text": "。湯は思ったより",
                    "confidence": 0.85
                },
                {
                    "place_name": "瀬戸内海",
                    "before_text": "向こうに見える",
                    "sentence": "向こうに見える瀬戸内海の島々は美しかった",
                    "after_text": "。しかし、おれは",
                    "confidence": 0.8
                }
            ],
            "吾輩は猫である": [
                {
                    "place_name": "東京",
                    "before_text": "この家は",
                    "sentence": "この家は東京の片隅にある小さな家である",
                    "after_text": "。主人は学校の",
                    "confidence": 0.9
                },
                {
                    "place_name": "本郷",
                    "before_text": "主人は毎日",
                    "sentence": "主人は毎日本郷の学校へ通っている",
                    "after_text": "。帰りはいつも",
                    "confidence": 0.85
                }
            ],
            "こころ": [
                {
                    "place_name": "鎌倉",
                    "before_text": "私は夏休みに",
                    "sentence": "私は夏休みに鎌倉の海岸で先生と出会った",
                    "after_text": "。先生は毎日",
                    "confidence": 0.9
                },
                {
                    "place_name": "東京",
                    "before_text": "秋になって",
                    "sentence": "秋になって東京に戻ると、先生との交流が始まった",
                    "after_text": "。先生の家は",
                    "confidence": 0.85
                }
            ],
            "羅生門": [
                {
                    "place_name": "京都",
                    "before_text": "ある日の暮方の事である。一人の下人が",
                    "sentence": "一人の下人が京都の羅生門の下で雨やみを待っていた",
                    "after_text": "。羅生門の上には",
                    "confidence": 0.95
                },
                {
                    "place_name": "朱雀大路",
                    "before_text": "羅生門から",
                    "sentence": "羅生門から朱雀大路を見下ろすと人影はない",
                    "after_text": "。ただ、ところどころに",
                    "confidence": 0.8
                }
            ],
            "人間失格": [
                {
                    "place_name": "津軽",
                    "before_text": "私の生まれた",
                    "sentence": "私の生まれた津軽の大きな家の思い出",
                    "after_text": "。父は地主で",
                    "confidence": 0.9
                },
                {
                    "place_name": "東京",
                    "before_text": "やがて",
                    "sentence": "やがて東京の学校に入学することになった",
                    "after_text": "。しかし、そこでも",
                    "confidence": 0.85
                }
            ],
            "走れメロス": [
                {
                    "place_name": "シラクス",
                    "before_text": "メロスは激怒した。必ず、かの邪智暴虐の王を除かなければならぬと決意した。メロスには政治がわからぬ。メロスは、村の牧人である。笛を吹き、羊と遊んで暮して来た。けれども邪悪に対しては、人一倍に敏感であった。きょう未明",
                    "sentence": "きょう未明シラクスの市に出て来て、王の不信を確信した",
                    "after_text": "。なぜなら、",
                    "confidence": 0.95
                }
            ]
        }
    
    def extract_places(self, work_id: int, work_title: str, aozora_url: str = None) -> List[Place]:
        """作品から地名を抽出してPlaceオブジェクトのリストを返す"""
        places_data = self.sample_places.get(work_title, [])
        
        places = []
        for place_data in places_data:
            place = Place(
                work_id=work_id,
                place_name=place_data['place_name'],
                before_text=place_data['before_text'],
                sentence=place_data['sentence'],
                after_text=place_data['after_text'],
                aozora_url=aozora_url,
                confidence=place_data['confidence'],
                extraction_method="sample_data"
            )
            places.append(place)
        
        return places
    
    def get_available_works(self) -> List[str]:
        """地名データが利用可能な作品リストを返す"""
        return list(self.sample_places.keys()) 