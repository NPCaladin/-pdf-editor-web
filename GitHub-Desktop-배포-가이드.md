# GitHub Desktop으로 Railway 배포하기 (가장 쉬운 방법!)

GitHub Desktop이 이미 설치되어 있으므로, 명령줄 없이 GUI로 배포할 수 있습니다!

---

## 1단계: GitHub Desktop에서 저장소 준비

### 1-1. 현재 저장소 확인

GitHub Desktop에서 이미 "Aladin_project" 저장소가 열려있습니다.

**옵션 1: 기존 저장소 사용**
- 현재 "Aladin_project" 저장소를 그대로 사용

**옵션 2: 새 저장소 생성 (추천)**
- GitHub Desktop에서:
  - File → New Repository
  - Name: `pdf-editor-web`
  - Local Path: `C:\Users\master\Desktop\new_aladin`
  - "Create repository" 클릭

---

## 2단계: 파일 추가 및 커밋

### 2-1. 필요한 파일 확인

GitHub Desktop의 "Changes" 탭에서 다음 파일들이 보여야 합니다:

**필수 파일:**
- ✅ `app.py`
- ✅ `requirements-web.txt`
- ✅ `Procfile`
- ✅ `runtime.txt`
- ✅ `.gitignore`
- ✅ `templates/` 폴더
- ✅ `static/` 폴더

**제외할 파일 (이미 .gitignore에 있음):**
- ❌ `temp/` 폴더
- ❌ `build/` 폴더
- ❌ `dist/` 폴더
- ❌ `main.py` (데스크탑 앱용, 웹앱에서는 불필요)

### 2-2. 파일 추가

1. **GitHub Desktop에서**
   - 왼쪽 "Changes" 탭 확인
   - 보이지 않는 파일이 있다면:
     - File → Add Local Repository
     - 또는 파일 탐색기에서 파일을 복사

2. **수동으로 파일 추가 (필요한 경우)**
   - 파일 탐색기에서 `C:\Users\master\Desktop\new_aladin` 열기
   - 필요한 파일들을 확인

### 2-3. 커밋

1. **GitHub Desktop 하단에서**
   - "Summary"에 메시지 입력: `Initial commit: PDF Editor Web App`
   - "Description" (선택사항): `PDF 편집기 웹앱 배포`
   - "Commit to main" 클릭

---

## 3단계: GitHub에 푸시

### 3-1. GitHub 저장소 생성 (아직 없다면)

1. **GitHub 웹사이트에서**
   - https://github.com 접속
   - 로그인
   - 우측 상단 "+" → "New repository"
   - Repository name: `pdf-editor-web`
   - "Add a README file" 체크 해제
   - "Create repository" 클릭

### 3-2. GitHub Desktop에서 푸시

1. **GitHub Desktop 상단에서**
   - "Publish repository" 버튼 클릭
   - 또는 Repository → Push origin

2. **저장소 연결 (처음인 경우)**
   - "Publish repository" 클릭
   - Repository name: `pdf-editor-web`
   - "Keep this code private" 체크 해제 (Public으로 공개)
   - "Publish repository" 클릭

3. **푸시 완료**
   - GitHub에 업로드 완료!

---

## 4단계: Railway 배포

### 4-1. Railway 계정 생성

1. **Railway 접속**
   - https://railway.app 접속
   - "Start a New Project" 클릭

2. **로그인**
   - "Login with GitHub" 클릭
   - GitHub 계정으로 로그인
   - 권한 승인

### 4-2. 프로젝트 배포

1. **새 프로젝트 생성**
   - "New Project" 클릭
   - "Deploy from GitHub repo" 선택

2. **저장소 선택**
   - 방금 푸시한 `pdf-editor-web` 저장소 선택
   - "Deploy Now" 클릭

3. **자동 배포**
   - Railway가 자동으로:
     - ✅ 코드 다운로드
     - ✅ 패키지 설치
     - ✅ 서버 시작
     - ✅ 배포 완료!

### 4-3. 도메인 확인

1. **배포 완료 후**
   - 프로젝트 대시보드 → "Settings" 탭
   - "Generate Domain" 클릭
   - 생성된 URL 확인

2. **웹앱 접속**
   - 예: `https://pdf-editor-web-production.up.railway.app`
   - 이 URL로 접속하여 확인!

---

## 5단계: 업데이트 배포

코드를 수정한 후:

1. **GitHub Desktop에서**
   - 변경된 파일 확인
   - "Summary"에 메시지 입력
   - "Commit to main" 클릭
   - "Push origin" 클릭

2. **Railway 자동 재배포**
   - GitHub에 푸시하면 Railway가 자동으로 재배포!

---

## 문제 해결

### ❌ 파일이 Changes에 안 보임

**해결:**
- File → Add Local Repository
- 또는 파일 탐색기에서 파일 확인

### ❌ 푸시 실패

**해결:**
- GitHub 계정 확인
- Repository → Repository Settings → Remote 확인

### ❌ Railway 배포 실패

**해결:**
- Railway 대시보드 → View Logs 확인
- `requirements-web.txt`, `Procfile` 파일 확인

---

## 완료! 🎉

이제 웹앱이 배포되었습니다!
- Railway URL로 접속
- PDF 파일 업로드 및 편집 가능
- 여러 사용자가 동시에 사용 가능

