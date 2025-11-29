# Git 설치 가이드 (Windows)

## 방법 1: 공식 사이트에서 다운로드 (추천)

### 1단계: Git 다운로드

1. **브라우저에서 접속**
   - https://git-scm.com/download/win 접속
   - 자동으로 다운로드가 시작됩니다
   - 또는 "64-bit Git for Windows Setup" 클릭

2. **다운로드 확인**
   - 다운로드 폴더에서 `Git-2.xx.x-64-bit.exe` 파일 확인

### 2단계: Git 설치

1. **설치 파일 실행**
   - 다운로드한 `.exe` 파일 더블클릭

2. **설치 과정**
   - "Next" 클릭하여 진행
   - 대부분 기본 설정으로 진행하면 됩니다
   - 중요한 옵션:
     - **Editor**: 기본값 (Vim) 또는 "Use Visual Studio Code" 선택
     - **Default branch name**: "main" (기본값)
     - **PATH environment**: "Git from the command line and also from 3rd-party software" (기본값, 추천)
   - "Install" 클릭

3. **설치 완료**
   - "Finish" 클릭

### 3단계: 설치 확인

1. **새 PowerShell 또는 명령 프롬프트 열기**
   - Windows 키 + R
   - `powershell` 입력
   - Enter

2. **Git 버전 확인**
   ```powershell
   git --version
   ```
   
   **성공하면:**
   ```
   git version 2.xx.x.windows.x
   ```
   
   **여전히 오류가 나면:**
   - PowerShell을 완전히 종료하고 다시 열기
   - 또는 컴퓨터 재시작

---

## 방법 2: winget 사용 (Windows 10/11)

PowerShell을 관리자 권한으로 실행:

```powershell
winget install --id Git.Git -e --source winget
```

설치 후 PowerShell을 다시 열고 확인:
```powershell
git --version
```

---

## 방법 3: Chocolatey 사용 (이미 설치되어 있다면)

PowerShell을 관리자 권한으로 실행:

```powershell
choco install git
```

---

## 설치 후 다음 단계

Git이 설치되면:

1. **PowerShell을 새로 열기** (중요!)

2. **프로젝트 폴더로 이동**
   ```powershell
   cd C:\Users\master\Desktop\new_aladin
   ```

3. **Git 초기화**
   ```powershell
   git init
   ```

4. **이제 정상 작동합니다!**

---

## 문제 해결

### ❌ "git은 내부 또는 외부 명령..." 오류

**해결 방법:**
1. PowerShell을 완전히 종료하고 새로 열기
2. 그래도 안 되면 컴퓨터 재시작
3. 설치 시 PATH 환경 변수 설정 확인

### ❌ 설치 후에도 인식 안 됨

**수동으로 PATH 추가:**
1. Windows 키 → "환경 변수" 검색
2. "시스템 환경 변수 편집" 선택
3. "환경 변수" 버튼 클릭
4. "Path" 선택 → "편집"
5. "새로 만들기" → `C:\Program Files\Git\cmd` 추가
6. 확인 클릭
7. PowerShell 재시작

---

## 빠른 설치 링크

- **공식 다운로드**: https://git-scm.com/download/win
- **직접 다운로드**: https://github.com/git-for-windows/git/releases/latest

