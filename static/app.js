// PDF.js 설정
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

// 모바일 감지 및 최적화
function detectMobile() {
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
        || window.innerWidth <= 768;
    
    if (isMobile) {
        document.body.classList.add('mobile-view');
        // 모바일 메뉴 토글 버튼을 메뉴바 안에 추가
        if (!document.getElementById('menu-toggle-btn')) {
            const menuLeft = document.querySelector('.menu-left');
            if (menuLeft) {
                const menuToggle = document.createElement('button');
                menuToggle.id = 'menu-toggle-btn';
                menuToggle.className = 'menu-toggle';
                menuToggle.innerHTML = '☰';
                menuToggle.setAttribute('aria-label', '메뉴 열기');
                
                // 메뉴 토글 함수
                const toggleMenu = (e) => {
                    e.stopPropagation();
                    const leftPanel = document.querySelector('.left-panel');
                    const isOpen = leftPanel.classList.contains('show');
                    
                    if (isOpen) {
                        leftPanel.classList.remove('show');
                        menuToggle.innerHTML = '☰';
                        menuToggle.setAttribute('aria-label', '메뉴 열기');
                    } else {
                        leftPanel.classList.add('show');
                        menuToggle.innerHTML = '×';
                        menuToggle.setAttribute('aria-label', '메뉴 닫기');
                    }
                };
                
                menuToggle.addEventListener('click', toggleMenu);
                // 메뉴바의 첫 번째 요소로 추가
                menuLeft.insertBefore(menuToggle, menuLeft.firstChild);
                
                // 좌측 패널 외부 클릭 시 닫기
                document.addEventListener('click', (e) => {
                    const leftPanel = document.querySelector('.left-panel');
                    const menuToggle = document.getElementById('menu-toggle-btn');
                    if (leftPanel && leftPanel.classList.contains('show')) {
                        if (!leftPanel.contains(e.target) && e.target !== menuToggle) {
                            leftPanel.classList.remove('show');
                            if (menuToggle) {
                                menuToggle.innerHTML = '☰';
                                menuToggle.setAttribute('aria-label', '메뉴 열기');
                            }
                        }
                    }
                });
            }
        }
    }
    
    return isMobile;
}

// 페이지 로드 시 모바일 감지
const isMobileDevice = detectMobile();

// 리사이즈 이벤트로 모바일 감지 업데이트
window.addEventListener('resize', () => {
    const isMobile = window.innerWidth <= 768;
    if (isMobile && !document.body.classList.contains('mobile-view')) {
        document.body.classList.add('mobile-view');
        if (!document.getElementById('menu-toggle-btn')) {
            const menuLeft = document.querySelector('.menu-left');
            if (menuLeft) {
                const menuToggle = document.createElement('button');
                menuToggle.id = 'menu-toggle-btn';
                menuToggle.className = 'menu-toggle';
                menuToggle.innerHTML = '☰';
                menuToggle.setAttribute('aria-label', '메뉴 열기');
                
                // 메뉴 토글 함수
                const toggleMenu = (e) => {
                    e.stopPropagation();
                    const leftPanel = document.querySelector('.left-panel');
                    const isOpen = leftPanel.classList.contains('show');
                    
                    if (isOpen) {
                        leftPanel.classList.remove('show');
                        menuToggle.innerHTML = '☰';
                        menuToggle.setAttribute('aria-label', '메뉴 열기');
                    } else {
                        leftPanel.classList.add('show');
                        menuToggle.innerHTML = '×';
                        menuToggle.setAttribute('aria-label', '메뉴 닫기');
                    }
                };
                
                menuToggle.addEventListener('click', toggleMenu);
                menuLeft.insertBefore(menuToggle, menuLeft.firstChild);
            }
        }
    } else if (!isMobile && document.body.classList.contains('mobile-view')) {
        document.body.classList.remove('mobile-view');
        const leftPanel = document.querySelector('.left-panel');
        if (leftPanel) leftPanel.classList.remove('show');
        const menuToggle = document.getElementById('menu-toggle-btn');
        if (menuToggle) menuToggle.remove();
    }
});

// 전역 변수
let tabs = {}; // {tabId: {fileId, pdf, pageCount, currentPage, scale, filename}}
let currentTabId = null;
let tabCounter = 0;

