import requests
from datetime import datetime

TOKEN = "8698225504:AAGKuWc12_OMFTG1o9xUmpv5J9ztiz7JbRA"
CHAT = "1041523200"
API = "https://api.dexscreener.com/latest/dex/search"

try:
    params = {'q': 'trending', 'order': 'liquidity', 'limit': 50}
    r = requests.get(API, params=params, timeout=15)
    data = r.json()
    pairs = data.get('pairs', [])
    
    result = []
    for p in pairs:
        if p.get('chainId', '').lower() != 'solana':
            continue
        
        ch = float(p.get('priceChange', {}).get('h1', 0) or 0)
        lq = float(p.get('liquidity', {}).get('usd', 0) or 0)
        
        if (ch <= -7.0 or ch >= 7.0) and lq >= 70000:
            result.append({
                'sym': p.get('baseToken', {}).get('symbol', '?'),
                'pr': float(p.get('priceUsd', 0) or 0),
                'ch': ch,
                'vol': float(p.get('volume', {}).get('h24', 0) or 0),
                'lq': lq,
                'url': p.get('url', '')
            })
    
    if result:
        msg = "<b>🔥 PAIRS SOLANA</b>\n\n"
        for i, x in enumerate(result[:10], 1):
            em = "📈" if x['ch'] >= 0 else "📉"
            msg += f"<b>{i}. {x['sym']}</b>\n"
            msg += f"├ ${x['pr']:.8f}\n"
            msg += f"├ {em} {x['ch']:+.2f}%\n"
            msg += f"└ Liq: ${x['lq']:,.0f}\n\n"
    else:
        msg = "<b>ℹ️ Không có coin</b>\n\n"
    
    msg += f"⏰ {datetime.now().strftime('%H:%M:%S')}"
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT, 'text': msg, 'parse_mode': 'HTML'}
    requests.post(url, json=payload, timeout=10)
    
except Exception as e:
    print(f"Error: {e}")
