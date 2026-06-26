import requests
from datetime import datetime

TELEGRAM_TOKEN = "8698225504:AAGKuWc12_OMFTG1o9xUmpv5J9ztiz7JbRA"
TELEGRAM_CHAT_ID = "1041523200"

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/search"

def debug_dexscreener():
    try:
        print("📡 Kết nối DEXScreener...")
        params = {'q': 'trending', 'order': 'liquidity', 'limit': 50}
        response = requests.get(DEXSCREENER_API, params=params, timeout=15)
        data = response.json()
        
        print(f"✅ Kết nối thành công!")
        
        pairs = data.get('pairs', [])
        print(f"✅ Tổng pairs: {len(pairs)}\n")
        
        # Lọc Solana
        solana_pairs = [p for p in pairs if p.get('chainId', '').lower() == 'solana']
        print(f"✅ Solana pairs: {len(solana_pairs)}\n")
        
        # In 10 pairs đầu (chi tiết)
        print("🔍 TOP 10 SOLANA PAIRS:")
        print("-" * 100)
        
        for idx, pair in enumerate(solana_pairs[:10], 1):
            symbol = pair.get('baseToken', {}).get('symbol', 'N/A')
            price = pair.get('priceUsd', 'N/A')
            change_h1 = pair.get('priceChange', {}).get('h1', 'N/A')
            liquidity = pair.get('liquidity', {}).get('usd', 'N/A')
            
            print(f"\n{idx}. {symbol}")
            print(f"   Giá: {price}")
            print(f"   % 1h: {change_h1}")
            print(f"   Liquidity: {liquidity}")
        
        # Đếm coins đạt tiêu chí
        print("\n\n📊 THỐNG KÊ TIÊU CHÍ:")
        print("-" * 100)
        
        count_change = 0
        count_liq = 0
        count_all = 0
        
        for pair in solana_pairs:
            price_change_h1 = float(pair.get('priceChange', {}).get('h1', 0) or 0)
            liquidity = float(pair.get('liquidity',