// DOM 요소
const fileInput = document.getElementById('file-input');
const addPageFileInput = document.getElementById('add-page-file-input');
const mergeFileInput = document.getElementById('merge-file-input');
const pageList = document.getElementById('page-list');
const pdfContainer = document.getElementById('pdf-container');
const tabContainer = document.getElementById('tab-container');

// 이벤트 리스너
document.getElementById('btn-open').addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileUpload);
document.getElementById('btn-merge').addEventListener('click', handleMergeClick);
document.getElementById('btn-undo').addEventListener('click', undoLastAction);
document.getElementById('btn-save').addEventListener('click', savePdf);
document.getElementById('btn-save-as').addEventListener('click', savePdfAs);
document.getElementById('btn-zoom-in').addEventListener('click', () => zoom(1.2));
document.getElementById('btn-zoom-out').addEventListener('click', () => zoom(0.8));
document.getElementById('btn-move-up').addEventListener('click', movePageUp);
document.getElementById('btn-move-down').addEventListener('click', movePageDown);
document.getElementById('btn-delete-page').addEventListener('click', deletePage);
document.getElementById('btn-add-pages').addEventListener('click', () => addPageFileInput.click());
addPageFileInput.addEventListener('change', handleAddPages);
mergeFileInput.addEventListener('change', handleMergeFiles);

// 마우스 드래그 panning 기능 제거 - 마우스 휠 스크롤만 사용

// 스크롤 이벤트 (휠)
pdfContainer.addEventListener('wheel', (e) => {
    // 스크롤 허용
}, { passive: true });

// 파일 업로드 (새 탭 생성)
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    await createNewTab(file);
    fileInput.value = ''; // 같은 파일 다시 선택 가능하도록
}

// 새 탭 생성
async function createNewTab(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        const tabId = `tab_${tabCounter++}`;
        
        tabs[tabId] = {
            fileId: data.file_id,
            pageCount: data.page_count,
            currentPage: 1,
            scale: 1.0,
            filename: data.filename,
            pdf: null
        };

        // 탭 UI 생성
        createTabUI(tabId, data.filename);
        
        // 탭 전환
        switchTab(tabId);
        
        // PDF 로드
        await loadPdf(tabId);
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('파일 업로드 실패');
    }
}

// 탭 UI 생성
function createTabUI(tabId, filename) {
    const tab = document.createElement('div');
    tab.className = 'tab';
    tab.dataset.tabId = tabId;
    tab.innerHTML = `
        <span class="tab-label">${filename}</span>
        <button class="tab-close" onclick="closeTab('${tabId}', event)">×</button>
    `;
    tab.addEventListener('click', (e) => {
        if (!e.target.classList.contains('tab-close')) {
            switchTab(tabId);
        }
    });
    
    tabContainer.appendChild(tab);
}

// 탭 전환
async function switchTab(tabId) {
    if (!tabs[tabId]) return;
    
    // 기존 observer 정리
    if (intersectionObserver) {
        intersectionObserver.disconnect();
        intersectionObserver = null;
    }
    
    // 현재 탭 설정
    const previousTabId = currentTabId;
    currentTabId = tabId;
    
    // 탭 활성화
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    const tabElement = document.querySelector(`[data-tab-id="${tabId}"]`);
    if (tabElement) {
        tabElement.classList.add('active');
    }
    
    // PDF 로드 및 표시
    if (!tabs[tabId].pdf) {
        await loadPdf(tabId);
    } else {
        await renderAllPages(tabId);
    }
    
    // 현재 탭이 여전히 활성인지 확인 후 업데이트
    if (currentTabId === tabId && tabs[tabId]) {
        updatePageList(tabId);
        updateZoomLabel(tabId);
        enableButtons();
        updateUndoButton();
        // 스크롤 observer 재설정
        setupScrollObserver(tabId);
    }
}

