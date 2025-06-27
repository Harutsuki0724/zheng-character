
# GPT_RP API

以 **FastAPI** 打造的輕量角色扮演後端，能讀取 9 份 YAML 劇本資料並管理多玩家對話 Session。
適合放置於 **GPTs > 後台動作** 中，成為前台聊天機器人的工具 API。

## 安裝

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 檔案結構

```
GPT_RP_API/
├── GPT_RP.py
├── data/                 # ← 將 9 個 YAML 檔放入此處
│   ├── 玩家角色卡.yaml
│   └── ...
├── requirements.txt
└── README.md
```

## 執行

```bash
uvicorn GPT_RP:app --reload
```

* 預設埠：<http://127.0.0.1:8000>  
* 自動生成 Swagger UI：<http://127.0.0.1:8000/docs>

## 端點說明

| 方法 | 路徑 | 功能 |
|--|--|--|
| POST | /session | 建立新視窗 / 會話 |
| POST | /start_storyline | 寫入開場銜接事件 |
| POST | /message | 玩家發言 |
| GET  | /bundle/{session_id} | 取得歷史 (JSON) |
| POST | /import_history | 匯入歷史至新視窗 |

### Chat 窗口操作流程示例

1. `POST /session` 帶入 `open_status_bar` 與 `player_card`。  
2. (可選) `POST /start_storyline` 注入開場劇情。  
3. 重複 `POST /message` 完成對話。  
4. 換聊天窗前：`GET /bundle/{session_id}` 取回 history → 存檔。  
5. 新聊天窗：`POST /session` 建立新 session → `POST /import_history` 將 history 帶入。

## 系統指令 (可自行擴充)

* `/stash` → 取得歷史並存檔  
* `/load`  → 在新窗匯入歷史  

## License

MIT

## Render 部署

1. 登入 [Render](https://dashboard.render.com) 後，選擇 **New → Web Service**  
2. 連結 GitHub 儲存庫 (或選擇「Public Git Deploy」直接指向倉庫 URL)  
3. Render 會自動偵測 `render.yaml`，以 Blueprint 方式建立服務：  
   * Runtime: **Python**  
   * Build Command: `pip install -r requirements.txt`  
   * Start Command: `uvicorn GPT_RP:app --host 0.0.0.0 --port $PORT`  
4. 點擊 **Create Web Service** 即可。首次建置完成後，公開網址類似：  
   ```
   https://gpt-rp-api.onrender.com
   ```  
5. 若要手動設定而不使用 Blueprint，可刪除 `render.yaml`，並僅保留 `Procfile`；Render 仍能自動推論設定。

### 常見問題

* **SSL 與 CORS**  
  Render 網址預設走 HTTPS，若前端 (GPTs) 與 API 位於不同網域，請在 FastAPI 加入 `CORSMiddleware`。  
* **環境變數**  
  若 YAML 劇本太大想改讀外部儲存，請在 Render → Environment 欄位新增 `SCRIPTS_BUCKET` 等自訂參數。
