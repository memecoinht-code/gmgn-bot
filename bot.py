import requests
import time
from datetime import datetime

TELEGRAM_TOKEN = "8698225504:AAGKuWc12_OMFTG1o9xUmpv5J9ztiz7JbRA"
TELEGRAM_CHAT_ID = "1041523200"

GMGN_API = "https://api.gmgn.ai/trending"
CHAIN = "sol"

MIN_PRICE_CHANGE_1M = -7.0
MAX_PRICE_CHANGE_1M = 7.0
MIN_AGE_DAYS = 3
MIN_LIQUIDITY_USD = 70000

def get_qualified_coins():
    try:
        params = {"chain": CHAIN, "limit": 200}
        response = requests.get(GMGN_API, params=params, timeout=15)
        data = response.json()
        tokens = data.get("data", [])
        
        qualified_tokens = []
        
        for token in tokens:
            price_change_1m = token.get('price_change_1m')
            if price_change_1m is None:
                price_change_1m = token.get('price_change_5m', 0)
            
            if (price_change_1m >= MIN_PRICE_CHANGE_1M and price_change_1m <= MAX_PRICE_CHANGE_1M) and price_change_1m != 0:
                continue
            
            created_at = token.get('created_at')
            if created_at:
                try:
                    created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    age_days = (datetime.now(created_time.tzinfo) - created_time).days
                    if age_days < MIN_AGE_DAYS:
                        continue
                except:
                    continue
            else:
                continue
            
            liquidity = token.get('liquidity', 0)
            if liquidity < MIN_LIQUIDITY_USD:
                continue
            
            socials = token.get('socials', {})
            twitter = socials.get('twitter') if isinstance(socials, dict) else None
            if not twitter:
                continue
            
            is_mintable = token.get('is_mintable', False)
            if is_mintable:
                continue
            
            is_blacklisted = token.get('is_blacklisted', False)
            if is_blacklisted:
                continue
            
            lp_burned = token.get('lp_burned', False)
            if not lp_burned:
                continue
            
            freeze_authority = token.get('freeze_authority', None)
            if freeze_authority:
                continue
            
            qualified_tokens.append(token)
        
        qualified_tokens.sort(key=lambda x: x.get('price_change_1m', x.get('price_change_5m', 0)))
        return qualified_tokens
        
    except Exception as e:
        print(f"Lỗi: {e}")
        return []

def create_message(tokens):
    if not tokens:
        return f"<b>ℹ️ Không có coin GMGN</b>\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    
    message = f"<b>✅ COINS GMGN (±7%, Liq 70k+)</b>\n\n"
    
    for idx, token in enumerate(tokens[:10], 1):
        symbol = token.get('symbol', 'N/A')
        price = token.get('price', 0)
        
        price_change_1m = token.get('price_change_1m')
        if price_change_1m is None:
            price_change_1m = token.get('price_change_5m', 0)
        
        price_change_5m = token.get('price_change_5m', 0)
        price_change_1h = token.get('price_change_1h', 0)
        volume = token.get('volume_24h', 0)
        liquidity = token.get('liquidity', 0)
        address = token.get('address', '')
        
        emoji = "📈" if price_change_1m >= 0 else "📉"
        gmgn_link = f"https://gmgn.ai/sol/token/{address}" if address else "#"
        
        message += f"<b>{idx}. {symbol}</b>\n"
        message += f"├ ${price:.8f}\n"
        message += f"├ {emoji} {price_change_1m:+.2f}% (1m) | {price_change_5m:+.2f}% (5m) | {price_change_1h:+.2f}% (1h)\n"
        message += f"├ Vol: ${volume:,.0f} | Liq: ${liquidity:,.0f}\n"
        message += f"└ <a href='{gmgn_link}'>🔗GMGN</a>\n\n"
    
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
    tokens = get_qualified_coins()
    if tokens:
        message = create_message(tokens)
        send_message(message)
    else:
        message = create_message([])
        send_message(message)
