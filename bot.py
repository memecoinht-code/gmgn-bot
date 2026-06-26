import requests
from datetime import datetime

TELEGRAM_TOKEN = "8698225504:AAGKuWc12_OMFTG1o9xUmpv5J9ztiz7JbRA"
TELEGRAM_CHAT_ID = "1041523200"

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/search"

MIN_PRICE_CHANGE = -7.0
MAX_PRICE_CHANGE = 7.0
MIN_LIQUIDITY = 70000

def get_qualified_pairs():
    try:
        print("📡 Kết nối DEXScreener API...")
        params = {'q': 'trending', 'order': 'liquidity', 'limit': 50}
        response = requests.get(DEXSCREENER_API, params=params, timeout=15)
        data = response.json()
        
        pairs = []
        if 'pairs' in data:
            for pair in data['pairs']:
                if pair.get('chainId', '').lower() != 'solana':
                    continue
                
                price_change_h1 = float(pair.get('priceChange', {}).get('h1', 0) or 0)
                
                # Lọc: ±7%
                if price_change_h1 > MIN_PRICE_CHANGE and price_change_h1 < MAX_PRICE_CHANGE:
                    continue
                
                liquidity = float(pair.get('liquidity', {}).get('usd', 0) or 0)
                if liquidity < MIN_LIQUIDITY:
                    continue
                
                pairs.append({
                    'symbol': pair.get('baseToken', {}).get('symbol', '?'),
                    'name': pair.get('baseToken', {}).get('name', '?'),
                    'price': float(pair.get('priceUsd', 0) or 0),
                    'price_change_h1': price_change_h1,
                    'price_change_h6': float(pair.get('priceChange', {}).get('h6', 0) or 0),
                    'price_change_h24': float(pair.get('priceChange', {}).get('h24', 0) or 0),
                    'volume_h24': float(pair.get('volume', {}).get('h24', 0) or 0),
                    'liquidity': liquidity,
                    'url': pair.get('url', ''),
                })
        
        print(f"✅ Lấy được {len(pairs)} pairs phù hợp")
        return pairs
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return []

def create_message(pairs):
    if not pairs:
        return f"<b>ℹ️ Không có pair động lực</b>\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    
    message = f"<b>🔥 PAIRS SOLANA (±7%, Liq 70k+)</b>\n\n"
    
    for idx, pair in enumerate(pairs[:10], 1):
        symbol = pair.get('symbol', '?')
        name = pair.get('name', '?')
        price = pair.get('price', 0)
        change_h1 = pair.get('price_change_h1', 0)
        change_h6 = pair.get('price_change_h6', 0)
        change_h24 = pair.get('price_change_h24', 0)
        volume = pair.get('volume_h24', 0)
        liquidity = pair.get('liquidity', 0)
        
        emoji = "📈" if change_h1 >= 0 else "📉"
        url = pair.get('url', '')
        dex_link = f"<a href='{url}'>🔗DEX</a>" if url else ""
        
        if price < 0.01:
            price_str = f"{price:.8f}"
        else:
            price_str = f"{price:.4f}"
        
        message += f"<b>{idx}. {symbol}</b> - {name}\n"
        message += f"├ ${price_str}\n"
        message += f"├ {emoji} 1h: {change_h1:+.2f}% | 6h: {change_h6:+.2f}% | 24h: {change_h24:+.2f}%\n"
        message += f"├ Vol: ${volume:,.0f} | Liq: ${liquidity:,.0f}\n"
        message += f"└ {dex_link}\n\n"
    
    message += f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    return message

def send_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    pairs = get_qualified_pairs()
    message = create_message(pairs)
    send_message(message)
