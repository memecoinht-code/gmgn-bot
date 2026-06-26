import requests
from datetime import datetime

TELEGRAM_TOKEN = "8698225504:AAGKuWc12_OMFTG1o9xUmpv5J9ztiz7JbRA"
TELEGRAM_CHAT_ID = "1041523200"

GMGN_API = "https://api.gmgn.ai/trending"
CHAIN = "sol"

def debug_coins():
    try:
        params = {"chain": CHAIN, "limit": 200}
        response = requests.get(GMGN_API, params=params, timeout=15)
        data = response.json()
        tokens = data.get("data", [])
        
        print(f"✅ Lấy được {len(tokens)} tokens\n")
        
        # In chi tiết 10 token đầu tiên
        print("TOP 10 COINS:")
        print("-" * 80)
        for idx, token in enumerate(tokens[:10], 1):
            symbol = token.get('symbol', 'N/A')
            price = token.get('price', 0)
            change_1m = token.get('price_change_1m', 'N/A')
            change_5m = token.get('price_change_5m', 'N/A')
            change_1h = token.get('price_change_1h', 'N/A')
            liquidity = token.get('liquidity', 0)
            age_days = "N/A"
            
            created_at = token.get('created_at')
            if created_at:
                try:
                    created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    age_days = (datetime.now(created_time.tzinfo) - created_time).days
                except:
                    pass
            
            print(f"\n{idx}. {symbol}")
            print(f"   Giá: ${price}")
            print(f"   % Thay đổi 1m: {change_1m}% | 5m: {change_5m}% | 1h: {change_1h}%")
            print(f"   Liquidity: ${liquidity:,.0f}")
            print(f"   Tuổi: {age_days} ngày")
            print(f"   Twitter: {'✅' if token.get('socials', {}).get('twitter') else '❌'}")
            print(f"   Mintable: {'❌ (Bad)' if token.get('is_mintable') else '✅'}")
            print(f"   Blacklist: {'❌ (Bad)' if token.get('is_blacklisted') else '✅'}")
            print(f"   LP Burned: {'✅' if token.get('lp_burned') else '❌'}")
            print(f"   Freeze Auth: {'❌ (Bad)' if token.get('freeze_authority') else '✅'}")
        
        # Gửi Telegram
        message = f"<b>🔍 DEBUG GMGN</b>\n\n"
        message += f"✅ Tổng tokens: {len(tokens)}\n\n"
        
        # Đếm coins đạt từng tiêu chí
        count_change = 0
        count_age = 0
        count_liq = 0
        count_twitter = 0
        count_mint = 0
        count_blacklist = 0
        count_lp = 0
        count_freeze = 0
        count_all = 0
        
        for token in tokens:
            change = token.get('price_change_1m', token.get('price_change_5m', 0))
            if change <= -7 or change >= 7:
                count_change += 1
            
            created_at = token.get('created_at')
            if created_at:
                try:
                    created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    age_days = (datetime.now(created_time.tzinfo) - created_time).days
                    if age_days >= 3:
                        count_age += 1
                except:
                    pass
            
            liq = token.get('liquidity', 0)
            if liq >= 70000:
                count_liq += 1
            
            if token.get('socials', {}).get('twitter'):
                count_twitter += 1
            
            if not token.get('is_mintable'):
                count_mint += 1
            
            if not token.get('is_blacklisted'):
                count_blacklist += 1
            
            if token.get('lp_burned'):
                count_lp += 1
            
            if not token.get('freeze_authority'):
                count_freeze += 1
            
            # Tất cả tiêu chí
            if (change <= -7 or change >= 7) and age_days >= 3 and liq >= 70000 and token.get('socials', {}).get('twitter') and not token.get('is_mintable') and not token.get('is_blacklisted') and token.get('lp_burned') and not token.get('freeze_authority'):
                count_all += 1
        
        message += f"<b>📊 THỐNG KÊ TIÊU CHÍ:</b>\n"
        message += f"📈 % Thay đổi ±7%: {count_change}\n"
        message += f"📅 Tuổi 3+ ngày: {count_age}\n"
        message += f"💧 Liquidity 70k+: {count_liq}\n"
        message += f"🐦 Có Twitter: {count_twitter}\n"
        message += f"🚫 Không mint: {count_mint}\n"
        message += f"✅ Không blacklist: {count_blacklist}\n"
        message += f"🔥 LP burned: {count_lp}\n"
        message += f"❄️ Freeze auth: {count_freeze}\n"
        message += f"\n<b>✅ ĐẠT TẤT CẢ TIÊU CHÍ: {count_all}</b>\n"
        message += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
        
        # Gửi
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
            requests.post(url, data=data, timeout=10)
        except:
            pass
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    debug_coins()
