# Railway 배포 가이드 (단계별)

## 1단계: GitHub 저장소 준비

### 1-1. GitHub 계정 및 저장소 생성

1. **GitHub 계정이 없다면**
   - https://github.com 접속
   - "Sign up" 클릭하여 계정 생성

2. **새 저장소 생성**
   - GitHub 로그인 후 우측 상단 "+" → "New repository" 클릭
   - Repository name: `pdf-editor-web` (원하는 이름)
   - Public 또는 Private 선택
   - "Add a README file" 체크 해제 (이미 파일이 있으므로)
   - "Create repository" 클릭

### 1-2. 로컬에서 Git 초기화 및 업로드

**Windows PowerShell 또는 명령 프롬프트에서 실행:**

```bash
# 현재 폴더로 이동 (이미 해당 폴더에 있다면 생략)
cd C:\Users\master\Desktop\new_aladin

# Git 초기화
git init

# 모든 파일 추가 (필요한 파일만)
git add app.py
git add requirements-web.txt
git add Procfile
git add runtime.txt
git add .gitignore
git add templates/
git add static/
git add README-DEPLOY.md

# 커밋
git commit -m "Initial commit: PDF Editor Web App"

# GitHub 저장소 연결 (YOUR_USERNAME과 YOUR_REPO_NAME을 실제 값으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 브랜치 이름을 main으로 설정
git branch -M main

# GitHub에 업로드
git push -u origin main
```

**예시:**
```bash
git remote add origin https://github.com/yourusername/pdf-editor-web.git
```

---

## 2단계: Railway 배포

### 2-1. Railway 계정 생성

1. **Railway 접속**
   - https://railway.app 접속
   - "Start a New Project" 클릭

2. **로그인**
   - "Login with GitHub" 클릭
   - GitHub 계정으로 로그인
   - 권한 승인

### 2-2. 프로젝트 배포

1. **새 프로젝트 생성**
   - "New Project" 클릭
   - "Deploy from GitHub repo" 선택

2. **저장소 선택**
   - 방금 만든 GitHub 저장소 선택
   - "Deploy Now" 클릭

3. **자동 배포**
   - Railway가 자동으로:
     - 코드 다운로드
     - `requirements-web.txt`에서 패키지 설치
     - `Procfile`에 따라 서버 시작
     - 배포 완료!

### 2-3. 도메인 확인

1. **배포 완료 후**
   - 프로젝트 대시보드에서 "Settings" 탭 클릭
   - "Generate Domain" 클릭
   - 또는 "Custom Domain"에서 원하는 도메인 설정

2. **URL 확인**
   - 예: `https://pdf-editor-web-production.up.railway.app`
   - 이 URL로 접속하면 웹앱 사용 가능!

---

## 3단계: 환경 변수 설정 (선택사항)

필요한 경우:

1. Railway 대시보드에서 프로젝트 선택
2. "Variables" 탭 클릭
3. 환경 변수 추가 (현재는 필요 없음)

---

## 4단계: 업데이트 배포

코드를 수정한 후:

```bash
# 변경사항 커밋
git add .
git commit -m "Update: 설명"

# GitHub에 푸시
git push

# Railway가 자동으로 재배포!
```

---

## 문제 해결

### Git 업로드 오류
- GitHub Personal Access Token 필요할 수 있음
- Settings → Developer settings → Personal access tokens → Generate new token

### 배포 실패
- `requirements-web.txt` 파일 확인
- `Procfile` 내용 확인
- Railway 로그 확인 (View Logs)

### 포트 오류
- `Procfile`에서 `$PORT` 사용 확인
- Railway는 자동으로 포트 할당

---

## 완료!

배포가 완료되면:
- Railway에서 제공하는 URL로 접속
- PDF 파일 업로드 및 편집 가능
- 여러 사용자가 동시에 사용 가능

