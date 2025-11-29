# PDF 편집기 웹앱 배포 가이드

이 문서는 PDF 편집기 웹앱을 다양한 플랫폼에 배포하는 방법을 안내합니다.

## 배포 옵션

### 1. Railway (추천 - 가장 간단)

1. **Railway 계정 생성**
   - https://railway.app 접속
   - GitHub 계정으로 로그인

2. **프로젝트 배포**
   - "New Project" 클릭
   - "Deploy from GitHub repo" 선택
   - GitHub 저장소 연결
   - 자동으로 배포 시작

3. **환경 변수 설정 (필요시)**
   - Settings → Variables에서 환경 변수 추가

4. **도메인 설정**
   - Settings → Domains에서 커스텀 도메인 설정 가능

**장점**: 무료 티어 제공, 자동 배포, 간단한 설정

---

### 2. Render

1. **Render 계정 생성**
   - https://render.com 접속
   - GitHub 계정으로 로그인

2. **새 Web Service 생성**
   - "New" → "Web Service" 선택
   - GitHub 저장소 연결
   - 설정:
     - **Name**: pdf-editor (원하는 이름)
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements-web.txt`
     - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
     - **Plan**: Free

3. **배포**
   - "Create Web Service" 클릭
   - 자동으로 빌드 및 배포 시작

**장점**: 무료 티어, 자동 HTTPS, 쉬운 설정

---

### 3. PythonAnywhere

1. **계정 생성**
   - https://www.pythonanywhere.com 접속
   - 무료 계정 생성

2. **파일 업로드**
   - Files 탭에서 파일 업로드:
     - `app.py`
     - `requirements-web.txt`
     - `templates/` 폴더
     - `static/` 폴더

3. **가상환경 설정**
   - Bash 콘솔에서:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 pdf-editor
   pip install -r requirements-web.txt
   ```

4. **Web App 설정**
   - Web 탭으로 이동
   - "Add a new web app" 클릭
   - Manual configuration 선택
   - Python 3.10 선택
   - WSGI 설정 파일 편집:
   ```python
   import sys
   path = '/home/yourusername/path/to/app'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app
   application = app
   ```

5. **Static files 설정**
   - Static files 섹션에서:
     - URL: `/static`
     - Directory: `/home/yourusername/path/to/app/static`

**장점**: 무료 티어, Python 전용, 쉬운 파일 관리

---

### 4. Heroku

1. **Heroku CLI 설치**
   - https://devcenter.heroku.com/articles/heroku-cli

2. **로그인 및 앱 생성**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **배포**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

**참고**: Heroku는 무료 티어가 종료되었습니다.

---

## 로컬 테스트

배포 전에 로컬에서 테스트:

```bash
# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements-web.txt

# 앱 실행
uvicorn app:app --host 0.0.0.0 --port 8000
```

브라우저에서 http://localhost:8000 접속

---

## 주의사항

1. **임시 파일 관리**
   - `temp/` 폴더는 서버에 생성됩니다
   - 주기적으로 정리하는 스크립트를 추가하는 것을 권장합니다

2. **파일 크기 제한**
   - 무료 티어는 파일 크기 제한이 있을 수 있습니다
   - 큰 PDF 파일 업로드 시 주의

3. **보안**
   - 프로덕션 환경에서는 HTTPS 사용 필수
   - 파일 업로드 크기 제한 설정 권장

4. **환경 변수**
   - 필요시 `.env` 파일 사용 (python-dotenv 패키지 추가)

---

## 문제 해결

### 포트 오류
- `$PORT` 환경 변수가 없는 경우: `--port 8000` 직접 지정

### 정적 파일 로드 실패
- `static/` 폴더 경로 확인
- FastAPI의 `StaticFiles` 설정 확인

### PDF 로드 실패
- PDF.js CDN 링크 확인
- 브라우저 콘솔에서 에러 확인

