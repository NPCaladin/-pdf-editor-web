# Panning 기능 제거 옵션

만약 마우스 드래그 panning이 여전히 부드럽지 않다면, 이 기능을 제거할 수 있습니다.

## 제거 방법

`static/app.js` 파일에서 다음 코드를 삭제하거나 주석 처리:

```javascript
// 마우스 드래그로 스크롤 (panning) 관련 코드 전체 삭제
// 약 33번째 줄부터 100번째 줄까지
```

또는 CSS에서 커서 스타일만 제거:

```css
.pdf-viewer-container {
    cursor: default; /* grab 대신 default */
}
```

## 대안

- 마우스 휠 스크롤: 정상 작동 중
- 키보드 화살표 키: 추가 가능
- 스크롤바 사용: 기본 제공

