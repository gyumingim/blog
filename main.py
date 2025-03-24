from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os
import re
import uvicorn
import markdown
import yaml
import glob


templates = Jinja2Templates(directory="templates")

# 디렉토리 경로
articles_dir = "./templates/articles"
work_dir = "./templates/work"

# 데이터 및 HTML 캐시 저장소
articles_data = []
articles_html = {}
work_data = []
work_html = {}

# 숫자 순서대로 정렬하기 위한 함수 (역순)
def natural_sort_key(s):
    # 기존 로직을 유지하되, 역순 정렬을 위해 음수 값을 반환
    return [-int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# 마크다운 파일에서 메타데이터와 내용을 추출하는 함수
def parse_markdown_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    parts = content.split('---', 2)
    if len(parts) > 1:
        try:
            metadata = yaml.safe_load(parts[1].strip())
            return metadata, parts[2].strip() if len(parts) > 2 else ""
        except Exception as e:
            print(f"메타데이터 파싱 오류: {e}")
    
    return {}, content

# 콘텐츠 로드 함수 (재사용 가능)
def load_content_data(directory, data_list, html_cache):
    try:
        # 디렉토리에서 모든 마크다운 파일 가져오기
        md_files = glob.glob(os.path.join(directory, "*.md"))
        
        # 파일명 기준으로 정렬
        md_files.sort(key=natural_sort_key)
        print(f"{directory} 디렉토리 처리 시작")
        
        # 각 마크다운 파일 읽기
        for md_file in md_files:
            print(f"마크다운 파일 처리: {md_file}")
            
            # 메타데이터와 내용 추출
            metadata, md_content = parse_markdown_file(md_file)
            
            if not metadata:
                print(f"메타데이터 없음: {md_file}")
                continue
            
            # 필수 메타데이터 확인
            if 'id' not in metadata or 'title' not in metadata:
                print(f"필수 메타데이터 누락: {md_file}")
                continue
            
            # 데이터 목록에 추가
            data_list.append(metadata)
            
            # HTML 변환 및 캐시 저장
            content_number = int(metadata['id'])
            html_content = markdown.markdown(md_content, extensions=['fenced_code'])
            html_cache[content_number] = html_content
            print(f"Markdown 파일 변환 완료: {md_file}, ID: {content_number}")
            
    except Exception as e:
        print(f"디렉토리 처리 오류: {e}")

# 콘텐츠 데이터 로드
load_content_data(articles_dir, articles_data, articles_html)
load_content_data(work_dir, work_data, work_html)

# ID 기준으로 데이터 정렬 (내림차순)
articles_data.sort(key=lambda x: -int(x['id']))
work_data.sort(key=lambda x: -int(x['id']))

app = FastAPI()

# CORS 설정 - 배포 시 실제 도메인으로 변경 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 설정
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
@app.head("/")
def root():
    return FileResponse("templates/about.html")

@app.get("/article")
def article_list():
    return templates.TemplateResponse("article.html", {"request": {}, "data": articles_data})

@app.get("/work")
def work_list():
    return templates.TemplateResponse("work.html", {"request": {}, "data": work_data})

# 통합된 콘텐츠 상세 페이지 처리 함수
def get_content_detail(content_id, content_type):
    # 콘텐츠 타입에 따라 데이터와 캐시 선택
    if content_type == "article":
        data_list = articles_data
        html_cache = articles_html
        content_dir = articles_dir
        template_name = "article_one.html"
        content_key = "article_number"
    else:  # work
        data_list = work_data
        html_cache = work_html
        content_dir = work_dir
        template_name = "work_one.html"
        content_key = "work_number"
    
    # ID로 데이터 찾기
    content_data = None
    content_index = -1
    for i, item in enumerate(data_list):
        if item['id'] == content_id:
            content_data = item
            content_index = i
            break
    
    # 데이터가 없으면 404 에러
    if content_data is None:
        raise HTTPException(status_code=404, detail=f"{content_type.capitalize()} not found")
    
    # 이전/다음 글 데이터 - 역순 정렬에 맞게 수정
    # 역순 정렬이므로 이전(back)은 리스트의 다음 항목, 다음(front)은 리스트의 이전 항목
    front_data = data_list[content_index - 1] if content_index > 0 else None
    back_data = data_list[content_index + 1] if content_index < len(data_list) - 1 else None
    
    # HTML 내용 가져오기
    contents = html_cache.get(content_id, "")
    if not contents:
        contents = "<p>컨텐츠를 찾을 수 없습니다.</p>"
    
    # 템플릿 응답 데이터 준비
    template_data = {
        "request": {}, 
        "html": contents,
        "data": content_data,
        "back": back_data,
        "front": front_data,
    }
    # 콘텐츠 번호 추가 (키 이름이 다름)
    template_data[content_key] = content_id
    
    return templates.TemplateResponse(template_name, template_data)

@app.get("/article/{article_id}")
def article_detail(article_id: int):
    return get_content_detail(article_id, "article")

@app.get("/work/{work_id}")
def work_detail(work_id: int):
    return get_content_detail(work_id, "work")

# 서버 실행 코드 (직접 실행 시에만 작동)
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
