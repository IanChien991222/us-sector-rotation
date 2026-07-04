# 🇺🇸 US Sector Rotation Dashboard

**美股板塊輪動 & 資金流可視化儀表板** — inspired by [tide-tw.app](https://tide-tw.app)

> 追蹤 S&P 500 11 大板塊 ETF 的資金流向，以泡泡圖呈現板塊輪動態勢

## 功能特性

| 功能 | 說明 |
|------|------|
| **板塊泡泡圖** | X軸 = 當日資金流入/流出 ($M)，Y軸 = 5日趨勢，泡泡大小 = 20日累積資金流 |
| **4 象限分類** | 🟦 漲潮 (Rising) / 🟧 退潮 (Falling) / 🟩 輪動 (Rotating) / 🟨 翻望 (Watching) |
| **即時 S&P 500** | 顯示 SPY 當日漲跌幅 |
| **影藏排行** | 右側列出 11 板塊依當日資金流排序 |
| **自動更新** | GitHub Actions 每天工作日 UTC 21:00 & 22:00 自動拉取新資料 |

## 追蹤的 ETF

`XLK` 科技 | `XLF` 金融 | `XLV` 醫療 | `XLY` 非必需消費 | `XLC` 通訊 |
`XLI` 工業 | `XLP` 必需消費 | `XLE` 能源 | `XLU` 公用 | `XLRE` 房地產 | `XLB` 原材料

## 資料來源

- **yfinance** (Yahoo Finance 免費 API) — 無需付費 API Key
- 資金流計算公式: `(Close - Open) × Volume` 每日

## 專案結構

```
us-sector-rotation/
├── api_server.py          # FastAPI 後端 (本地開發用)
├── generate_data.py       # 靜態 JSON 生成器 (GitHub Actions 呼叫)
├── requirements.txt       # Python 依賴
├── static/
│   ├── index.html           # 前端頁面 (ECharts 泡泡圖)
│   └── data/                # 自動生成的 JSON (GitHub Actions)
│       ├── sectors.json
│       └── breadth.json
└── .github/workflows/
    └── update_data.yml      # 每天自動更新排程
```

## 快速啟動 (本地開發)

```bash
# 1. Clone
git clone https://github.com/IanChien991222/us-sector-rotation.git
cd us-sector-rotation

# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 啟動 API server
uvicorn api_server:app --reload --port 8000

# 4. 開瀏覽器開啟 http://localhost:8000
```

## GitHub Pages 部署 (静態模式)

1. 先執行 `python generate_data.py` 生成初始 JSON
2. 將 `static/index.html` 中的 API 呼叫改為讀取 `/data/sectors.json`
3. Settings > Pages > Source: `main` branch, `/static` folder
4. GitHub Actions 每天自動更新 `static/data/*.json`

## Tech Stack

| 層 | 技術 |
|-----|------|
| Frontend | HTML + ECharts 5 (CDN) |
| Backend | Python FastAPI + uvicorn |
| Data | yfinance (Yahoo Finance) |
| CI/CD | GitHub Actions (cron schedule) |
| 部署選項 | GitHub Pages / Vercel / Railway |

## License

MIT
