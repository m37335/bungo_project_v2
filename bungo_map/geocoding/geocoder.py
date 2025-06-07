#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ジオコーディング機能
地名を緯度・経度座標に変換
"""

import time
import logging
from typing import Optional, Tuple, List, Dict, Any
from geopy.geocoders import Nominatim, GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import googlemaps
from dataclasses import dataclass


@dataclass
class GeocodingResult:
    """ジオコーディング結果"""
    place_name: str
    lat: Optional[float]
    lng: Optional[float]
    formatted_address: Optional[str] = None
    confidence: float = 0.0
    source: str = "unknown"
    error: Optional[str] = None


class Geocoder:
    """地名ジオコーディングクラス"""
    
    def __init__(self, google_api_key: Optional[str] = None, user_agent: str = "bungo-map/2.0"):
        """
        初期化
        
        Args:
            google_api_key: Google Maps API キー
            user_agent: User-Agent文字列
        """
        self.logger = logging.getLogger(__name__)
        self.user_agent = user_agent
        
        # Nominatim (OpenStreetMap) - 無料
        self.nominatim = Nominatim(user_agent=user_agent)
        
        # Google Maps API - 有料だが高精度
        self.google_client = None
        self.google_geocoder = None
        if google_api_key:
            try:
                self.google_client = googlemaps.Client(key=google_api_key)
                self.google_geocoder = GoogleV3(api_key=google_api_key)
                self.logger.info("Google Maps API クライアント初期化完了")
            except Exception as e:
                self.logger.warning(f"Google Maps API 初期化失敗: {e}")
        
        # キャッシュ（メモリ内）
        self.cache: Dict[str, GeocodingResult] = {}
        
        # 日本の地名補正辞書
        self.japan_locations = {
            "東京": "東京都",
            "大阪": "大阪府",
            "京都": "京都府",
            "愛知": "愛知県",
            "松山": "松山市, 愛媛県",
            "道後温泉": "道後温泉, 松山市, 愛媛県",
            "瀬戸内海": "瀬戸内海, 日本",
            "本州": "本州, 日本",
            "青森": "青森県",
            "津軽": "津軽地方, 青森県",
            "鎌倉": "鎌倉市, 神奈川県",
            "神奈川": "神奈川県",
            "文京区": "文京区, 東京都",
            "本郷": "本郷, 文京区, 東京都",
            "上野": "上野, 台東区, 東京都",
            "浅草": "浅草, 台東区, 東京都",
            "シラクス": "Syracuse, Sicily, Italy",
            "シチリア島": "Sicily, Italy"
        }
    
    def normalize_place_name(self, place_name: str) -> str:
        """地名の正規化"""
        # 余分な空白を削除
        normalized = place_name.strip()
        
        # 日本の地名補正
        if normalized in self.japan_locations:
            normalized = self.japan_locations[normalized]
        
        return normalized
    
    def geocode_with_nominatim(self, place_name: str) -> GeocodingResult:
        """Nominatimでジオコーディング"""
        try:
            location = self.nominatim.geocode(place_name, language='ja', timeout=5)
            
            if location:
                return GeocodingResult(
                    place_name=place_name,
                    lat=location.latitude,
                    lng=location.longitude,
                    formatted_address=location.address,
                    confidence=0.7,  # Nominatimの信頼度は固定
                    source="nominatim"
                )
            else:
                return GeocodingResult(
                    place_name=place_name,
                    lat=None,
                    lng=None,
                    error="場所が見つかりません",
                    source="nominatim"
                )
                
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            self.logger.warning(f"Nominatim エラー ({place_name}): {e}")
            return GeocodingResult(
                place_name=place_name,
                lat=None,
                lng=None,
                error=str(e),
                source="nominatim"
            )
    
    def geocode_with_google(self, place_name: str) -> GeocodingResult:
        """Google Maps APIでジオコーディング"""
        if not self.google_client:
            return GeocodingResult(
                place_name=place_name,
                lat=None,
                lng=None,
                error="Google Maps API が利用できません",
                source="google"
            )
        
        try:
            results = self.google_client.geocode(place_name, language='ja')
            
            if results:
                result = results[0]  # 最初の結果を使用
                location = result['geometry']['location']
                
                # 信頼度を計算（location_typeに基づく）
                location_type = result['geometry'].get('location_type', 'APPROXIMATE')
                confidence_map = {
                    'ROOFTOP': 1.0,
                    'RANGE_INTERPOLATED': 0.9,
                    'GEOMETRIC_CENTER': 0.8,
                    'APPROXIMATE': 0.6
                }
                confidence = confidence_map.get(location_type, 0.5)
                
                return GeocodingResult(
                    place_name=place_name,
                    lat=location['lat'],
                    lng=location['lng'],
                    formatted_address=result['formatted_address'],
                    confidence=confidence,
                    source="google"
                )
            else:
                return GeocodingResult(
                    place_name=place_name,
                    lat=None,
                    lng=None,
                    error="場所が見つかりません",
                    source="google"
                )
                
        except Exception as e:
            self.logger.warning(f"Google Maps API エラー ({place_name}): {e}")
            return GeocodingResult(
                place_name=place_name,
                lat=None,
                lng=None,
                error=str(e),
                source="google"
            )
    
    def geocode(self, place_name: str, use_cache: bool = True) -> GeocodingResult:
        """
        地名をジオコーディング
        
        Args:
            place_name: 地名
            use_cache: キャッシュを使用するか
            
        Returns:
            GeocodingResult: ジオコーディング結果
        """
        # キャッシュをチェック
        if use_cache and place_name in self.cache:
            self.logger.debug(f"キャッシュヒット: {place_name}")
            return self.cache[place_name]
        
        # 地名を正規化
        normalized_name = self.normalize_place_name(place_name)
        
        self.logger.info(f"ジオコーディング実行: {place_name} → {normalized_name}")
        
        # まずGoogle Maps APIを試す（利用可能な場合）
        if self.google_client:
            result = self.geocode_with_google(normalized_name)
            if result.lat is not None:
                self.cache[place_name] = result
                time.sleep(0.1)  # レート制限対策
                return result
        
        # Nominatimを試す
        result = self.geocode_with_nominatim(normalized_name)
        if result.lat is not None:
            self.cache[place_name] = result
            time.sleep(1.0)  # Nominatimのレート制限対策
            return result
        
        # どちらも失敗した場合
        result = GeocodingResult(
            place_name=place_name,
            lat=None,
            lng=None,
            error="全てのジオコーダーで失敗",
            source="none"
        )
        self.cache[place_name] = result
        return result
    
    def batch_geocode(self, place_names: List[str], max_retry: int = 2) -> List[GeocodingResult]:
        """
        複数地名の一括ジオコーディング
        
        Args:
            place_names: 地名リスト
            max_retry: 最大リトライ回数
            
        Returns:
            List[GeocodingResult]: ジオコーディング結果リスト
        """
        results = []
        total = len(place_names)
        
        self.logger.info(f"一括ジオコーディング開始: {total}件")
        
        for i, place_name in enumerate(place_names, 1):
            self.logger.info(f"進行状況: {i}/{total} - {place_name}")
            
            retry_count = 0
            while retry_count <= max_retry:
                result = self.geocode(place_name)
                
                # 成功した場合
                if result.lat is not None:
                    results.append(result)
                    break
                
                # 失敗した場合
                retry_count += 1
                if retry_count <= max_retry:
                    self.logger.warning(f"リトライ {retry_count}/{max_retry}: {place_name}")
                    time.sleep(2.0)  # リトライ前に待機
                else:
                    self.logger.error(f"ジオコーディング失敗: {place_name}")
                    results.append(result)
        
        success_count = sum(1 for r in results if r.lat is not None)
        self.logger.info(f"一括ジオコーディング完了: {success_count}/{total} 成功")
        
        return results
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """キャッシュ統計情報"""
        total = len(self.cache)
        success = sum(1 for r in self.cache.values() if r.lat is not None)
        
        return {
            "total_cached": total,
            "successful": success,
            "failed": total - success,
            "success_rate": success / total if total > 0 else 0.0
        } 