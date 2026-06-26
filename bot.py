import requests
from datetime import datetime

TELEGRAM_TOKEN = "8698225504:AAGKuWc12_OMFTG1o9xUmpv5J9ztiz7JbRA"
TELEGRAM_CHAT_ID = "1041523200"

def get_pairs():
    try:
        url = "https://api.dexscreener.com/latest/dex/search"
        params = {'q': 'trending', 'order': 'liquidity', 'limit': 50}
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        pairs = data.get('pairs', [])
        
        # Lọc Solana + tiêu chí
        result = []
        for pair in pairs:
            chain = pair.get('chainId', '').lower()
            if chain != 'solana':
                continue
            
            change = float(pair.get('priceChange', {}).get('h1', 0) or 0)
            liq = float(pair.get('liquidity', {}).get('usd', 0) or 0)
            
            # Tiêu chí: ±7% + liquidity 70k
            if (change <= -7.0 or change >= 7.0) and liq >= 70000:
                result.append({
                    'symbol': pair.get('baseToken', {}).get('symbol', '?'),
                    'price': float(pair.get('priceUsd', 0) or 0),
                    'change_h1': change,
                    'change_h6': float(pair.get('priceChange', {}).get('h6', 0) or 0),
                    'change_h24': float(pair.get('priceChange', {}).get('h24', 0) or 0),
                    'volume': float(pair.get('volume', {}).get('h24', 0) or 0),
                    'liquidity': liq,
                    'url': pair.get('url', ''),
                })
        
        return result
    except Exception as e:
        print(f"Error: {e}")
        return []

def send_telegram(pairs):
    try:
        if not pairs:
            msg = "<b>ℹ️ Không có pair động lực</b>"
        else:
            msg = "<b>🔥 PAIRS SOLANA (±7%, Liq 70k+)</b>\n\n"
            for i, p in enumerate(pairs[:10], 1):
                emoji = "📈" if p['change_h1'] >= 0 else "📉"
                msg += f"<b>{i}. {p['symbol']}</b>\n"
                msg += f"├ ${p['price']:.8f}\n"
                msg += f"├ {emoji} 1h: {p['change_h1']:+.2f}%\n"
                msg += f"├ Vol: ${p['volume']:,.0f}\n"
                msg += f"└ Liq: ${p['liquidity']:,.0f}\n\n"
        
        msg += f"⏰ {datetime.now().strftime('%H:%M:%S')}"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}
        requests.post(url, data=data,
