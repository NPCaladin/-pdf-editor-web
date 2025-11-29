# GitHub Desktop 저장소 경로 변경하기

현재 작업 폴더(`C:\Users\master\Desktop\new_aladin`)를 Git 저장소로 설정하는 방법입니다.

---

## 방법 1: GitHub Desktop에서 새 저장소 생성 (추천)

### 1단계: 새 저장소 생성

1. **GitHub Desktop 열기**
   - File → New Repository 클릭

2. **저장소 설정**
   - **Name**: `pdf-editor-web` (원하는 이름)
   - **Description**: `PDF 편집기 웹앱` (선택사항)
   - **Local Path**: `C:\Users\master\Desktop\new_aladin` 
     - 또는 "Choose..." 버튼 클릭하여 폴더 선택
   - **Git ignore**: None (이미 .gitignore 파일이 있음)
   - **License**: None
   - **"Create repository"** 클릭

3. **완료!**
   - 이제 현재 작업 폴더가 Git 저장소가 되었습니다

---

## 방법 2: 기존 저장소 경로 변경

### 2-1. 기존 저장소 제거

1. **GitHub Desktop에서**
   - File → Options → Repositories
   - "Aladin_project" 저장소 선택
   - "Remove" 클릭
   - "Move to Trash" 또는 "Keep" 선택

### 2-2. 새 저장소 생성

위의 "방법 1"을 따라 새 저장소를 생성하세요.

---

## 방법 3: 현재 폴더를 Git 저장소로 초기화 (고급)

만약 GitHub Desktop이 제대로 작동하지 않는다면:

1. **현재 폴더에서 Git 초기화**
   - PowerShell에서:
   ```powershell
   cd C:\Users\master\Desktop\new_aladin
   git init
   ```

2. **GitHub Desktop에서 추가**
   - File → Add Local Repository
   - `C:\Users\master\Desktop\new_aladin` 선택
   - "Add repository" 클릭

---

## 확인

저장소가 제대로 설정되었는지 확인:

1. **GitHub Desktop에서**
   - 왼쪽 "Changes" 탭 확인
   - 다음 파일들이 보여야 합니다:
     - ✅ `app.py`
     - ✅ `requirements-web.txt`
     - ✅ `Procfile`
     - ✅ `runtime.txt`
     - ✅ `templates/` 폴더
     - ✅ `static/` 폴더

2. **파일이 보이지 않으면**
   - GitHub Desktop을 새로고침 (F5)
   - 또는 File → Refresh

---

## 다음 단계

저장소가 설정되면:

1. **커밋**
   - "Summary"에 메시지 입력
   - "Commit to main" 클릭

2. **GitHub에 푸시**
   - "Publish repository" 클릭

3. **Railway 배포**
   - Railway에서 저장소 선택 후 배포

