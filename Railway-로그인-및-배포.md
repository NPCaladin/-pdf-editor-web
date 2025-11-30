# Railway 로그인 및 배포 가이드

## 1단계: Railway 로그인

### GitHub로 로그인

1. **Railway 웹사이트에서**
   - 우측 상단 "Sign in" 버튼 클릭

2. **로그인 방법 선택**
   - "Continue with GitHub" 또는 "Login with GitHub" 클릭
   - GitHub 계정으로 로그인

3. **권한 승인**
   - Railway가 GitHub 저장소에 접근할 수 있도록 권한 승인
   - "Authorize Railway" 클릭

---

## 2단계: 새 프로젝트 생성

### 프로젝트 배포 시작

1. **Railway 대시보드에서**
   - "Deploy a new project" 버튼 클릭
   - 또는 "New Project" 클릭

2. **배포 방법 선택**
   - "Deploy from GitHub repo" 선택
   - GitHub 저장소 목록이 표시됩니다

3. **저장소 선택**
   - 방금 푸시한 `pdf-editor-web` (또는 `new_aladin`) 저장소 선택
   - "Deploy Now" 클릭

---

## 3단계: 배포 설정 확인

### 자동 설정

Railway가 자동으로:
- ✅ 코드 다운로드
- ✅ `requirements-web.txt`에서 패키지 설치
- ✅ `Procfile`에 따라 서버 시작
- ✅ 배포 완료!

### 수동 설정 (필요한 경우)

만약 자동으로 인식하지 못한다면:

1. **Settings 탭에서**
   - Build Command: `pip install -r requirements-web.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

---

## 4단계: 도메인 확인

### 도메인 생성

1. **프로젝트 대시보드에서**
   - "Settings" 탭 클릭

2. **도메인 생성**
   - "Generate Domain" 클릭
   - 또는 "Custom Domain"에서 원하는 도메인 설정

3. **URL 확인**
   - 예: `https://pdf-editor-web-production.up.railway.app`
   - 이 URL을 복사하여 브라우저에서 열기

---

## 5단계: 배포 확인

### 웹앱 테스트

1. **생성된 URL로 접속**
   - 브라우저에서 Railway URL 열기

2. **기능 확인**
   - PDF 파일 업로드
   - 페이지 편집
   - 저장 기능

---

## 문제 해결

### ❌ 로그인 실패

- GitHub 계정 확인
- 브라우저 캐시 삭제 후 다시 시도

### ❌ 배포 실패

- Railway 대시보드 → "View Logs" 클릭
- 에러 메시지 확인
- `requirements-web.txt`, `Procfile` 파일 확인

### ❌ 포트 오류

- `Procfile`에서 `$PORT` 사용 확인
- Railway는 자동으로 포트 할당

---

## 완료! 🎉

배포가 완료되면:
- ✅ Railway URL로 접속 가능
- ✅ PDF 파일 업로드 및 편집 가능
- ✅ 여러 사용자가 동시에 사용 가능
- ✅ 코드 수정 후 GitHub에 푸시하면 자동 재배포!