// 탭 닫기
function closeTab(tabId, event) {
    event.stopPropagation();
    
    if (Object.keys(tabs).length <= 1) {
        alert('최소 하나의 탭은 열려있어야 합니다.');
        return;
    }
    
    delete tabs[tabId];
    document.querySelector(`[data-tab-id="${tabId}"]`).remove();
    
    // 다른 탭으로 전환
    const remainingTabs = Object.keys(tabs);
    if (remainingTabs.length > 0) {
        switchTab(remainingTabs[0]);
    } else {
        // 모든 탭이 닫힌 경우
        pdfContainer.innerHTML = '';
        pageList.innerHTML = '';
        document.getElementById('btn-save').disabled = true;
        document.getElementById('btn-save-as').disabled = true;
        document.getElementById('btn-merge').disabled = false;
    }
}

// PDF 로드
async function loadPdf(tabId) {
    if (!tabs[tabId]) return;

    try {
        const response = await fetch(`/api/pdf/${tabs[tabId].fileId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const arrayBuffer = await response.arrayBuffer();
        
        const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
        tabs[tabId].pdf = await loadingTask.promise;
        
        await renderAllPages(tabId);
    } catch (error) {
        console.error('Error loading PDF:', error);
        // 에러가 발생해도 합치기는 완료되었을 수 있으므로 조용히 처리
        // alert('PDF 로드 실패');
    }
}

// 모든 페이지 렌더링 (성능 최적화)
async function renderAllPages(tabId) {
    if (!tabs[tabId] || !tabs[tabId].pdf) return;

    const container = pdfContainer;
    container.innerHTML = '';
    
    const tab = tabs[tabId];
    const pageCanvases = [];

    // 순차 렌더링으로 초기 로딩 속도 개선
    // 첫 몇 페이지만 먼저 렌더링하고 나머지는 지연 로딩
    const initialPages = Math.min(3, tab.pageCount);
    
    for (let pageNum = 1; pageNum <= initialPages; pageNum++) {
        // 탭이 변경되었는지 확인
        if (tabId !== currentTabId || !tabs[tabId]) return;
        await renderPage(tabId, pageNum, container, pageCanvases);
    }
    
    // 나머지 페이지는 백그라운드에서 렌더링
    if (tab.pageCount > initialPages) {
        setTimeout(async () => {
            // 탭이 변경되었는지 확인
            if (tabId !== currentTabId || !tabs[tabId]) return;
            
            for (let pageNum = initialPages + 1; pageNum <= tab.pageCount; pageNum++) {
                if (tabId !== currentTabId || !tabs[tabId]) return;
                await renderPage(tabId, pageNum, container, pageCanvases);
            }
            // 렌더링 완료 후 observer 재설정 (현재 탭인지 확인)
            if (tabId === currentTabId && tabs[tabId]) {
                setupScrollObserver(tabId);
            }
        }, 100);
    }

    // 페이지 클릭 이벤트 (이벤트 위임으로 최적화 - 한 번만 등록)
    if (!container.dataset.clickListenerAdded) {
        container.addEventListener('click', (e) => {
            const canvas = e.target.closest('canvas[data-page-num]');
            if (canvas && currentTabId && tabs[currentTabId]) {
                const pageNum = parseInt(canvas.dataset.pageNum);
                tabs[currentTabId].currentPage = pageNum;
                updatePageList(currentTabId);
                canvas.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
        container.dataset.clickListenerAdded = 'true';
    }

    // 스크롤 이벤트로 현재 페이지 감지 (현재 탭인지 확인)
    if (tabId === currentTabId && tabs[tabId]) {
        setupScrollObserver(tabId);
    }
}

// 개별 페이지 렌더링 (성능 최적화)
async function renderPage(tabId, pageNum, container, pageCanvases) {
    const tab = tabs[tabId];
    const page = await tab.pdf.getPage(pageNum);
    
    // 모바일에서 스케일 조정
    let scale = tab.scale;
    if (isMobileDevice) {
        // 모바일에서는 기본 스케일을 화면 크기에 맞게 조정
        const baseViewport = page.getViewport({ scale: 1.0 });
        const maxWidth = window.innerWidth - 20;
        if (baseViewport.width > maxWidth) {
            scale = (maxWidth / baseViewport.width) * tab.scale;
        }
    }
    
    const viewport = page.getViewport({ scale: scale });

    const pageCanvas = document.createElement('canvas');
    const pageCtx = pageCanvas.getContext('2d');
    pageCanvas.height = viewport.height;
    pageCanvas.width = viewport.width;
    pageCanvas.style.display = 'block';
    pageCanvas.style.margin = '10px auto';
    pageCanvas.style.border = '1px solid #ccc';
    pageCanvas.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
    pageCanvas.className = 'pdf-page-canvas';
    pageCanvas.dataset.pageNum = pageNum;
    
    // 모바일에서 캔버스 크기 조정
    if (isMobileDevice) {
        pageCanvas.style.maxWidth = '100%';
        pageCanvas.style.height = 'auto';
    }

    const renderContext = {
        canvasContext: pageCtx,
        viewport: viewport
    };

    await page.render(renderContext).promise;
    container.appendChild(pageCanvas);
    pageCanvases.push(pageCanvas);
}

// 스크롤 감지 및 현재 페이지 업데이트 (성능 최적화)
let scrollTimeout = null;
let intersectionObserver = null;

function setupScrollObserver(tabId) {
    // 현재 탭이 아니면 observer 설정하지 않음
    if (!tabs[tabId] || tabId !== currentTabId) return;
    
    // 기존 observer 제거
    if (intersectionObserver) {
        intersectionObserver.disconnect();
        intersectionObserver = null;
    }

    const tab = tabs[tabId];
    if (!tab) return;
    
    const canvases = pdfContainer.querySelectorAll('canvas[data-page-num]');
    if (canvases.length === 0) return;
    
    // IntersectionObserver로 현재 보이는 페이지 감지
    intersectionObserver = new IntersectionObserver((entries) => {
        // 현재 탭이 변경되었으면 무시
        if (tabId !== currentTabId || !tabs[tabId]) return;
        
        // 가장 많이 보이는 페이지 찾기
        let maxVisible = 0;
        let detectedPage = tab.currentPage;
        
        entries.forEach(entry => {
            if (entry.isIntersecting && entry.intersectionRatio > maxVisible) {
                maxVisible = entry.intersectionRatio;
                const pageNum = parseInt(entry.target.dataset.pageNum);
                if (pageNum && pageNum > 0) {
                    detectedPage = pageNum;
                }
            }
        });
        
        // 현재 페이지가 변경되었으면 업데이트
        if (detectedPage !== tab.currentPage && detectedPage > 0 && detectedPage <= tab.pageCount) {
            tab.currentPage = detectedPage;
            // 현재 탭인지 다시 확인
            if (tabId === currentTabId) {
                updatePageList(tabId);
            }
        }
    }, {
        root: pdfContainer,
        rootMargin: '-20% 0px -20% 0px', // 중앙 60% 영역에서 감지
        threshold: [0, 0.1, 0.5, 1.0]
    });

    // 모든 캔버스 관찰
    canvases.forEach(canvas => {
        intersectionObserver.observe(canvas);
    });
}

// 스크롤 이벤트 리스너는 전역으로 한 번만 등록
if (!pdfContainer.dataset.scrollListenerAdded) {
    pdfContainer.addEventListener('scroll', () => {
        if (!currentTabId || !tabs[currentTabId]) return;
        
        if (scrollTimeout) {
            clearTimeout(scrollTimeout);
        }
        
        scrollTimeout = setTimeout(() => {
            // 현재 탭 확인
            if (currentTabId && tabs[currentTabId]) {
                updateCurrentPageFromScroll(currentTabId);
            }
        }, 100); // 디바운싱
    }, { passive: true });
    pdfContainer.dataset.scrollListenerAdded = 'true';
}

// 스크롤 위치로 현재 페이지 계산
function updateCurrentPageFromScroll(tabId) {
    // 현재 탭인지 확인
    if (!tabs[tabId] || tabId !== currentTabId) return;
    
    const tab = tabs[tabId];
    const container = pdfContainer;
    const containerRect = container.getBoundingClientRect();
    const containerCenter = containerRect.top + containerRect.height / 2;
    
    const canvases = container.querySelectorAll('canvas[data-page-num]');
    if (canvases.length === 0) return;
    
    let closestPage = tab.currentPage;
    let minDistance = Infinity;
    
    canvases.forEach(canvas => {
        const canvasRect = canvas.getBoundingClientRect();
        const canvasCenter = canvasRect.top + canvasRect.height / 2;
        const distance = Math.abs(canvasCenter - containerCenter);
        
        if (distance < minDistance) {
            minDistance = distance;
            const pageNum = parseInt(canvas.dataset.pageNum);
            if (pageNum && pageNum > 0 && pageNum <= tab.pageCount) {
                closestPage = pageNum;
            }
        }
    });
    
    // 현재 페이지가 변경되었고, 여전히 현재 탭인지 확인
    if (closestPage !== tab.currentPage && closestPage > 0 && closestPage <= tab.pageCount && tabId === currentTabId) {
        tab.currentPage = closestPage;
        updatePageList(tabId);
    }
}

// 페이지 목록 업데이트 (성능 최적화)
function updatePageList(tabId) {
    // 현재 탭인지 확인 - 현재 탭이 아니면 업데이트하지 않음
    if (!tabs[tabId] || tabId !== currentTabId) return;
    
    const tab = tabs[tabId];
    const currentPage = tab.currentPage;
    
    // 페이지 목록 완전히 재생성 (탭 간 충돌 방지)
    pageList.innerHTML = '';
    
    for (let i = 1; i <= tab.pageCount; i++) {
        const item = document.createElement('div');
        item.className = 'page-item' + (i === currentPage ? ' active' : '');
        item.textContent = `페이지 ${i}`;
        item.dataset.pageNum = i;
        
        // 클릭 이벤트
        item.addEventListener('click', () => {
            // 현재 탭인지 다시 확인
            if (tabId !== currentTabId || !tabs[tabId]) return;
            
            const pageNum = parseInt(item.dataset.pageNum);
            tabs[tabId].currentPage = pageNum;
            updatePageList(tabId);
            const canvas = document.querySelector(`canvas[data-page-num="${pageNum}"]`);
            if (canvas) {
                canvas.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
        
        pageList.appendChild(item);
    }
    
    // 버튼 활성화/비활성화
    document.getElementById('btn-move-up').disabled = currentPage <= 1;
    document.getElementById('btn-move-down').disabled = currentPage >= tab.pageCount;
    document.getElementById('btn-delete-page').disabled = tab.pageCount <= 1;
}

// 줌 (성능 최적화)
let zoomTimeout = null;
function zoom(factor) {
    if (!currentTabId || !tabs[currentTabId]) return;
    
    const tab = tabs[currentTabId];
    tab.scale *= factor;
    tab.scale = Math.max(0.5, Math.min(tab.scale, 3.0));
    updateZoomLabel(currentTabId);
    
    // 디바운싱으로 연속 줌 시 성능 개선
    if (zoomTimeout) {
        clearTimeout(zoomTimeout);
    }
    
    zoomTimeout = setTimeout(() => {
        renderAllPages(currentTabId);
    }, 150); // 150ms 후 렌더링
}

function updateZoomLabel(tabId) {
    if (!tabs[tabId]) return;
    document.getElementById('zoom-label').textContent = Math.round(tabs[tabId].scale * 100) + '%';
}

// 페이지 추가
async function handleAddPages(event) {
    const file = event.target.files[0];
    if (!file || !currentTabId) return;

    // 파일 업로드
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        const sourceFileId = data.file_id;
        const sourcePageCount = data.page_count;

        // 페이지 범위 선택 다이얼로그
        const pageRange = prompt(`추가할 페이지 범위를 입력하세요 (1-${sourcePageCount}):\n예: 1-3 또는 1,3,5 또는 전체는 그냥 Enter`, '1-' + sourcePageCount);
        if (pageRange === null) return;

        // 페이지 범위 파싱
        const pages = parsePageRange(pageRange, sourcePageCount);
        if (pages.length === 0) {
            alert('유효한 페이지 범위가 아닙니다.');
            return;
        }

        // 추가 위치 선택
        const tab = tabs[currentTabId];
        const insertPosition = prompt(`어느 위치에 추가하시겠습니까? (1-${tab.pageCount + 1}):`, tab.pageCount + 1);
        if (insertPosition === null) return;

        const position = parseInt(insertPosition);
        if (isNaN(position) || position < 1 || position > tab.pageCount + 1) {
            alert('유효한 위치가 아닙니다.');
            return;
        }

        // 페이지 추가 API 호출
        const addResponse = await fetch(`/api/pdf/${tab.fileId}/pages/add-range`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                source_file_id: sourceFileId,
                pages: pages,
                insert_position: position - 1 // 0-based index
            })
        });

        if (addResponse.ok) {
            const result = await addResponse.json();
            tab.pageCount = result.page_count;
            await loadPdf(currentTabId);
            updatePageList(currentTabId);
        } else {
            alert('페이지 추가 실패');
        }
    } catch (error) {
        console.error('Error adding pages:', error);
        alert('페이지 추가 실패');
    }
    
    addPageFileInput.value = '';
}

// 페이지 범위 파싱
function parsePageRange(range, maxPages) {
    const pages = [];
    const parts = range.split(',');
    
    for (const part of parts) {
        const trimmed = part.trim();
        if (trimmed.includes('-')) {
            const [start, end] = trimmed.split('-').map(s => parseInt(s.trim()));
            if (!isNaN(start) && !isNaN(end)) {
                for (let i = start; i <= end && i <= maxPages; i++) {
                    if (i >= 1 && !pages.includes(i - 1)) {
                        pages.push(i - 1); // 0-based index
                    }
                }
            }
        } else {
            const page = parseInt(trimmed);
            if (!isNaN(page) && page >= 1 && page <= maxPages) {
                if (!pages.includes(page - 1)) {
                    pages.push(page - 1); // 0-based index
                }
            }
        }
    }
    
    return pages.sort((a, b) => a - b);
}

// PDF 합치기 클릭
function handleMergeClick() {
    mergeFileInput.click();
}

// PDF 합치기
async function handleMergeFiles(event) {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    if (files.length < 2) {
        alert('합치려면 최소 2개의 파일이 필요합니다.');
        mergeFileInput.value = '';
        return;
    }

    let mergeOption = null;
    let insertPosition = null;
    let mergedFilename = null;

    if (currentTabId && tabs[currentTabId]) {
        // 열려있는 파일이 있는 경우
        mergeOption = confirm('열려있는 파일과 합치시겠습니까?\n확인: 열려있는 파일과 합치기\n취소: 선택한 파일들만 합치기');
        
        if (mergeOption) {
            // 열려있는 파일과 합치기 - 위치 선택
            const tab = tabs[currentTabId];
            const position = prompt(`어느 위치에 추가하시겠습니까? (1-${tab.pageCount + 1}):`, tab.pageCount + 1);
            if (position === null) {
                mergeFileInput.value = '';
                return;
            }
            insertPosition = parseInt(position);
            if (isNaN(insertPosition) || insertPosition < 1 || insertPosition > tab.pageCount + 1) {
                alert('유효한 위치가 아닙니다.');
                mergeFileInput.value = '';
                return;
            }
        } else {
            // 선택한 파일들만 합치기 - 파일명 입력
            mergedFilename = prompt('합친 파일의 이름을 입력하세요:', 'merged.pdf');
            if (mergedFilename === null) {
                mergeFileInput.value = '';
                return;
            }
            if (!mergedFilename.endsWith('.pdf')) {
                mergedFilename += '.pdf';
            }
        }
    } else {
        // 문서가 열려있지 않은 경우 - 파일명 입력
        mergedFilename = prompt('합친 파일의 이름을 입력하세요:', 'merged.pdf');
        if (mergedFilename === null) {
            mergeFileInput.value = '';
            return;
        }
        if (!mergedFilename.endsWith('.pdf')) {
            mergedFilename += '.pdf';
        }
    }

    try {
        if (mergeOption && currentTabId) {
            // 열려있는 파일과 합치기
            const activeTabId = currentTabId; // 현재 탭 ID 저장
            const tab = tabs[activeTabId];
            
            if (!tab) {
                alert('현재 탭을 찾을 수 없습니다.');
                mergeFileInput.value = '';
                return;
            }
            
            for (const file of files) {
                // 탭이 변경되었는지 확인
                if (currentTabId !== activeTabId || !tabs[activeTabId]) {
                    alert('탭이 변경되어 합치기가 취소되었습니다.');
                    mergeFileInput.value = '';
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', file);
                
                const uploadResponse = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const uploadData = await uploadResponse.json();
                const sourceFileId = uploadData.file_id;
                const sourcePageCount = uploadData.page_count;
                
                // 모든 페이지 추가
                const pages = Array.from({ length: sourcePageCount }, (_, i) => i);
                
                const addResponse = await fetch(`/api/pdf/${tab.fileId}/pages/add-range`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        source_file_id: sourceFileId,
                        pages: pages,
                        insert_position: insertPosition - 1
                    })
                });
                
                if (addResponse.ok) {
                    const result = await addResponse.json();
                    tab.pageCount = result.page_count;
                    insertPosition += sourcePageCount; // 다음 파일은 그 뒤에 추가
                }
            }
            
            // 현재 탭이 여전히 활성인지 확인
            if (currentTabId !== activeTabId || !tabs[activeTabId] || tabs[activeTabId].fileId !== tab.fileId) {
                alert('탭이 변경되어 업데이트가 취소되었습니다.');
                mergeFileInput.value = '';
                return;
            }
            
            // PDF 다시 로드 (파일이 업데이트되었으므로)
            const response = await fetch(`/api/pdf/${tab.fileId}`);
            const arrayBuffer = await response.arrayBuffer();
            const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
            tab.pdf = await loadingTask.promise;
            
            // 현재 탭 확인 후 렌더링
            if (currentTabId === activeTabId && tabs[activeTabId] && tabs[activeTabId].fileId === tab.fileId) {
                await renderAllPages(activeTabId);
                updatePageList(activeTabId);
                updateZoomLabel(activeTabId);
                updateUndoButton();
                // Observer 재설정
                setupScrollObserver(activeTabId);
                alert('PDF 합치기가 완료되었습니다.');
            }
        } else {
            // 선택한 파일들만 합치기 (새 탭 생성)
            const formData = new FormData();
            formData.append('file', files[0]);
            
            const firstResponse = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const firstData = await firstResponse.json();
            let currentFileId = firstData.file_id;
            let currentPageCount = firstData.page_count;
            
            // 나머지 파일들 추가
            for (let i = 1; i < files.length; i++) {
                const fileFormData = new FormData();
                fileFormData.append('file', files[i]);
                
                const uploadResponse = await fetch('/api/upload', {
                    method: 'POST',
                    body: fileFormData
                });
                
                const uploadData = await uploadResponse.json();
                const sourceFileId = uploadData.file_id;
                const sourcePageCount = uploadData.page_count;
                const pages = Array.from({ length: sourcePageCount }, (_, i) => i);
                
                const addResponse = await fetch(`/api/pdf/${currentFileId}/pages/add-range`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        source_file_id: sourceFileId,
                        pages: pages,
                        insert_position: currentPageCount
                    })
                });
                
                if (addResponse.ok) {
                    const result = await addResponse.json();
                    currentPageCount = result.page_count;
                }
            }
            
            // 새 탭 생성
            const tabId = `tab_${tabCounter++}`;
            tabs[tabId] = {
                fileId: currentFileId,
                pageCount: currentPageCount,
                currentPage: 1,
                scale: 1.0,
                filename: mergedFilename || 'merged.pdf',
                pdf: null
            };
            
            createTabUI(tabId, tabs[tabId].filename);
            
            // 탭 전환 (현재 탭을 명시적으로 설정)
            currentTabId = tabId;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelector(`[data-tab-id="${tabId}"]`).classList.add('active');
            
            // PDF 로드
            await loadPdf(tabId);
            
            // 현재 탭 확인 후 업데이트
            if (currentTabId === tabId && tabs[tabId]) {
                await renderAllPages(tabId);
                updatePageList(tabId);
                updateZoomLabel(tabId);
                enableButtons();
                updateUndoButton();
                // Observer 설정
                setupScrollObserver(tabId);
            }
        }
    } catch (error) {
        console.error('Error merging files:', error);
        alert('PDF 합치기 실패: ' + error.message);
    }
    
    mergeFileInput.value = '';
}

// 페이지 이동
async function movePageUp() {
    if (!currentTabId || !tabs[currentTabId]) return;
    const tab = tabs[currentTabId];
    if (tab.currentPage <= 1) return;
    
    try {
        const response = await fetch(`/api/pdf/${tab.fileId}/pages/reorder`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                from: tab.currentPage - 1,
                to: tab.currentPage - 2
            })
        });

        if (response.ok) {
            tab.currentPage--;
            await loadPdf(currentTabId);
            updatePageList(currentTabId);
            updateUndoButton();
        }
    } catch (error) {
        console.error('Error moving page:', error);
        alert('페이지 이동 실패');
    }
}

async function movePageDown() {
    if (!currentTabId || !tabs[currentTabId]) return;
    const tab = tabs[currentTabId];
    if (tab.currentPage >= tab.pageCount) return;
    
    try {
        const response = await fetch(`/api/pdf/${tab.fileId}/pages/reorder`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                from: tab.currentPage - 1,
                to: tab.currentPage
            })
        });

        if (response.ok) {
            tab.currentPage++;
            await loadPdf(currentTabId);
            updatePageList(currentTabId);
            updateUndoButton();
        }
    } catch (error) {
        console.error('Error moving page:', error);
        alert('페이지 이동 실패');
    }
}

// 페이지 삭제
async function deletePage() {
    if (!currentTabId || !tabs[currentTabId]) return;
    const tab = tabs[currentTabId];
    if (tab.pageCount <= 1) {
        alert('최소 1개의 페이지가 필요합니다.');
        return;
    }

    if (!confirm(`페이지 ${tab.currentPage}를 삭제하시겠습니까?`)) return;

    try {
        const response = await fetch(`/api/pdf/${tab.fileId}/pages/${tab.currentPage - 1}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            const data = await response.json();
            tab.pageCount = data.page_count;
            
            if (tab.currentPage > tab.pageCount) {
                tab.currentPage = tab.pageCount;
            }
            
            await loadPdf(currentTabId);
            updatePageList(currentTabId);
            updateUndoButton();
        }
    } catch (error) {
        console.error('Error deleting page:', error);
        alert('페이지 삭제 실패');
    }
}

