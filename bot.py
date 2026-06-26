import requests
import json
from datetime import datetime

TELEGRAM_TOKEN = "8698225504:AAGKuWc12_OMFTG1o9xUmpv5J9ztiz7JbRA"
TELEGRAM_CHAT_ID = "1041523200"

PHOTON_API = "https://api.photon-sol.tinyastro.io/trending"

def debug_photon():
    try:
        print("📡 Kết nối Photon API...")
        response = requests.get(PHOTON_API, timeout=15)
        data = response.json()
        
        print(f"✅ Kết nối thành công!\n")
        
        # In structure dữ liệu
        print("📊 STRUCTURE DỮ LIỆU:")
        print(f"Type: {type(data)}")
        print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'Không phải dict'}\n")
        
        # Lấy tokens
        if isinstance(data, dict):
            tokens = data.get('tokens', [])
        elif isinstance(data, list):
            tokens = data
        else:
            tokens = []
        
        print(f"✅ Tổng tokens: {len(tokens)}\n")
        
        # In 5 token đầu
        print("🔍 TOP 5 TOKENS CHI TIẾT:")
        print("-" * 100)
        
        for idx, token in enumerate(tokens[:5], 1):
            print(f"\n[Token {idx}]")
            print(f"Type: {type(token)}")
            
            if isinstance(token, dict):
                print("Keys có sẵn:")
                for key in sorted(token.keys()):
                    value = token[key]
                    if isinstance(value, (dict, list)) and len(str(value)) > 100:
                        print(f"  {key}: {type(value).__name__} (quá dài)")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"Value: {token}")
        
        # Gửi Telegram
        message = f"<b>🔍 DEBUG PHOTON API</b>\n\n"
        message += f"✅ Kết nối thành công!\n"
        message += f"📊 Tổng tokens: {len(tokens)}\n\n"
        
        message += f"<b>TOP 3 TOKENS:</b>\n\n"
        
        for idx, token in enumerate(tokens[:3], 1):
            if isinstance(token, dict):
                symbol = token.get('symbol', 'N/A')
                name = token.get('name', 'N/A')
                price = token.get('price', 'N/A')
                
                # Thử lấy % thay đổi với các key khác nhau
                change_h1 = 'N/A'
                if 'priceChange' in token:
                    if isinstance(token['priceChange'], dict):
                        change_h1 = token['priceChange'].get('h1', 'N/A')
                    else:
                        change_h1 = token['priceChange']
                elif 'h1' in token:
                    change_h1 = token['h1']
                elif 'change1h' in token:
                    change_h1 = token['change1h']
                
                # Thử lấy liquidity
                liquidity = 'N/A'
                if 'liquidity' in token:
                    liquidity = token['liquidity']
                elif 'usd' in token and isinstance(token.get('liquidity'), dict):
                    liquidity = token['liquidity']['usd']
                
                message += f"<b>{idx}. {symbol}</b> - {name}\n"
                message += f"├ Giá: {price}\n"
                message += f"├ % 1h: {change_h1}\n"
                message += f"└ Liquidity: {liquidity}\n\n"
        
        message += f"⏰ {datetime.now().strftime('%H:%M:%S')}"
        
        # Gửi
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            req_data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
            requests.post(url, data=req_data, timeout=10)
            print("✅ Đã gửi Telegram")
        except:
            pass
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        
        # Gửi lỗi qua Telegram
        message = f"<b>❌ LỖI DEBUG</b>\n\n{str(e)}\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            req_data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
            requests.post(url, data=req_data, timeout=10)
        except:
            pass

if __name__ == "__main__":
    debug_photon()
