from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # 이 부분이 누락되었습니다
from jinja2 import Environment, FileSystemLoader
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import json
import os
import re
import uvicorn

templates = Jinja2Templates(directory="templates")

# 모든 JSON 파일을 순서대로 읽기
articles_dir = "./templates/articles"
articles_data = []

# HTML 파일 내용을 저장할 딕셔너리 추가
articles_html = {}

# 숫자 순서대로 정렬하기 위한 함수
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

try:
    # 디렉토리에서 모든 JSON 파일 가져오기
    json_files = [f for f in os.listdir(articles_dir) if f.endswith('.json')]
    # 파일명 기준으로 정렬 (1.json, 2.json, ... 10.json 순서로)
    json_files.sort(key=natural_sort_key)
    print("try문 실행")
    # 각 JSON 파일 읽기
    for json_file in json_files:
        print("json_file", json_file)
        file_path = os.path.join(articles_dir, json_file)
        with open(file_path, "r", encoding="utf-8") as file:
            article_data = json.load(file)
            articles_data.append(article_data)
            
        # 해당 번호의 HTML 파일이 있는지 확인하고 내용 불러오기
        html_filename = json_file.replace('.json', '.html')
        html_path = os.path.join(articles_dir, html_filename)
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as html_file:
                # 파일 번호를 키로 사용 (확장자 제거)
                article_number = int(os.path.splitext(json_file)[0])
                articles_html[article_number] = html_file.read()
                print(f"HTML 파일 로드: {html_filename}")

except Exception as e:
    print("error", e)

app = FastAPI()

# CORS 설정 - 배포 시 실제 도메인으로 변경 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 출처로 설정하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 설정 (캐싱 헤더 추가)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
@app.head("/")
def root():
    return FileResponse("templates/about.html")

@app.get("/work")
def work():  # 함수명 중복 수정
    return FileResponse("templates/work.html")

@app.get("/article")
def article_list():  # 함수명 의미 명확하게 수정
    print(articles_data)
    return templates.TemplateResponse("article.html", {"request": {}, "data": articles_data})

@app.get("/article/{article_number}")
def article_detail(article_number: int):  # 함수명 의미 명확하게 수정
    # 변수 선언
    back_data = None
    front_data = None
    
    # 유효성 검사 추가
    if article_number <= 0 or article_number > len(articles_data):
        raise HTTPException(status_code=404, detail="Article not found")
    
    # HTML 내용 가져오기
    contents = articles_html.get(article_number, "")
    if not contents:
        # HTML 파일이 없으면 직접 로드 시도
        html_path = os.path.join(articles_dir, f"{article_number}.html")
        try:
            with open(html_path, "r", encoding="utf-8") as html_file:
                contents = html_file.read()
                # 캐시에 저장
                articles_html[article_number] = contents
        except FileNotFoundError:
            contents = "<p>HTML 내용이 없습니다.</p>"

    # 이전 글 데이터
    if article_number-2 >= 0:
        back_data = articles_data[article_number-2]

    # 다음 글 데이터
    if article_number < len(articles_data):
        front_data = articles_data[article_number]

    return templates.TemplateResponse(
        "article_one.html", 
        {
            "request": {}, 
            "html": contents,
            "data": articles_data[article_number-1],
            "back": back_data,
            "front": front_data,
            "article_number": article_number,
        }
    )

# 서버 실행 코드 (직접 실행 시에만 작동)
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
