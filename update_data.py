import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

def fetch_multpl_table(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', id='datatable')
    if not table:
        return []
    
    data = []
    rows = table.find_all('tr')
    for row in rows[1:]:  # 跳過表頭
        cols = row.find_all('td')
        if len(cols) >= 2:
            date_str = cols[0].get_text(strip=True)
            # 轉換數值，移除逗號並處理可能的多餘文字
            try:
                val = float(cols[1].get_text(strip=True).replace(',', '').split()[0])
                data.append({"date": date_str, "val": val})
            except (ValueError, IndexError):
                continue
    return data

def main():
    print("🚀 正在從 multpl.com 抓取數據...")
    
    cape_hist = fetch_multpl_table('https://www.multpl.com/shiller-pe/table/by-month')
    price_hist = fetch_multpl_table('https://www.multpl.com/s-p-500-historical-prices/table/by-month')
    gdp_hist = fetch_multpl_table('https://www.multpl.com/us-gdp/table/by-quarter')

    if not cape_hist or not price_hist or not gdp_hist:
        print("❌ 抓取失敗，請檢查來源網頁結構。")
        return

    # 封裝成 HTML 預期的格式
    market_data = {
        "ts": int(datetime.now().timestamp() * 1000),
        "cape": cape_hist[0]['val'],
        "price": price_hist[0]['val'],
        "gdp": gdp_hist[0]['val'] * 1000, # GDP 通常以 Billion 為單位，轉為 Million 或配合公式
        "history": {
            "cape": cape_hist,
            "price": price_hist,
            "gdp": [{"date": d['date'], "val": d['val'] * 1000} for d in gdp_hist]
        }
    }

    # 確保資料夾存在
    os.makedirs('data', exist_ok=True)
    
    with open('data/market_data.json', 'w', encoding='utf-8') as f:
        json.dump(market_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 數據更新完成：data/market_data.json")

if __name__ == "__main__":
    main()