// 저장
async function savePdf() {
    if (!currentTabId || !tabs[currentTabId]) return;

    try {
        const tab = tabs[currentTabId];
        const response = await fetch(`/api/pdf/${tab.fileId}/download`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = tab.filename;
            a.click();
            window.URL.revokeObjectURL(url);
            alert('저장 완료');
        } else {
            alert('저장 실패');
        }
    } catch (error) {
        console.error('Error saving PDF:', error);
        alert('저장 실패');
    }
}

async function savePdfAs() {
    if (!currentTabId || !tabs[currentTabId]) return;
    
    const filename = prompt('파일명 입력:', tabs[currentTabId].filename);
    if (!filename) return;

    try {
        const tab = tabs[currentTabId];
        const response = await fetch(`/api/pdf/${tab.fileId}/download`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(url);
            alert('저장 완료');
        } else {
            alert('저장 실패');
        }
    } catch (error) {
        console.error('Error saving PDF:', error);
        alert('저장 실패');
    }
}

// Undo 기능
async function undoLastAction() {
    if (!currentTabId || !tabs[currentTabId]) return;

    try {
        const tab = tabs[currentTabId];
        const response = await fetch(`/api/pdf/${tab.fileId}/undo`, {
            method: 'POST'
        });

        if (response.ok) {
            const data = await response.json();
            tab.pageCount = data.page_count;
            await loadPdf(currentTabId);
            updatePageList(currentTabId);
            updateUndoButton();
        } else {
            const error = await response.json();
            alert(error.detail || 'Undo 실패');
        }
    } catch (error) {
        console.error('Error undoing action:', error);
        alert('Undo 실패');
    }
}

async function updateUndoButton() {
    if (!currentTabId || !tabs[currentTabId]) {
        document.getElementById('btn-undo').disabled = true;
        return;
    }

    try {
        const tab = tabs[currentTabId];
        const response = await fetch(`/api/pdf/${tab.fileId}/undo/status`);
        if (response.ok) {
            const data = await response.json();
            document.getElementById('btn-undo').disabled = !data.can_undo;
        }
    } catch (error) {
        document.getElementById('btn-undo').disabled = true;
    }
}

function enableButtons() {
    const hasTab = currentTabId && tabs[currentTabId];
    document.getElementById('btn-save').disabled = !hasTab;
    document.getElementById('btn-save-as').disabled = !hasTab;
    document.getElementById('btn-merge').disabled = false; // 항상 활성화
    document.getElementById('btn-add-pages').disabled = !hasTab;
    updateUndoButton();
}
