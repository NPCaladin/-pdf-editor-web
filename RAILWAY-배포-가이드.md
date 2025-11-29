# Railway 배포 완전 가이드 (한국어)

## 📋 준비사항

1. GitHub 계정 (없으면 생성 필요)
2. Git 설치 (아래 참고)
3. Railway 계정 (GitHub로 로그인)

---

## 1단계: Git 설치 (아직 설치 안 했다면)

### Windows에서 Git 설치

1. **Git 다운로드**
   - https://git-scm.com/download/win 접속
   - 자동으로 다운로드 시작됨
   - 또는 "Download for Windows" 클릭

2. **설치**
   - 다운로드한 파일 실행
   - 기본 설정으로 "Next" 클릭
   - 설치 완료

3. **설치 확인**
   - PowerShell 또는 명령 프롬프트 열기
   - 다음 명령어 입력:
   ```bash
   git --version
   ```
   - 버전이 나오면 설치 완료!

---

## 2단계: GitHub 저장소 생성

### 2-1. GitHub 계정 생성 (없다면)

1. https://github.com 접속
2. "Sign up" 클릭
3. 이메일, 비밀번호 입력하여 계정 생성

### 2-2. 새 저장소 만들기

1. **GitHub 로그인 후**
   - 우측 상단 "+" 아이콘 클릭
   - "New repository" 선택

2. **저장소 설정**
   - Repository name: `pdf-editor-web` (원하는 이름)
   - Description: `PDF 편집기 웹앱` (선택사항)
   - Public 또는 Private 선택
   - **"Add a README file" 체크 해제** (이미 파일이 있으므로)
   - "Create repository" 클릭

3. **저장소 URL 복사**
   - 생성된 페이지에서 URL 복사
   - 예: `https://github.com/yourusername/pdf-editor-web.git`

---

## 3단계: 로컬 파일을 GitHub에 업로드

### 3-1. PowerShell 또는 명령 프롬프트 열기

- Windows 키 + R
- `powershell` 또는 `cmd` 입력
- Enter

### 3-2. 프로젝트 폴더로 이동

```bash
cd C:\Users\master\Desktop\new_aladin
```

### 3-3. Git 초기화 및 업로드

**다음 명령어를 순서대로 실행:**

```bash
# 1. Git 초기화
git init

# 2. 필요한 파일만 추가
git add app.py
git add requirements-web.txt
git add Procfile
git add runtime.txt
git add .gitignore
git add templates/
git add static/
git add README-DEPLOY.md
git add RAILWAY-배포-가이드.md

# 3. 커밋 (변경사항 저장)
git commit -m "Initial commit: PDF Editor Web App"

# 4. GitHub 저장소 연결
# 아래 YOUR_USERNAME과 YOUR_REPO_NAME을 실제 값으로 변경하세요!
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 예시:
# git remote add origin https://github.com/john/pdf-editor-web.git

# 5. 브랜치 이름을 main으로 설정
git branch -M main

# 6. GitHub에 업로드
git push -u origin main
```

**주의사항:**
- `git push` 실행 시 GitHub 사용자명과 비밀번호(또는 Personal Access Token) 입력 필요
- Personal Access Token이 필요하면 아래 참고

### 3-4. Personal Access Token 생성 (필요한 경우)

GitHub에서 비밀번호 대신 토큰 사용:

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" 클릭
3. Note: `Railway Deploy` 입력
4. Expiration: 원하는 기간 선택
5. Scopes: `repo` 체크
6. "Generate token" 클릭
7. **토큰 복사** (한 번만 보여줌!)
8. `git push` 시 비밀번호 대신 이 토큰 입력

---

## 4단계: Railway 배포

### 4-1. Railway 계정 생성

1. **Railway 접속**
   - https://railway.app 접속

2. **로그인**
   - "Start a New Project" 또는 "Login" 클릭
   - "Login with GitHub" 선택
   - GitHub 계정으로 로그인
   - 권한 승인

### 4-2. 프로젝트 배포

1. **새 프로젝트 생성**
   - 대시보드에서 "New Project" 클릭
   - "Deploy from GitHub repo" 선택

2. **저장소 선택**
   - 방금 만든 GitHub 저장소 선택
   - "Deploy Now" 클릭

3. **자동 배포 시작**
   - Railway가 자동으로:
     - ✅ 코드 다운로드
     - ✅ `requirements-web.txt`에서 패키지 설치
     - ✅ `Procfile`에 따라 서버 시작
     - ✅ 배포 완료!

### 4-3. 도메인 확인

1. **배포 완료 후**
   - 프로젝트 대시보드에서 "Settings" 탭 클릭
   - "Generate Domain" 클릭
   - 또는 "Custom Domain"에서 원하는 도메인 설정

2. **URL 확인**
   - 예: `https://pdf-editor-web-production.up.railway.app`
   - 이 URL을 복사하여 브라우저에서 열기
   - 웹앱이 정상 작동하는지 확인!

---

## 5단계: 업데이트 배포

코드를 수정한 후:

```bash
# 변경사항 추가
git add .

# 커밋
git commit -m "Update: 설명"

# GitHub에 푸시
git push

# Railway가 자동으로 재배포!
```

---

## 문제 해결

### ❌ Git 업로드 오류

**오류: "fatal: could not read Username"**
- Personal Access Token 사용 필요
- 위의 "3-4. Personal Access Token 생성" 참고

**오류: "remote origin already exists"**
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### ❌ Railway 배포 실패

**로그 확인:**
- Railway 대시보드 → 프로젝트 → "View Logs" 클릭
- 에러 메시지 확인

**일반적인 문제:**
- `requirements-web.txt` 파일이 있는지 확인
- `Procfile` 내용 확인 (`web: uvicorn app:app --host 0.0.0.0 --port $PORT`)
- `app.py` 파일이 있는지 확인

### ❌ 포트 오류

- `Procfile`에서 `$PORT` 사용 확인
- Railway는 자동으로 포트 할당

---

## 완료! 🎉

배포가 완료되면:
- ✅ Railway에서 제공하는 URL로 접속
- ✅ PDF 파일 업로드 및 편집 가능
- ✅ 여러 사용자가 동시에 사용 가능
- ✅ 코드 수정 후 `git push`만 하면 자동 재배포

---

## 추가 팁

1. **커스텀 도메인**
   - Railway Settings → Custom Domain에서 설정 가능

2. **환경 변수**
   - Settings → Variables에서 추가 가능 (현재는 필요 없음)

3. **로그 확인**
   - 프로젝트 → View Logs에서 실시간 로그 확인

4. **비용**
   - Railway 무료 티어: $5 크레딧/월
   - 소규모 사용에는 충분

