
"""
GPT_RP: Lightweight Role‑Play API

功能概要
------------
* 讀取 9 個 YAML 劇本檔案以作為背景資料  
* 為每位玩家建立獨立 Session，儲存：狀態欄開啟狀態、玩家角色卡、對話歷史  
* 提供端點：建立視窗 / 啟動劇情 / 玩家發話 / 打包歷史 / 載入歷史  
* 可整合至「GPTs → 後台動作」(工具模式)；於 GPTs 前台呼叫 `https://your-host/session ...` 等端點
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import yaml, uuid
from typing import List, Dict, Any

DATA_DIR = Path(__file__).parent / "data"
YAML_FILES = [
    "玩家角色卡.yaml",
    "place.yaml",
    "薄言錚人設.yaml",
    "狀態欄.yaml",
    "開場銜接事件.yaml",
    "角色互動守則.yaml",
    "情感漸進.yaml",
    "薄言錚相關人物.yaml",
    "薄言錚四年之謎.yaml",
]

# ---------- Utilities ----------
def load_yaml(name: str) -> Any:
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"{name} not found in {DATA_DIR}.")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ---------- Domain -------------
class SessionData:
    """In‑memory session model"""
    def __init__(self, open_status_bar: bool = False, player_card: str = "") -> None:
        self.id: str = str(uuid.uuid4())
        self.open_status_bar: bool = open_status_bar
        self.player_card: str = player_card
        self.history: List[Dict[str, Any]] = []

    def to_dict(self):
        return {
            "session_id": self.id,
            "open_status_bar": self.open_status_bar,
            "player_card": self.player_card,
            "history": self.history,
        }

# {session_id: SessionData}
_SESSIONS: Dict[str, SessionData] = {}

# ---------- FastAPI ------------
app = FastAPI(
    title="GPT_RP API",
    version="0.1.0",
    summary="Role‑Play session back‑end driven by YAML scenario files.",
)

# --------- Pydantic models -----
class NewSessionBody(BaseModel):
    open_status_bar: bool = False
    player_card: str = ""

class MessageBody(BaseModel):
    session_id: str
    message: str

class SessionOnly(BaseModel):
    session_id: str

class ImportHistoryBody(SessionOnly):
    history: List[Dict[str, Any]]

# --------- Endpoints -----------
@app.post("/session", summary="建立新視窗 / 會話")
def new_session(body: NewSessionBody):
    sess = SessionData(body.open_status_bar, body.player_card)
    _SESSIONS[sess.id] = sess
    # 若使用者選擇開啟狀態欄，自動注入 YAML 狀態欄內容
    if sess.open_status_bar:
        status_bar_cfg = load_yaml("狀態欄.yaml")
        sess.history.append({"role": "system", "content": status_bar_cfg})
    return sess.to_dict()

@app.post("/start_storyline", summary="匯入開場銜接事件並寫入歷史")
def start_storyline(body: SessionOnly):
    sess = _SESSIONS.get(body.session_id)
    if not sess:
        raise HTTPException(404, "Session not found.")
    storyline = load_yaml("開場銜接事件.yaml")
    sess.history.append({"role": "system", "content": storyline})
    return {"ok": True}

@app.post("/message", summary="玩家發話")
def add_message(body: MessageBody):
    sess = _SESSIONS.get(body.session_id)
    if not sess:
        raise HTTPException(404, "Session not found.")
    sess.history.append({"role": "user", "content": body.message})
    return {"ok": True}

@app.get("/bundle/{session_id}", summary="打包取得所有聊天歷史")
def bundle_history(session_id: str):
    sess = _SESSIONS.get(session_id)
    if not sess:
        raise HTTPException(404, "Session not found.")
    return {"history": sess.history}

@app.post("/import_history", summary="於新視窗匯入聊天歷史")
def import_history(body: ImportHistoryBody):
    sess = _SESSIONS.get(body.session_id)
    if not sess:
        raise HTTPException(404, "Session not found.")
    sess.history = body.history
    return {"ok": True}
