# 베이스 이미지 지정 (공백 없이)
FROM python:3.9-slim

# 작업 디렉터리 설정
WORKDIR /app

# 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY . .

# 앱 포트 노출
EXPOSE 443

# 컨테이너 시작 명령
CMD ["uvicorn", "main:app","--host", "0.0.0.0","--port", "8000","--ssl-keyfile", "/home/system/fastapi-nginx-docker/certs/gyumingim.kro.kr+3-key.pem","--ssl-certfile", "/home/system/fastapi-nginx-docker/certs/gyumingim.kro.kr+3.pem"]
