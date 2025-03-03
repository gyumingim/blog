from fastapi import FastAPI
from jinja2 import Environment, FileSystemLoader
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import json
import os
import re

templates = Jinja2Templates(directory="templates")

# 모든 JSON 파일을 순서대로 읽기
articles_dir = "./templates/articles"
articles_data = []

# 숫자 순서대로 정렬하기 위한 함수
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

# 디렉토리에서 모든 JSON 파일 가져오기
json_files = [f for f in os.listdir(articles_dir) if f.endswith('.json')]
# 파일명 기준으로 정렬 (1.json, 2.json, ... 10.json 순서로)
json_files.sort(key=natural_sort_key)

# 각 JSON 파일 읽기
for json_file in json_files:
    file_path = os.path.join(articles_dir, json_file)
    with open(file_path, "r", encoding="utf-8") as file:
        article_data = json.load(file)
        articles_data.append(article_data)

print(f"총 {len(articles_data)}개의 글을 불러왔습니다.\n\n\n\n")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return FileResponse(f"templates/about.html")

@app.get("/work")
def root():
    return FileResponse(f"templates/work.html")

@app.get("/article")
def article():
    return templates.TemplateResponse("article.html", {"request": {}, "data":articles_data})

@app.get("/article/{article_number}")
def article(article_number: int):

    # 변수 선언
    back_data = None
    front_data = None

    # 유효성 검사
    if article_number-2 >= 0:
        back_data = articles_data[article_number-2]

    if article_number < len(articles_data):
        front_data = articles_data[article_number]

    return templates.TemplateResponse(
        "article_one.html", 
        {
            "request": {}, 
            "data":articles_data[article_number-1],
            "back":back_data,
            "front":front_data,
            "article_number":article_number,
        }
    )
