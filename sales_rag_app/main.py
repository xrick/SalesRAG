import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libs.service_manager import ServiceManager 


# from libs.service_manager import ServiceManager

# 載入環境變數
load_dotenv()

# 初始化 FastAPI 應用
app = FastAPI()

# 掛載靜態檔案目錄
app.mount("/static", StaticFiles(directory="static"), name="static")

# 設定模板目錄
templates = Jinja2Templates(directory="sales_rag_app/templates")

# 初始化服務管理器
service_manager = ServiceManager()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """渲染主頁面"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/get-services", response_class=JSONResponse)
async def get_services():
    """獲取可用的服務列表"""
    services = service_manager.list_services()
    return {"services": services}

@app.post("/api/chat-stream")
async def chat_stream(request: Request):
    """處理聊天請求並返回流式響應"""
    try:
        data = await request.json()
        query = data.get("query")
        service_name = data.get("service_name", "sales_assistant") # 預設使用銷售助理

        if not query:
            return JSONResponse(status_code=400, content={"error": "Query cannot be empty"})

        service = service_manager.get_service(service_name)
        if not service:
             return JSONResponse(status_code=404, content={"error": f"Service '{service_name}' not found"})

        # 返回一個流式響應，從服務的 chat_stream 方法獲取內容
        return StreamingResponse(service.chat_stream(query), media_type="text/event-stream")

    except Exception as e:
        print(f"Error in chat_stream: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)