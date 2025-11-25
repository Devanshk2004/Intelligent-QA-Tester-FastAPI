from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from dotenv import load_dotenv

from vector_db import process_and_store_documents
from llm_helper import ask_bot, generate_selenium_script

load_dotenv()

app = FastAPI(title="QA Agent API")

class QueryRequest(BaseModel):
    query: str
    api_key: Optional[str] = None

class ScriptRequest(BaseModel):
    test_case: str
    html_code: str
    api_key: Optional[str] = None

class FileAdapter:
    def __init__(self, upload_file: UploadFile):
        self.name = upload_file.filename
        self.file_obj = upload_file.file
    
    def read(self):
        return self.file_obj.read()


@app.get("/")
def health_check():
    return {"status": "running", "message": "QA Agent Backend is Active"}

@app.post("/upload-docs")
async def upload_documents(files: List[UploadFile] = File(...)):
    try:
        if os.path.exists("chroma_db"):
            shutil.rmtree("chroma_db")
            
        adapted_files = [FileAdapter(f) for f in files]
        
        status, html_content = process_and_store_documents(adapted_files)
        
        return {
            "status": "success",
            "message": status,
            "html_content": html_content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-test-cases")
async def generate_tests(request: QueryRequest):
    try:
        api_key = request.api_key if request.api_key else os.getenv("GEMINI_API_KEY")
        response = ask_bot(request.query, api_key)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-script")
async def generate_script_endpoint(request: ScriptRequest):
    try:
        api_key = request.api_key if request.api_key else os.getenv("GEMINI_API_KEY")
        script = generate_selenium_script(request.test_case, request.html_code, api_key)
        return {"script": script}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))