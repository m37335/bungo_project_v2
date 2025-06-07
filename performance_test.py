#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能テスト実行スクリプト
仕様書要件: 検索機能は0.5秒以内
"""

import time
import sys
from bungo_map.core.database import BungoDatabase

def main():
    """性能テスト実行"""
    try:
        db = BungoDatabase('data/bungo_production.db')
        
        test_cases = [
            ('search_authors', '夏目'),
            ('search_works', '坊っちゃん'),
            ('search_places', '松山')
        ]
        
        all_passed = True
        
        print("⚡ 性能テスト実行中...")
        
        for method_name, query in test_cases:
            start_time = time.time()
            method = getattr(db, method_name)
            result = method(query)
            execution_time = time.time() - start_time
            
            if execution_time >= 0.5:
                print(f'❌ {method_name}: {execution_time:.3f}s >= 0.5s')
                all_passed = False
            else:
                print(f'✅ {method_name}: {execution_time:.3f}s')
        
        if all_passed:
            print("🎉 全ての性能テストに合格しました！")
            sys.exit(0)
        else:
            print("💥 性能要件を満たさないテストがあります")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 性能テスト実行エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 