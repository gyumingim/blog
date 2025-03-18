from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import json
import os
import re
import uvicorn
import markdown

templates = Jinja2Templates(directory="templates")

# 모든 JSON 파일을 순서대로 읽기
articles_dir = "./templates/articles"
articles_data = []
articles_html = {}

weekly_dir = "./templates/weekly"
weekly_data = []
weekly_html = {}

# CSS 파일의 상대 경로

# 숫자 순서대로 정렬하기 위한 함수
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# 콘텐츠 로드 함수 (재사용 가능)
def load_content_data(directory, data_list, html_cache):
    try:
        # 디렉토리에서 모든 JSON 파일 가져오기
        json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
        # 파일명 기준으로 정렬
        json_files.sort(key=natural_sort_key)
        print(f"{directory} 디렉토리 처리 시작")
        
        # 각 JSON 파일 읽기
        for json_file in json_files:
            print(f"JSON 파일 처리: {json_file}")
            file_path = os.path.join(directory, json_file)
            with open(file_path, "r", encoding="utf-8") as file:
                content_data = json.load(file)
                data_list.append(content_data)
            
            # 파일 번호 추출 (확장자 제거)
            content_number = int(os.path.splitext(json_file)[0])
            
            # HTML 또는 MD 파일 확인
            html_filename = f"{content_number}.html"
            md_filename = f"{content_number}.md"
            html_path = os.path.join(directory, html_filename)
            md_path = os.path.join(directory, md_filename)
            
            # MD 파일이 있으면 우선 처리
            if os.path.exists(md_path):
                try:
                    with open(md_path, "r", encoding="utf-8") as md_file:
                        md_content = md_file.read()
                        # Markdown을 HTML로 변환
                        html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite', 'attr_list'])
                        html_cache[content_number] = html_content
                        print(f"Markdown 파일 변환: {md_filename}")
                        print(type(html_content))
                except Exception as e:
                    print(f"MD 파일 처리 오류: {e}")
            # HTML 파일 처리
            # elif os.path.exists(html_path):
            #     try:
            #         with open(html_path, "r", encoding="utf-8") as html_file:
            #             html_cache[content_number] = html_file.read()
            #             print(f"HTML 파일 로드: {html_filename}")
            #     except Exception as e:
            #         print(f"HTML 파일 처리 오류: {e}")
    except Exception as e:
        print(f"디렉토리 처리 오류: {e}")

# 콘텐츠 데이터 로드
load_content_data(articles_dir, articles_data, articles_html)
load_content_data(weekly_dir, weekly_data, weekly_html)

app = FastAPI()

# CORS 설정 - 배포 시 실제 도메인으로 변경 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 출처로 설정하세요
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

@app.get("/work")
def work():
    return FileResponse("templates/work.html")

@app.get("/article")
def article_list():
    return templates.TemplateResponse("article.html", {"request": {}, "data": articles_data})

@app.get("/weekly")
def weekly_list():
    return templates.TemplateResponse("weekly.html", {"request": {}, "data": weekly_data})

# 통합된 콘텐츠 상세 페이지 처리 함수
def get_content_detail(content_number, content_type):
    # 콘텐츠 타입에 따라 데이터와 캐시 선택
    if content_type == "article":
        data_list = articles_data
        html_cache = articles_html
        content_dir = articles_dir
        template_name = "article_one.html"
        content_key = "article_number"
    else:  # weekly
        data_list = weekly_data
        html_cache = weekly_html
        content_dir = weekly_dir
        template_name = "weekly_one.html"
        content_key = "weekly_number"
    
    # 유효성 검사
    if content_number <= 0 or content_number > len(data_list):
        raise HTTPException(status_code=404, detail=f"{content_type.capitalize()} not found")
    
    # 이전/다음 글 데이터
    back_data = data_list[content_number-2] if content_number-2 >= 0 else None
    front_data = data_list[content_number] if content_number < len(data_list) else None
    
    # HTML 내용 가져오기
    contents = html_cache.get(content_number, "")
    if not contents:
        # 먼저 MD 파일 확인
        md_path = os.path.join(content_dir, f"{content_number}.md")
        # html_path = os.path.join(content_dir, f"{content_number}.html")
        
        if os.path.exists(md_path):
            try:
                with open(md_path, "r", encoding="utf-8") as md_file:
                    md_content = md_file.read()
                    # Markdown을 HTML로 변환
                    contents = markdown.markdown(md_content, extensions=['extra', 'codehilite'])
                    # 캐시에 저장
                    html_cache[content_number] = contents
            except FileNotFoundError:
                contents = "<p>Markdown 내용이 없습니다.</p>"
        elif os.path.exists(html_path):
            try:
                with open(html_path, "r", encoding="utf-8") as html_file:
                    contents = html_file.read()
                    # 캐시에 저장
                    html_cache[content_number] = contents
            except FileNotFoundError:
                contents = "<p>HTML 내용이 없습니다.</p>"
        else:
            contents = "<p>컨텐츠를 찾을 수 없습니다.</p>"
    
    # 템플릿 응답 데이터 준비
    template_data = {
        "request": {}, 
        "html": contents,
        "data": data_list[content_number-1],
        "back": back_data,
        "front": front_data,
    }
    # 콘텐츠 번호 추가 (키 이름이 다름)
    template_data[content_key] = content_number
    
    return templates.TemplateResponse(template_name, template_data)

@app.get("/article/{article_number}")
def article_detail(article_number: int):
    return get_content_detail(article_number, "article")

@app.get("/weekly/{weekly_number}")
def weekly_detail(weekly_number: int):
    return get_content_detail(weekly_number, "weekly")

# 서버 실행 코드 (직접 실행 시에만 작동)
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
