from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import tempfile
import shutil
import json
from typing import Optional
import pypdf
# import fitz  # PyMuPDF - 웹앱에서는 사용하지 않음

app = FastAPI(title="서울자가김부장용PDF편집기 Ver 1.3")

# 임시 파일 저장 디렉토리
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 업로드된 PDF 파일 저장
uploaded_files = {}

# Undo 스택 저장 {file_id: [undo_states]}
undo_stacks = {}
MAX_UNDO = 10

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """메인 페이지"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """PDF 파일 업로드"""
    try:
        # 임시 파일에 저장
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=TEMP_DIR)
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()
        
        file_id = Path(temp_file.name).stem
        uploaded_files[file_id] = temp_file.name
        
        # Undo 스택 초기화
        undo_stacks[file_id] = []
        
        # PDF 정보 가져오기
        pdf_reader = pypdf.PdfReader(temp_file.name)
        page_count = len(pdf_reader.pages)
        
        return JSONResponse({
            "file_id": file_id,
            "filename": file.filename,
            "page_count": page_count
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pdf/{file_id}")
async def get_pdf(file_id: str):
    """PDF 파일 다운로드"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = uploaded_files[file_id]
    return FileResponse(file_path, media_type="application/pdf")

@app.get("/api/pdf/{file_id}/info")
async def get_pdf_info(file_id: str):
    """PDF 정보 가져오기"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = uploaded_files[file_id]
    pdf_reader = pypdf.PdfReader(file_path)
    
    return JSONResponse({
        "page_count": len(pdf_reader.pages),
        "filename": Path(file_path).name
    })

@app.get("/api/pdf/{file_id}/download")
async def download_pdf(file_id: str):
    """PDF 파일 다운로드"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = uploaded_files[file_id]
    return FileResponse(file_path, media_type="application/pdf", filename=Path(file_path).name)

def save_undo_state(file_id: str):
    """현재 상태를 Undo 스택에 저장"""
    if file_id not in uploaded_files:
        return
    
    if file_id not in undo_stacks:
        undo_stacks[file_id] = []
    
    try:
        file_path = uploaded_files[file_id]
        # 현재 파일을 복사하여 Undo 상태로 저장
        undo_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=TEMP_DIR)
        shutil.copy2(file_path, undo_file.name)
        undo_file.close()
        
        undo_stacks[file_id].append(undo_file.name)
        
        # 최대 개수 제한
        if len(undo_stacks[file_id]) > MAX_UNDO:
            old_file = undo_stacks[file_id].pop(0)
            try:
                Path(old_file).unlink()
            except:
                pass
    except Exception as e:
        print(f"Error saving undo state: {e}")

@app.post("/api/pdf/{file_id}/pages/reorder")
async def reorder_pages(file_id: str, reorder_data: dict):
    """페이지 순서 변경"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Undo 상태 저장
        save_undo_state(file_id)
        
        file_path = uploaded_files[file_id]
        pdf_reader = pypdf.PdfReader(file_path)
        pdf_writer = pypdf.PdfWriter()
        
        from_idx = reorder_data.get("from")
        to_idx = reorder_data.get("to")
        
        # 페이지 순서 배열 생성
        pages = list(range(len(pdf_reader.pages)))
        pages[from_idx], pages[to_idx] = pages[to_idx], pages[from_idx]
        
        # 새로운 순서로 페이지 추가
        for page_num in pages:
            pdf_writer.add_page(pdf_reader.pages[page_num])
        
        # 임시 파일에 저장
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=TEMP_DIR)
        pdf_writer.write(temp_file)
        temp_file.close()
        
        # 원본 파일 교체
        shutil.move(temp_file.name, file_path)
        
        return JSONResponse({"status": "success"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pdf/{file_id}/pages/add-range")
async def add_pages_range(file_id: str, add_data: dict):
    """다른 PDF에서 특정 페이지 범위 추가"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    source_file_id = add_data.get("source_file_id")
    if source_file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="Source file not found")
    
    pages = add_data.get("pages", [])  # 0-based index list
    insert_position = add_data.get("insert_position", 0)
    
    try:
        # Undo 상태 저장
        save_undo_state(file_id)
        
        file_path = uploaded_files[file_id]
        source_path = uploaded_files[source_file_id]
        
        pdf_reader = pypdf.PdfReader(file_path)
        source_reader = pypdf.PdfReader(source_path)
        pdf_writer = pypdf.PdfWriter()
        
        # 기존 페이지 추가 (insert_position 전까지)
        for i in range(insert_position):
            pdf_writer.add_page(pdf_reader.pages[i])
        
        # 새 페이지 추가
        for page_idx in pages:
            if 0 <= page_idx < len(source_reader.pages):
                pdf_writer.add_page(source_reader.pages[page_idx])
        
        # 나머지 기존 페이지 추가
        for i in range(insert_position, len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[i])
        
        # 임시 파일에 저장
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=TEMP_DIR)
        pdf_writer.write(temp_file)
        temp_file.close()
        
        # 원본 파일 교체
        shutil.move(temp_file.name, file_path)
        
        return JSONResponse({
            "status": "success",
            "page_count": len(pdf_writer.pages)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pdf/{file_id}/undo")
async def undo_last_action(file_id: str):
    """마지막 작업 되돌리기"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file_id not in undo_stacks or len(undo_stacks[file_id]) == 0:
        raise HTTPException(status_code=400, detail="No undo history available")
    
    try:
        # 마지막 Undo 상태 가져오기
        undo_file = undo_stacks[file_id].pop()
        file_path = uploaded_files[file_id]
        
        # 현재 파일을 Undo 상태로 복원
        shutil.copy2(undo_file, file_path)
        
        # Undo 파일 삭제
        try:
            Path(undo_file).unlink()
        except:
            pass
        
        # PDF 정보 가져오기
        pdf_reader = pypdf.PdfReader(file_path)
        page_count = len(pdf_reader.pages)
        
        return JSONResponse({
            "status": "success",
            "page_count": page_count
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pdf/{file_id}/undo/status")
async def get_undo_status(file_id: str):
    """Undo 가능 여부 확인"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    can_undo = file_id in undo_stacks and len(undo_stacks[file_id]) > 0
    
    return JSONResponse({
        "can_undo": can_undo,
        "undo_count": len(undo_stacks.get(file_id, []))
    })

@app.delete("/api/pdf/{file_id}/pages/{page_num}")
async def delete_page(file_id: str, page_num: int):
    """페이지 삭제"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Undo 상태 저장
        save_undo_state(file_id)
        
        file_path = uploaded_files[file_id]
        pdf_reader = pypdf.PdfReader(file_path)
        pdf_writer = pypdf.PdfWriter()
        
        # 해당 페이지 제외하고 추가
        for i, page in enumerate(pdf_reader.pages):
            if i != page_num:
                pdf_writer.add_page(page)
        
        # 임시 파일에 저장
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=TEMP_DIR)
        pdf_writer.write(temp_file)
        temp_file.close()
        
        # 원본 파일 교체
        shutil.move(temp_file.name, file_path)
        
        return JSONResponse({"status": "success", "page_count": len(pdf_writer.pages)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

