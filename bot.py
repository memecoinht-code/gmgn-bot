import requests
from datetime import datetime

TELEGRAM_TOKEN = "8698225504:AAGKuWc12_OMFTG1o9xUmpv5J9ztiz7JbRA"
TELEGRAM_CHAT_ID = "1041523200"

PHOTON_API = "https://api.photon-sol.tinyastro.io/trending"

MIN_PRICE_CHANGE = -7.0
MAX_PRICE_CHANGE = 7.0
MIN_LIQUIDITY = 70000

def get_qualified_tokens():
    try:
        print("📡 Kết nối Photon API...")
        response = requests.get(PHOTON_API, timeout=15)
        data = response.json()
        
        tokens = data.get('tokens', []) if isinstance(data, dict) else data
        
        print(f"✅ Lấy được {len(tokens)} tokens")
        
        qualified_tokens = []
        
        for token in tokens:
            # Lấy thông tin
            price = float(token.get('price', 0) or 0)
            price_change = float(token.get('priceChange', {}).get('h1', 0) or 0) if isinstance(token.get('priceChange'), dict) else 0
            liquidity = float(token.get('liquidity', 0) or 0)
            volume = float(token.get('volume', {}).get('h24', 0) or 0) if isinstance(token.get('volume'), dict) else 0
            
            # Lọc: ±7%
            if price_change > MIN_PRICE_CHANGE and price_change < MAX_PRICE_CHANGE:
                continue
            
            # Lọc: liquidity 70k+
            if liquidity < MIN_LIQUIDITY:
                continue
            
            qualified_tokens.append({
                'symbol': token.get('symbol', 'N/A'),
                'name': token.get('name', 'N/A'),
                'price': price,
                'price_change_h1': price_change,
                'price_change_h6': float(token.get('priceChange', {}).get('h6', 0) or 0) if isinstance(token.get('priceChange'), dict) else 0,
                'price_change_h24': float(token.get('priceChange', {}).get('h24', 0) or 0) if isinstance(token.get('priceChange'), dict) else 0,
                'volume': volume,
                'liquidity': liquidity,
                'url': token.get('url', ''),
                'mint': token.get('mint', ''),
            })
        
        print(f"✅ Lọc được {len(qualified_tokens)} tokens")
        return qualified_tokens
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return []

def create_message(tokens):
    if not tokens:
        return f"<b>ℹ️ Không có token động lực</b>\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    
    message = f"<b>🔥 TOKENS SOLANA (Photon - ±7%, Liq 70k+)</b>\n\n"
    
    for idx, token in enumerate(tokens[:10], 1):
        symbol = token.get('symbol', '?')
        name = token.get('name', '?')
        price = token.get('price', 0)
        change_h1 = token.get('price_change_h1', 0)
        change_h6 = token.get('price_change_h6', 0)
        change_h24 = token.get('price_change_h24', 0)
        volume = token.get('volume', 0)
        liquidity = token.get('liquidity', 0)
        mint = token.get('mint', '')
        
        emoji = "📈" if change_h1 >= 0 else "📉"
        
        if price < 0.01:
            price_str = f"{price:.8f}"
        else:
            price_str = f"{price:.4f}"
        
        message += f"<b>{idx}. {symbol}</b> - {name}\n"
        message += f"├ Giá: <code>${price_str}</code>\n"
        message += f"├ {emoji} 1h: <code>{change_h1:+.2f}%</code> | 6h: <code>{change_h6:+.2f}%</code> | 24h: <code>{change_h24:+.2f}%</code>\n"
        message += f"├ Vol: <code>${volume:,.0f}</code> | Liq: <code>${liquidity:,.0f}</code>\n"
        
        if mint:
            message += f"├ Mint: <code>{mint[:20]}...</code>\n"
        
        message += f"└ <a href='https://photon-sol.tinyastro.io/token/{mint}'>🔗Photon</a>\n\n" if mint else f"└ Link\n\n"
    
    message += f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    return message

def send_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Lỗi gửi: {e}")
        return False

if __name__ == "__main__":
    tokens = get_qualified_tokens()
    message = create_message(tokens)
    send_message(message)
