# Render 배포 완전 가이드

## 1단계: Render 접속 및 로그인

1. **Render 웹사이트 접속**
   - https://render.com 접속
   - "Get Started for Free" 또는 "Sign Up" 클릭

2. **GitHub로 로그인**
   - "Continue with GitHub" 클릭
   - GitHub 계정으로 로그인
   - 권한 승인

---

## 2단계: 새 Web Service 생성

1. **대시보드에서**
   - "New" 버튼 클릭
   - "Web Service" 선택

2. **GitHub 저장소 연결**
   - "Connect account" 또는 "Connect repository" 클릭
   - GitHub 저장소 목록에서 `NPCaladin/-pdf-editor-web` 선택
   - "Connect" 클릭

3. **서비스 설정**
   - **Name**: `pdf-editor-web` (원하는 이름)
   - **Region**: `Singapore` 또는 가까운 지역 선택
   - **Branch**: `main`
   - **Root Directory**: (비워두기 - 루트 디렉토리)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements-web.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free` 선택

4. **생성**
   - "Create Web Service" 클릭

---

## 3단계: 배포 완료 대기

1. **자동 배포 시작**
   - Render가 자동으로:
     - 코드 다운로드
     - 패키지 설치
     - 서버 시작
     - 배포 완료 (5-10분 소요)

2. **배포 상태 확인**
   - 대시보드에서 배포 진행 상황 확인
   - "Logs" 탭에서 로그 확인

3. **배포 완료**
   - "Live" 상태가 되면 완료
   - 무료 URL 제공
   - 예: `https://pdf-editor-web.onrender.com`

---

## 4단계: 도메인 확인

1. **대시보드에서**
   - 생성된 서비스 클릭
   - "Settings" 탭 확인
   - "Custom Domain"에서 원하는 도메인 설정 가능 (선택사항)

2. **URL 확인**
   - 기본 URL: `https://pdf-editor-web.onrender.com`
   - 이 URL로 접속하여 웹앱 확인

---

## 5단계: 업데이트 배포

코드를 수정한 후:

1. **GitHub에 푸시**
   - GitHub Desktop에서 변경사항 커밋 및 푸시

2. **자동 재배포**
   - Render가 자동으로 재배포 시작
   - GitHub에 푸시하면 자동으로 감지

---

## 문제 해결

### ❌ 배포 실패

- **Logs 확인**: 대시보드 → 서비스 → "Logs" 탭
- **에러 메시지 확인**: 빌드 또는 시작 명령어 확인
- **requirements-web.txt 확인**: 파일이 있는지 확인

### ❌ 포트 오류

- **Start Command 확인**: `$PORT` 환경 변수 사용 확인
- Render는 자동으로 포트 할당

### ❌ 슬리프 모드

- **무료 플랜 제한**: 15분 비활성 시 슬리프 모드
- 첫 요청 시 자동으로 깨어남 (약 30초 소요)
- 유료 플랜으로 업그레이드하면 항상 활성 상태

---

## 완료! 🎉

배포가 완료되면:
- ✅ Render URL로 접속 가능
- ✅ PDF 파일 업로드 및 편집 가능
- ✅ 여러 사용자가 동시에 사용 가능
- ✅ 코드 수정 후 GitHub 푸시하면 자동 재배포

---

## 참고사항

- **무료 플랜 제한**: 15분 비활성 시 슬리프 모드
- **업그레이드**: 필요시 유료 플랜으로 업그레이드 가능
- **도메인**: 커스텀 도메인 설정 가능

