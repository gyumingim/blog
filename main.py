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


# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 디렉토리 경로
articles_dir = "./templates/articles"
work_dir = "./templates/work"
awards_dir = "./templates/awards"

# 데이터 및 HTML 캐시 저장소
articles_data = []
articles_html = {}
work_data = []
work_html = {}
awards_data = []
awards_html = {}

# 숫자 순서대로 정렬하기 위한 함수 (역순)
def natural_sort_key(s):
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
        md_files = glob.glob(os.path.join(directory, "*.md"))
        md_files.sort(key=natural_sort_key)
        print(f"{directory} 디렉토리 처리 시작")
        for md_file in md_files:
            print(f"마크다운 파일 처리: {md_file}")
            metadata, md_content = parse_markdown_file(md_file)
            if not metadata:
                print(f"메타데이터 없음: {md_file}")
                continue
            if 'id' not in metadata or 'title' not in metadata:
                print(f"필수 메타데이터 누락: {md_file}")
                continue
            if 'thumbnail' in metadata:
                metadata['thumbnail'] = 'static/image/' + metadata['thumbnail']
            data_list.append(metadata)
            content_number = int(metadata['id'])
            html_content = markdown.markdown(md_content, extensions=['fenced_code', 'extra'])
            html_cache[content_number] = html_content
            print(f"Markdown 파일 변환 완료: {md_file}, ID: {content_number}")
    except Exception as e:
        print(f"디렉토리 처리 오류: {e}")

# 콘텐츠 데이터 로드
load_content_data(articles_dir, articles_data, articles_html)
load_content_data(work_dir, work_data, work_html)
load_content_data(awards_dir, awards_data, awards_html)

# ID 기준으로 데이터 정렬 (내림차순)
articles_data.sort(key=lambda x: -int(x['id']))
work_data.sort(key=lambda x: -int(x['id']))
awards_data.sort(key=lambda x: -int(x['id']))

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

@app.get("/award")
def award_list():
    return templates.TemplateResponse("award.html", {"request": {}, "data": awards_data})

# 통합된 콘텐츠 상세 페이지 처리 함수
def get_content_detail(content_id, content_type):
    if content_type == "article":
        data_list, html_cache = articles_data, articles_html
        template_name, key = "article_one.html", "article_number"
    elif content_type == "work":
        data_list, html_cache = work_data, work_html
        template_name, key = "work_one.html", "work_number"
    elif content_type == "award":
        data_list, html_cache = awards_data, awards_html
        template_name, key = "award_one.html", "award_number"
    else:
        raise HTTPException(status_code=404, detail="Invalid content type")

    content_data = next((item for item in data_list if item['id'] == content_id), None)
    if content_data is None:
        raise HTTPException(status_code=404, detail=f"{content_type.capitalize()} not found")

    idx = data_list.index(content_data)
    front = data_list[idx - 1] if idx > 0 else None
    back = data_list[idx + 1] if idx < len(data_list) - 1 else None

    html = html_cache.get(content_id, "<p>컨텐츠를 찾을 수 없습니다.</p>")

    context = {
        "request": {},
        "html": html,
        "data": content_data,
        "front": front,
        "back": back,
        key: content_id
    }
    return templates.TemplateResponse(template_name, context)

@app.get("/article/{article_id}")
def article_detail(article_id: int):
    return get_content_detail(article_id, "article")

@app.get("/work/{work_id}")
def work_detail(work_id: int):
    return get_content_detail(work_id, "work")

# 서버 실행 코드
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
