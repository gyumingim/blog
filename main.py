from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # 이 부분이 누락되었습니다
from jinja2 import Environment, FileSystemLoader
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import json
import uvicorn

templates = Jinja2Templates(directory="templates")

# 모든 JSON 파일을 순서대로 읽기
articles_dir = "./templates/articles"
articles_data = []

# 숫자 순서대로 정렬하기 위한 함수
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

try:
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

    logger.info(f"총 {len(articles_data)}개의 글을 불러왔습니다.")
except Exception as e:
    logger.error(f"글 로딩 중 오류 발생: {str(e)}")

app = FastAPI()

# CORS 설정 - 배포 시 실제 도메인으로 변경 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용하도록 변경 (예: ["https://yourdomain.com"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 설정 (캐싱 헤더 추가)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
def root():
    return FileResponse("templates/about.html")

@app.get("/work")
def work():  # 함수명 중복 수정
    return FileResponse("templates/work.html")

@app.get("/article")
def article_list():  # 함수명 의미 명확하게 수정
    return templates.TemplateResponse("article.html", {"request": {}, "data": articles_data})

@app.get("/article/{article_number}")
def article_detail(article_number: int):  # 함수명 의미 명확하게 수정
    # 유효성 검사 강화
    if article_number <= 0 or article_number > len(articles_data):
        raise HTTPException(status_code=404, detail="Article not found")
    
    # 변수 선언
    back_data = None
    front_data = None

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
