# 지하철 실시간 도착 정보 웹앱

서울시 열린데이터 광장의 지하철 실시간 도착 정보 API를 활용한 Streamlit 웹 애플리케이션입니다.

## 주요 기능

- 🚇 실시간 지하철 도착 정보 조회
- 🔍 역 이름 검색 (기본값: 지축)
- 🔄 새로고침 기능
- 📱 모바일 친화적 UI
- 🎯 상행선/하행선 구분 표시
- 🚨 막차 표시 기능
- ⏱️ 도착 시간 정보 표시

## 설치 및 실행

### 1. 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. API 키 설정

`subway_app.py` 파일 상단의 `API_KEY` 변수에 서울시 열린데이터 API 키를 입력하세요.

```python
API_KEY = "여기에_API_키_입력"
```

서울시 열린데이터 광장에서 API 키를 발급받을 수 있습니다:
- https://data.seoul.go.kr/

### 3. 앱 실행

```bash
streamlit run subway_app.py
```

## 배포

### Streamlit Cloud 배포

1. GitHub에 코드 업로드
2. [Streamlit Cloud](https://streamlit.io/cloud)에 접속
3. "New app" 클릭
4. GitHub 저장소 선택
5. Main file path: `subway_app.py` 입력
6. "Deploy" 클릭

**중요**: API 키는 Streamlit Cloud의 Secrets 기능을 사용하여 안전하게 관리하세요.

### Streamlit Secrets 설정

Streamlit Cloud에서 Secrets를 설정하려면:
1. 앱 설정 → Secrets
2. 다음 형식으로 입력:

```toml
API_KEY = "여기에_API_키_입력"
```

그리고 `subway_app.py`에서 다음과 같이 수정:

```python
import streamlit as st

# Streamlit Secrets에서 API 키 가져오기
if 'API_KEY' in st.secrets:
    API_KEY = st.secrets['API_KEY']
else:
    API_KEY = ""  # 로컬 개발용
```

## 사용 방법

1. 앱 실행 시 기본적으로 '지축' 역 정보가 표시됩니다
2. 검색창에 다른 역 이름을 입력하여 정보를 조회할 수 있습니다
3. 상행선/하행선 탭을 클릭하여 방향별 정보를 확인할 수 있습니다
4. 막차는 빨간색으로 강조 표시됩니다

## 기술 스택

- Python 3.x
- Streamlit
- Requests
- 서울시 열린데이터 광장 API

## 라이선스

이 프로젝트는 개인 사용 목적으로 제작되었습니다.

