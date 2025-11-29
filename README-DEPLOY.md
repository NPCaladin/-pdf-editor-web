# PDF 편집기 웹앱 배포 가이드 (한국어)

## 빠른 시작

### Railway로 배포 (가장 쉬움)

1. **GitHub에 코드 업로드**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Railway 배포**
   - https://railway.app 접속
   - GitHub로 로그인
   - "New Project" → "Deploy from GitHub repo"
   - 저장소 선택
   - 자동 배포 완료!

3. **도메인 확인**
   - 배포 완료 후 제공되는 URL로 접속
   - 예: `https://your-app.railway.app`

---

### Render로 배포

1. **GitHub에 코드 업로드** (위와 동일)

2. **Render 설정**
   - https://render.com 접속
   - "New" → "Web Service"
   - GitHub 저장소 연결
   - 설정:
     - **Build Command**: `pip install -r requirements-web.txt`
     - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - "Create Web Service"

---

## 로컬 테스트

```bash
# 패키지 설치
pip install -r requirements-web.txt

# 서버 실행
uvicorn app:app --host 0.0.0.0 --port 8000
```

브라우저에서 http://localhost:8000 접속

---

## 파일 구조

```
.
├── app.py                 # FastAPI 메인 파일
├── requirements-web.txt   # 웹앱용 패키지 목록
├── Procfile              # Railway/Heroku용
├── runtime.txt           # Python 버전
├── templates/
│   └── index.html        # HTML 템플릿
└── static/
    ├── app.js            # JavaScript
    └── style.css         # CSS
```

---

## 문제 해결

**포트 오류가 나는 경우:**
- `Procfile`의 `$PORT` 대신 `8000` 직접 사용

**정적 파일이 로드되지 않는 경우:**
- `static/` 폴더 경로 확인
- `templates/` 폴더 경로 확인

**PDF가 표시되지 않는 경우:**
- 브라우저 콘솔(F12)에서 에러 확인
- PDF.js CDN 링크 확인

