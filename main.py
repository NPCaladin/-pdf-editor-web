import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QPointF, QPoint, QRect
from PySide6.QtGui import QAction, QPainter, QPen, QColor, QMouseEvent, QPaintEvent
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QFileDialog,
    QMessageBox,
    QPushButton,
    QDialog,
    QDialogButtonBox,
    QSpinBox,
    QRadioButton,
    QButtonGroup,
    QFormLayout,
    QTabWidget,
    QSizePolicy,
)

from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF


class TextInputDialog(QDialog):
    """텍스트 입력 다이얼로그 (색상, 크기 선택 가능)"""
    
    def __init__(self, parent=None, default_text: str = "", default_color: QColor = QColor(255, 0, 0), default_size: int = 12):
        super().__init__(parent)
        self.setWindowTitle("텍스트 입력")
        self.setModal(True)
        self.resize(400, 250)
        
        main_layout = QVBoxLayout(self)
        
        # 텍스트 입력
        from PySide6.QtWidgets import QLineEdit, QTextEdit
        text_label = QLabel("텍스트:")
        self.text_edit = QLineEdit()
        self.text_edit.setText(default_text)
        self.text_edit.setMinimumHeight(40)
        self.text_edit.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: black;
                border: 2px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        
        text_layout = QVBoxLayout()
        text_layout.addWidget(text_label)
        text_layout.addWidget(self.text_edit)
        main_layout.addLayout(text_layout)
        
        # 색상 선택
        color_label = QLabel("색상:")
        color_layout = QHBoxLayout()
        self.color_group = QButtonGroup(self)
        self.btn_color_red = QRadioButton("빨강")
        self.btn_color_blue = QRadioButton("파랑")
        self.btn_color_black = QRadioButton("검정")
        
        if default_color == QColor(255, 0, 0):
            self.btn_color_red.setChecked(True)
        elif default_color == QColor(0, 0, 255):
            self.btn_color_blue.setChecked(True)
        else:
            self.btn_color_black.setChecked(True)
        
        self.color_group.addButton(self.btn_color_red, 0)
        self.color_group.addButton(self.btn_color_blue, 1)
        self.color_group.addButton(self.btn_color_black, 2)
        
        color_layout.addWidget(self.btn_color_red)
        color_layout.addWidget(self.btn_color_blue)
        color_layout.addWidget(self.btn_color_black)
        color_layout.addStretch()
        
        color_container = QVBoxLayout()
        color_container.addWidget(color_label)
        color_container.addLayout(color_layout)
        main_layout.addLayout(color_container)
        
        # 크기 선택
        size_label = QLabel("크기:")
        self.size_spin = QSpinBox()
        self.size_spin.setMinimum(8)
        self.size_spin.setMaximum(72)
        self.size_spin.setValue(default_size)
        
        size_layout = QHBoxLayout()
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spin)
        size_layout.addStretch()
        main_layout.addLayout(size_layout)
        
        main_layout.addStretch()
        
        # 버튼
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.btn_ok = QPushButton("확인")
        self.btn_ok.setMinimumWidth(80)
        self.btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        self.btn_ok.clicked.connect(self.accept)
        
        self.btn_cancel = QPushButton("취소")
        self.btn_cancel.setMinimumWidth(80)
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f3f3f3;
                color: black;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e1e1e1;
            }
            QPushButton:pressed {
                background-color: #d1d1d1;
            }
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_ok)
        main_layout.addLayout(button_layout)
    
    def get_text(self) -> str:
        """입력된 텍스트 반환"""
        return self.text_edit.text()
    
    def get_color(self) -> QColor:
        """선택된 색상 반환"""
        if self.btn_color_red.isChecked():
            return QColor(255, 0, 0)
        elif self.btn_color_blue.isChecked():
            return QColor(0, 0, 255)
        else:
            return QColor(0, 0, 0)
    
    def get_size(self) -> int:
        """선택된 크기 반환"""
        return self.size_spin.value()


class DrawingLayer(QWidget):
    """PDF 위에 그리기를 위한 투명 레이어"""
    
    def __init__(self, parent=None, pdf_view=None, pdf_doc=None):
        super().__init__(parent)
        # 마우스 이벤트를 받기 위해 필수
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setStyleSheet("background: transparent;")
        # 마우스 추적 활성화
        self.setMouseTracking(True)
        
        self.drawing_mode = "cursor"  # "cursor", "pen", "highlighter", "text", "rectangle", "ellipse"
        self.drawing_color = QColor(255, 0, 0)  # 빨간색 기본
        self.pen_width = 3
        
        self.pdf_view = pdf_view  # PDF 뷰어 참조
        self.pdf_doc = pdf_doc  # PDF 문서 참조
        self._pdf_path = None  # PDF 파일 경로
        
        self.current_path = []  # 현재 그리는 경로 (화면 좌표)
        self.drawn_paths_by_page = {}  # 페이지별로 그려진 경로들 {page_index: [drawings]} (PDF 좌표로 저장)
        self.current_page_index = 0  # 현재 페이지 인덱스
        self.start_point = None  # 화면 좌표
        self.end_point = None  # 화면 좌표
        
        self.is_drawing = False
        self.is_panning = False  # 페이지 드래그 중인지
        self.pan_start_pos = None  # 드래그 시작 위치
        self.pan_start_scroll = None  # 드래그 시작 시 스크롤 위치
        
        # 필기 선택 관련
        self.selected_drawing_index = None  # 선택된 필기 인덱스
        self.selected_group_id = None  # 선택된 그룹 ID
        self.selection_mode = False  # 선택 모드
        
        # 필기 그룹화: 여러 획을 하나의 그룹으로 묶기
        self._drawing_groups = {}  # {page_index: {group_id: [drawing_indices]}}
        self._current_group_id = 0  # 현재 그룹 ID
        self._last_drawing_time = 0  # 마지막 필기 시간
        from PySide6.QtCore import QElapsedTimer
        self._elapsed_timer = QElapsedTimer()
        self._elapsed_timer.start()
        
        # 성능 최적화: 좌표 변환 캐싱
        self._page_size_cache = {}  # {page_index: (width, height)}
        self._last_update_time = 0  # 마지막 업데이트 시간
        from PySide6.QtCore import QTimer
        self._update_timer = QTimer(self)
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._delayed_update)
        self._pending_update = False
    
    def set_pdf_path(self, pdf_path):
        """PDF 파일 경로 설정"""
        self._pdf_path = pdf_path
    
    def _get_pdf_page_size(self, page_index: int):
        """PyMuPDF를 사용하여 PDF 페이지 크기 가져오기 (캐싱)"""
        # 캐시에서 먼저 확인
        if page_index in self._page_size_cache:
            return self._page_size_cache[page_index]
        
        if not hasattr(self, '_pdf_path') or not self._pdf_path:
            return None, None
        
        try:
            import fitz
            doc = fitz.open(str(self._pdf_path))
            if 0 <= page_index < len(doc):
                page = doc[page_index]
                rect = page.rect
                size = (rect.width, rect.height)
                # 캐시에 저장
                self._page_size_cache[page_index] = size
                doc.close()
                return size
            doc.close()
        except:
            pass
        
        return None, None
    
    def _delayed_update(self):
        """지연된 업데이트 (성능 최적화)"""
        if self._pending_update:
            self._pending_update = False
            self.update()
    
    def _screen_to_pdf_coords(self, screen_point: QPoint, page_index: int) -> QPointF:
        """화면 좌표를 PDF 좌표로 변환 (MultiPage 모드 고려)"""
        if not self.pdf_view or not self.pdf_doc or page_index < 0 or page_index >= self.pdf_doc.pageCount():
            return QPointF(screen_point.x(), screen_point.y())
        
        try:
            # PyMuPDF를 사용하여 PDF 페이지 크기 가져오기
            pdf_width, pdf_height = self._get_pdf_page_size(page_index)
            if pdf_width is None or pdf_height is None:
                return QPointF(screen_point.x(), screen_point.y())
            
            # 줌 팩터
            zoom = self.pdf_view.zoomFactor()
            
            # 뷰포트 크기
            viewport = self.pdf_view.viewport()
            viewport_width = viewport.width()
            viewport_height = viewport.height()
            
            # 스크롤 오프셋
            scrollbar = self.pdf_view.verticalScrollBar()
            scroll_offset_y = scrollbar.value() if scrollbar else 0
            
            # MultiPage 모드에서 각 페이지의 화면상 위치 계산
            page_y_offset = 0
            for i in range(page_index):
                prev_pdf_width, prev_pdf_height = self._get_pdf_page_size(i)
                if prev_pdf_height is not None:
                    # 페이지 높이를 줌 팩터로 조정
                    page_y_offset += prev_pdf_height * zoom
            
            # 화면 좌표에서 페이지 오프셋과 스크롤 오프셋 제거
            relative_y = screen_point.y() + scroll_offset_y - page_y_offset
            
            # PDF 좌표로 변환
            pdf_x = (screen_point.x() / viewport_width) * pdf_width
            pdf_y = (relative_y / (pdf_height * zoom)) * pdf_height
            
            return QPointF(pdf_x, pdf_y)
        except Exception as e:
            pass
        
        return QPointF(screen_point.x(), screen_point.y())
    
    def _pdf_to_screen_coords(self, pdf_point: QPointF, page_index: int) -> QPoint:
        """PDF 좌표를 화면 좌표로 변환 (MultiPage 모드 고려)"""
        if not self.pdf_view or not self.pdf_doc or page_index < 0 or page_index >= self.pdf_doc.pageCount():
            return QPoint(int(pdf_point.x()), int(pdf_point.y()))
        
        try:
            # PyMuPDF를 사용하여 PDF 페이지 크기 가져오기
            pdf_width, pdf_height = self._get_pdf_page_size(page_index)
            if pdf_width is None or pdf_height is None:
                return QPoint(int(pdf_point.x()), int(pdf_point.y()))
            
            # 줌 팩터
            zoom = self.pdf_view.zoomFactor()
            
            # 뷰포트 크기
            viewport = self.pdf_view.viewport()
            viewport_width = viewport.width()
            
            # 스크롤 오프셋
            scrollbar = self.pdf_view.verticalScrollBar()
            scroll_offset_y = scrollbar.value() if scrollbar else 0
            
            # MultiPage 모드에서 각 페이지의 화면상 위치 계산
            page_y_offset = 0
            for i in range(page_index):
                prev_pdf_width, prev_pdf_height = self._get_pdf_page_size(i)
                if prev_pdf_height is not None:
                    page_y_offset += prev_pdf_height * zoom
            
            # PDF 좌표를 화면 좌표로 변환
            screen_x = (pdf_point.x() / pdf_width) * viewport_width
            screen_y = (pdf_point.y() / pdf_height) * pdf_height * zoom + page_y_offset - scroll_offset_y
            
            return QPoint(int(screen_x), int(screen_y))
        except Exception as e:
            pass
        
        return QPoint(int(pdf_point.x()), int(pdf_point.y()))
    
    def set_current_page(self, page_index: int):
        """현재 페이지 설정"""
        self.current_page_index = page_index
        # 현재 페이지의 필기가 없으면 빈 리스트로 초기화
        if page_index not in self.drawn_paths_by_page:
            self.drawn_paths_by_page[page_index] = []
        # 선택 해제
        self.selected_drawing_index = None
        self.update()
    
    def get_current_page_drawings(self):
        """현재 페이지의 필기 반환"""
        return self.drawn_paths_by_page.get(self.current_page_index, [])
    
    def set_drawing_mode(self, mode: str):
        """그리기 모드 설정"""
        self.drawing_mode = mode
        if mode == "highlighter":
            self.drawing_color.setAlpha(128)  # 반투명
        else:
            self.drawing_color.setAlpha(255)  # 불투명
        
        # 커서 모드일 때도 마우스 이벤트를 받아서 드래그로 페이지 이동 가능
        # (필기 모드와 동일하게 마우스 이벤트 처리)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        # 커서 모양 설정
        if mode == "cursor":
            from PySide6.QtGui import QCursor
            self.setCursor(Qt.OpenHandCursor)
        elif mode == "select":
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
    
    def set_color(self, color: QColor):
        """색상 설정"""
        alpha = self.drawing_color.alpha()
        self.drawing_color = color
        self.drawing_color.setAlpha(alpha)
    
    def set_pen_width(self, width: int):
        """펜 두께 설정"""
        self.pen_width = width
    
    def _point_in_drawing(self, point: QPoint, drawing, page_index: int) -> bool:
        """점이 필기 내부에 있는지 확인"""
        try:
            if drawing["type"] in ["pen", "highlighter"]:
                # 경로의 선분(점과 점 사이의 선) 중 가까운 선분이 있는지 확인
                path = drawing["path"]
                if len(path) < 1:
                    return False
                
                threshold = max(10, drawing.get("width", 5) + 5)  # 펜 굵기에 따라 임계값 조정
                
                # 경로의 각 선분에 대해 점과의 거리 확인
                for i in range(len(path) - 1):
                    pt1 = self._pdf_to_screen_coords(path[i], page_index)
                    pt2 = self._pdf_to_screen_coords(path[i + 1], page_index)
                    
                    # 선분과 점 사이의 최단 거리 계산
                    # 선분의 방향 벡터
                    dx = pt2.x() - pt1.x()
                    dy = pt2.y() - pt1.y()
                    
                    # 선분의 길이
                    seg_len_sq = dx * dx + dy * dy
                    
                    if seg_len_sq < 0.01:  # 선분이 너무 짧으면 점 거리로 확인
                        dist = ((point.x() - pt1.x()) ** 2 + (point.y() - pt1.y()) ** 2) ** 0.5
                        if dist < threshold:
                            return True
                    else:
                        # 점에서 선분까지의 최단 거리
                        # t는 선분 위의 가장 가까운 점의 위치 (0~1)
                        t = max(0, min(1, ((point.x() - pt1.x()) * dx + (point.y() - pt1.y()) * dy) / seg_len_sq))
                        # 선분 위의 가장 가까운 점
                        closest_x = pt1.x() + t * dx
                        closest_y = pt1.y() + t * dy
                        # 거리 계산
                        dist = ((point.x() - closest_x) ** 2 + (point.y() - closest_y) ** 2) ** 0.5
                        if dist < threshold:
                            return True
                
                # 마지막 점도 확인 (혹시 모를 경우를 위해)
                if len(path) > 0:
                    last_pt = self._pdf_to_screen_coords(path[-1], page_index)
                    dist = ((point.x() - last_pt.x()) ** 2 + (point.y() - last_pt.y()) ** 2) ** 0.5
                    if dist < threshold:
                        return True
                
                return False
            elif drawing["type"] in ["rectangle", "ellipse"]:
                screen_start = self._pdf_to_screen_coords(drawing["start"], page_index)
                screen_end = self._pdf_to_screen_coords(drawing["end"], page_index)
                rect = self._get_rect(screen_start, screen_end)
                return rect.contains(point)
            elif drawing["type"] == "text":
                screen_pos = self._pdf_to_screen_coords(drawing["position"], page_index)
                # 텍스트 영역 근처 확인
                threshold = 50
                dist = ((point.x() - screen_pos.x()) ** 2 + (point.y() - screen_pos.y()) ** 2) ** 0.5
                return dist < threshold
        except:
            pass
        return False
    
    def mousePressEvent(self, event: QMouseEvent):
        """마우스 누르기"""
        if event.button() == Qt.LeftButton:
            # 선택 모드일 때는 필기 선택
            if self.drawing_mode == "select":
                click_pos = event.position().toPoint()
                current_drawings = self.get_current_page_drawings()
                # 클릭한 위치의 필기 찾기 (역순으로 검색하여 위에 있는 것 선택)
                self.selected_drawing_index = None
                self.selected_group_id = None
                for i in range(len(current_drawings) - 1, -1, -1):
                    if self._point_in_drawing(click_pos, current_drawings[i], self.current_page_index):
                        self.selected_drawing_index = i
                        # 같은 그룹의 모든 필기 찾기
                        if "group_id" in current_drawings[i]:
                            self.selected_group_id = current_drawings[i]["group_id"]
                        break
                self.update()
                # 선택 삭제 버튼 활성화/비활성화 (부모 위젯에서 찾기)
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'btn_delete_selected'):
                        parent.btn_delete_selected.setEnabled(self.selected_drawing_index is not None)
                        break
                    parent = parent.parent()
                return
            
            # 커서 모드일 때는 드래그로 페이지 이동
            if self.drawing_mode == "cursor":
                if self.pdf_view:
                    scrollbar = self.pdf_view.verticalScrollBar()
                    if scrollbar:
                        self.is_panning = True
                        self.pan_start_pos = event.position().toPoint()
                        self.pan_start_scroll = (scrollbar.value(), self.pdf_view.horizontalScrollBar().value() if self.pdf_view.horizontalScrollBar() else 0)
                        # 커서를 손 모양으로 변경
                        self.setCursor(Qt.ClosedHandCursor)
                return
            
            # 필기 모드
            if self.drawing_mode == "text":
                # 텍스트 모드는 클릭 위치에 텍스트 입력 다이얼로그 표시
                dialog = TextInputDialog(self, "", self.drawing_color, self.pen_width * 2)
                if dialog.exec() == QDialog.Accepted:
                    text = dialog.get_text()
                    if text:
                        # 현재 페이지에만 추가
                        if self.current_page_index not in self.drawn_paths_by_page:
                            self.drawn_paths_by_page[self.current_page_index] = []
                        # 화면 좌표를 PDF 좌표로 변환
                        screen_pos = event.position().toPoint()
                        pdf_pos = self._screen_to_pdf_coords(screen_pos, self.current_page_index)
                        self.drawn_paths_by_page[self.current_page_index].append({
                            "type": "text",
                            "position": pdf_pos,  # PDF 좌표로 저장
                            "text": text,
                            "color": dialog.get_color(),
                            "width": dialog.get_size()
                        })
                        self.update()
                return
            
            self.is_drawing = True
            self.start_point = event.position().toPoint()
            self.end_point = self.start_point
            
            if self.drawing_mode in ["pen", "highlighter"]:
                self.current_path = [self.start_point]
            else:
                self.current_path = []
            
            self.update()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """마우스 이동"""
        # 커서 모드일 때 드래그로 페이지 이동
        if self.drawing_mode == "cursor" and self.is_panning:
            if self.pdf_view and self.pan_start_pos and self.pan_start_scroll:
                current_pos = event.position().toPoint()
                delta = current_pos - self.pan_start_pos
                
                # 스크롤바 조정
                scrollbar_v = self.pdf_view.verticalScrollBar()
                scrollbar_h = self.pdf_view.horizontalScrollBar()
                
                if scrollbar_v:
                    new_v = self.pan_start_scroll[0] - delta.y()
                    scrollbar_v.setValue(int(new_v))
                
                if scrollbar_h:
                    new_h = self.pan_start_scroll[1] - delta.x()
                    scrollbar_h.setValue(int(new_h))
            return
        
        if self.is_drawing and event.buttons() & Qt.LeftButton:
            current_point = event.position().toPoint()
            
            if self.drawing_mode in ["pen", "highlighter"]:
                self.current_path.append(current_point)
                # 성능 최적화: 너무 많은 점이 쌓이면 일부 제거
                if len(self.current_path) > 500:
                    # 경로 단순화: 일정 간격으로 점 선택 (부드러움 유지하면서 성능 향상)
                    step = max(1, len(self.current_path) // 300)
                    self.current_path = [self.current_path[i] for i in range(0, len(self.current_path), step)]
                
                # 업데이트 빈도 줄이기 (타이머 사용)
                self._pending_update = True
                if not self._update_timer.isActive():
                    self._update_timer.start(16)  # 약 60fps (16ms)
            else:
                # 사각형/원은 마지막 점만 업데이트 (성능 최적화)
                self.end_point = current_point
                # 사각형/원은 업데이트 빈도 줄이기 (타이머 사용 대신 직접 업데이트)
                self.update()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """마우스 놓기"""
        # 커서 모드일 때 드래그 종료
        if self.drawing_mode == "cursor" and self.is_panning:
            if event.button() == Qt.LeftButton:
                self.is_panning = False
                self.pan_start_pos = None
                self.pan_start_scroll = None
                # 커서를 기본으로 변경
                self.setCursor(Qt.ArrowCursor)
            return
        
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            
            # 현재 페이지의 필기 리스트 초기화 (없으면)
            if self.current_page_index not in self.drawn_paths_by_page:
                self.drawn_paths_by_page[self.current_page_index] = []
            
            if self.drawing_mode in ["pen", "highlighter"]:
                if len(self.current_path) > 1:
                    # 성능 최적화: 경로 단순화 (부드러움 유지하면서 점 수 제한)
                    # 화면 좌표를 PDF 좌표로 변환하면서 동시에 단순화
                    simplified_path = []
                    step = max(1, len(self.current_path) // 300)  # 최대 300개 점만 사용
                    for i in range(0, len(self.current_path), step):
                        pt = self.current_path[i]
                        pdf_pt = self._screen_to_pdf_coords(pt, self.current_page_index)
                        simplified_path.append(pdf_pt)
                    
                    # 마지막 점은 항상 포함
                    if len(self.current_path) > 1 and (len(self.current_path) - 1) % step != 0:
                        last_pt = self._screen_to_pdf_coords(self.current_path[-1], self.current_page_index)
                        if len(simplified_path) == 0 or simplified_path[-1] != last_pt:
                            simplified_path.append(last_pt)
                    
                    # 현재 시간 확인
                    current_time = self._elapsed_timer.elapsed()
                    time_since_last = current_time - self._last_drawing_time
                    
                    # 1초 이내에 다시 그리면 같은 그룹으로 묶기
                    if time_since_last > 1000:  # 1초 이상 지나면 새 그룹
                        self._current_group_id += 1
                    
                    # 필기 저장
                    drawing_index = len(self.drawn_paths_by_page[self.current_page_index])
                    self.drawn_paths_by_page[self.current_page_index].append({
                        "type": self.drawing_mode,
                        "path": simplified_path,  # PDF 좌표로 저장 (단순화됨)
                        "color": QColor(self.drawing_color),
                        "width": self.pen_width,
                        "group_id": self._current_group_id  # 그룹 ID 추가
                    })
                    
                    # 그룹에 추가
                    if self.current_page_index not in self._drawing_groups:
                        self._drawing_groups[self.current_page_index] = {}
                    if self._current_group_id not in self._drawing_groups[self.current_page_index]:
                        self._drawing_groups[self.current_page_index][self._current_group_id] = []
                    self._drawing_groups[self.current_page_index][self._current_group_id].append(drawing_index)
                    
                    # 마지막 필기 시간 업데이트
                    self._last_drawing_time = current_time
            else:
                if self.start_point and self.end_point:
                    # 화면 좌표를 PDF 좌표로 변환
                    pdf_start = self._screen_to_pdf_coords(self.start_point, self.current_page_index)
                    pdf_end = self._screen_to_pdf_coords(self.end_point, self.current_page_index)
                    self.drawn_paths_by_page[self.current_page_index].append({
                        "type": self.drawing_mode,
                        "start": pdf_start,  # PDF 좌표로 저장
                        "end": pdf_end,  # PDF 좌표로 저장
                        "color": QColor(self.drawing_color),
                        "width": self.pen_width
                    })
            
            self.current_path = []
            self.start_point = None
            self.end_point = None
            self.update()
    
    def wheelEvent(self, event):
        """마우스 휠 이벤트"""
        # 커서 모드일 때는 마우스 휠 이벤트를 PDF 뷰어의 스크롤바로 전달
        if self.drawing_mode == "cursor":
            if self.pdf_view:
                scrollbar = self.pdf_view.verticalScrollBar()
                if scrollbar:
                    # 휠 델타 값을 스크롤바에 적용
                    delta = event.angleDelta().y()
                    if delta != 0:
                        current_value = scrollbar.value()
                        # 스크롤 속도 조절 (기본값의 3배)
                        scroll_amount = delta // 8 * 3
                        new_value = current_value - scroll_amount
                        scrollbar.setValue(new_value)
            return
        
        # 필기 모드일 때는 이벤트를 처리 (필기 중 스크롤 방지)
        event.accept()
    
    def paintEvent(self, event: QPaintEvent):
        """그리기 (최적화)"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 펜/하이라이터는 경로를 단순화하여 성능 향상
        # 현재 페이지에 그린 경로들만 표시 (PDF 좌표를 화면 좌표로 변환)
        current_drawings = self.get_current_page_drawings()
        for path_data in current_drawings:
            pen = QPen(path_data["color"], path_data["width"])
            painter.setPen(pen)
            
            # 선택된 필기는 강조 표시 (같은 그룹의 모든 필기 강조)
            is_selected = False
            if self.selected_drawing_index is not None:
                current_idx = current_drawings.index(path_data)
                if current_idx == self.selected_drawing_index:
                    is_selected = True
                elif self.selected_group_id is not None and "group_id" in path_data:
                    # 같은 그룹의 필기도 강조
                    if path_data["group_id"] == self.selected_group_id:
                        is_selected = True
            
            if path_data["type"] in ["pen", "highlighter"]:
                if len(path_data["path"]) > 1:
                    # 성능 최적화: 경로는 이미 단순화되어 저장됨
                    path = path_data["path"]
                    # 모든 점을 직선으로 연결 (이미 단순화되어 있으므로 빠름)
                    for i in range(len(path) - 1):
                        screen_pt1 = self._pdf_to_screen_coords(path[i], self.current_page_index)
                        screen_pt2 = self._pdf_to_screen_coords(path[i + 1], self.current_page_index)
                        painter.drawLine(screen_pt1, screen_pt2)
                    
                    # 선택된 필기는 강조 표시
                    if is_selected:
                        highlight_pen = QPen(QColor(255, 255, 0), path_data["width"] + 4)
                        highlight_pen.setStyle(Qt.DashLine)
                        painter.setPen(highlight_pen)
                        # 강조 표시도 동일하게
                        for i in range(len(path) - 1):
                            screen_pt1 = self._pdf_to_screen_coords(path[i], self.current_page_index)
                            screen_pt2 = self._pdf_to_screen_coords(path[i + 1], self.current_page_index)
                            painter.drawLine(screen_pt1, screen_pt2)
                        painter.setPen(pen)
            elif path_data["type"] == "rectangle":
                # PDF 좌표를 화면 좌표로 변환
                screen_start = self._pdf_to_screen_coords(path_data["start"], self.current_page_index)
                screen_end = self._pdf_to_screen_coords(path_data["end"], self.current_page_index)
                rect = self._get_rect(screen_start, screen_end)
                painter.drawRect(rect)
                # 선택된 필기는 강조 표시
                if is_selected:
                    highlight_pen = QPen(QColor(255, 255, 0), 3)
                    highlight_pen.setStyle(Qt.DashLine)
                    painter.setPen(highlight_pen)
                    painter.drawRect(rect)
                    painter.setPen(pen)
            elif path_data["type"] == "ellipse":
                # PDF 좌표를 화면 좌표로 변환
                screen_start = self._pdf_to_screen_coords(path_data["start"], self.current_page_index)
                screen_end = self._pdf_to_screen_coords(path_data["end"], self.current_page_index)
                rect = self._get_rect(screen_start, screen_end)
                painter.drawEllipse(rect)
                # 선택된 필기는 강조 표시
                if is_selected:
                    highlight_pen = QPen(QColor(255, 255, 0), 3)
                    highlight_pen.setStyle(Qt.DashLine)
                    painter.setPen(highlight_pen)
                    painter.drawEllipse(rect)
                    painter.setPen(pen)
            elif path_data["type"] == "text":
                # 텍스트 그리기 (PDF 좌표를 화면 좌표로 변환)
                from PySide6.QtGui import QFont
                font = QFont()
                font.setPointSize(path_data["width"])
                painter.setFont(font)
                painter.setPen(QPen(path_data["color"], 1))
                screen_pos = self._pdf_to_screen_coords(path_data["position"], self.current_page_index)
                painter.drawText(screen_pos, path_data["text"])
                # 선택된 필기는 강조 표시
                if is_selected:
                    highlight_pen = QPen(QColor(255, 255, 0), 3)
                    highlight_pen.setStyle(Qt.DashLine)
                    painter.setPen(highlight_pen)
                    # 텍스트 주변에 사각형 그리기
                    text_rect = QRect(screen_pos.x() - 5, screen_pos.y() - path_data["width"], 
                                     len(path_data["text"]) * path_data["width"] // 2, path_data["width"] + 10)
                    painter.drawRect(text_rect)
                    painter.setPen(QPen(path_data["color"], 1))
        
        # 현재 그리는 중인 경로 (실시간 반영)
        if self.is_drawing:
            pen = QPen(self.drawing_color, self.pen_width)
            painter.setPen(pen)
            
            if self.drawing_mode in ["pen", "highlighter"]:
                if len(self.current_path) > 1:
                    # 실시간 그리기는 모든 점을 직선으로 연결 (부드럽고 빠름)
                    # 성능 최적화: 너무 많은 점이면 일부만 그리기
                    if len(self.current_path) > 500:
                        step = max(1, len(self.current_path) // 300)
                        for i in range(0, len(self.current_path) - 1, step):
                            next_idx = min(i + step, len(self.current_path) - 1)
                            painter.drawLine(self.current_path[i], self.current_path[next_idx])
                    else:
                        for i in range(len(self.current_path) - 1):
                            painter.drawLine(self.current_path[i], self.current_path[i + 1])
            elif self.drawing_mode == "rectangle" and self.start_point and self.end_point:
                rect = self._get_rect(self.start_point, self.end_point)
                painter.drawRect(rect)
            elif self.drawing_mode == "ellipse" and self.start_point and self.end_point:
                rect = self._get_rect(self.start_point, self.end_point)
                painter.drawEllipse(rect)
    
    def _get_rect(self, p1: QPoint, p2: QPoint):
        """두 점으로부터 사각형 생성"""
        return QRect(
            min(p1.x(), p2.x()),
            min(p1.y(), p2.y()),
            abs(p2.x() - p1.x()),
            abs(p2.y() - p1.y())
        )
    
    def clear_drawings(self):
        """현재 페이지의 그린 내용 모두 지우기"""
        if self.current_page_index in self.drawn_paths_by_page:
            self.drawn_paths_by_page[self.current_page_index] = []
        self.current_path = []
        self.update()
    
    def get_drawings(self, page_index: int = None):
        """그린 내용 반환 (특정 페이지 또는 현재 페이지)"""
        if page_index is None:
            page_index = self.current_page_index
        return self.drawn_paths_by_page.get(page_index, []).copy()


class ExtractPagesDialog(QDialog):
    """페이지 범위를 추출하는 다이얼로그"""
    
    def __init__(self, parent=None, total_pages: int = 0):
        super().__init__(parent)
        self.setWindowTitle("페이지 범위 저장")
        self.setModal(True)
        
        layout = QFormLayout(self)
        
        # 페이지 범위 입력
        self.start_page = QSpinBox()
        self.start_page.setMinimum(1)
        self.start_page.setMaximum(total_pages)
        self.start_page.setValue(1)
        
        self.end_page = QSpinBox()
        self.end_page.setMinimum(1)
        self.end_page.setMaximum(total_pages)
        self.end_page.setValue(total_pages if total_pages > 0 else 1)
        
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("시작:"))
        range_layout.addWidget(self.start_page)
        range_layout.addWidget(QLabel("끝:"))
        range_layout.addWidget(self.end_page)
        range_layout.addStretch()
        
        layout.addRow("페이지 범위:", range_layout)
        
        # 버튼
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_page_range(self) -> tuple[int, int] | None:
        """저장할 페이지 범위 반환 (start, end) - 1-based"""
        start = self.start_page.value()
        end = self.end_page.value()
        if start > end:
            return None
        return (start, end)


class InsertPagesDialog(QDialog):
    """다른 PDF에서 페이지를 가져와 삽입하는 다이얼로그"""
    
    def __init__(self, parent=None, source_page_count: int = 0):
        super().__init__(parent)
        self.setWindowTitle("페이지 추가")
        self.setModal(True)
        
        layout = QFormLayout(self)
        
        # 페이지 범위 선택
        self.page_range_group = QButtonGroup(self)
        self.radio_all = QRadioButton("전체 페이지")
        self.radio_range = QRadioButton("페이지 범위")
        self.page_range_group.addButton(self.radio_all, 0)
        self.page_range_group.addButton(self.radio_range, 1)
        self.radio_all.setChecked(True)
        
        range_layout = QHBoxLayout()
        range_layout.addWidget(self.radio_all)
        range_layout.addWidget(self.radio_range)
        
        self.start_page = QSpinBox()
        self.start_page.setMinimum(1)
        self.start_page.setMaximum(source_page_count)
        self.start_page.setValue(1)
        self.start_page.setEnabled(False)
        
        self.end_page = QSpinBox()
        self.end_page.setMinimum(1)
        self.end_page.setMaximum(source_page_count)
        self.end_page.setValue(source_page_count if source_page_count > 0 else 1)
        self.end_page.setEnabled(False)
        
        self.radio_range.toggled.connect(lambda checked: self.start_page.setEnabled(checked))
        self.radio_range.toggled.connect(lambda checked: self.end_page.setEnabled(checked))
        
        range_input_layout = QHBoxLayout()
        range_input_layout.addWidget(QLabel("시작:"))
        range_input_layout.addWidget(self.start_page)
        range_input_layout.addWidget(QLabel("끝:"))
        range_input_layout.addWidget(self.end_page)
        range_input_layout.addStretch()
        
        layout.addRow("가져올 페이지:", range_layout)
        layout.addRow("", range_input_layout)
        
        # 삽입 위치 선택
        self.insert_pos_group = QButtonGroup(self)
        self.radio_before = QRadioButton("현재 페이지 앞에")
        self.radio_after = QRadioButton("현재 페이지 뒤에")
        self.radio_end = QRadioButton("맨 뒤에")
        self.insert_pos_group.addButton(self.radio_before, 0)
        self.insert_pos_group.addButton(self.radio_after, 1)
        self.insert_pos_group.addButton(self.radio_end, 2)
        self.radio_after.setChecked(True)
        
        pos_layout = QVBoxLayout()
        pos_layout.addWidget(self.radio_before)
        pos_layout.addWidget(self.radio_after)
        pos_layout.addWidget(self.radio_end)
        
        layout.addRow("삽입 위치:", pos_layout)
        
        # 버튼
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def get_page_range(self) -> tuple[int, int] | None:
        """가져올 페이지 범위 반환 (start, end) - 0-based 인덱스"""
        if self.radio_all.isChecked():
            return (0, self.end_page.maximum() - 1)
        else:
            start = self.start_page.value() - 1  # 1-based -> 0-based
            end = self.end_page.value() - 1
            if start > end:
                return None
            return (start, end)
    
    def get_insert_position(self) -> str:
        """삽입 위치 반환: 'before', 'after', 'end'"""
        if self.radio_before.isChecked():
            return 'before'
        elif self.radio_after.isChecked():
            return 'after'
        else:
            return 'end'


class PdfEditorTab(QWidget):
    """각 탭에서 사용하는 PDF 편집기 위젯"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pdf_doc = QPdfDocument(self)
        self._current_path: Path | None = None
        self._current_zoom = 1.0
        self._undo_stack = []  # 최대 10개까지 저장
        self._max_undo = 10
        
        self._setup_ui()
    
    def _setup_ui(self):
        root_layout = QHBoxLayout(self)
        
        # 좌측: 페이지 리스트
        left_panel = QVBoxLayout()
        self.page_list = QListWidget()
        self.page_list.currentRowChanged.connect(self._on_page_selected)
        # 페이지 리스트 크기 제한 제거 (사용자 임의 조절 가능)
        from PySide6.QtWidgets import QSizePolicy
        list_size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.page_list.setSizePolicy(list_size_policy)
        left_panel.addWidget(QLabel("페이지 목록"))
        left_panel.addWidget(self.page_list)
        
        # 페이지 편집 버튼들
        button_layout = QHBoxLayout()
        self.btn_move_up = QPushButton("위로")
        self.btn_move_down = QPushButton("아래로")
        self.btn_delete = QPushButton("삭제")
        
        self.btn_move_up.clicked.connect(self.move_page_up)
        self.btn_move_down.clicked.connect(self.move_page_down)
        self.btn_delete.clicked.connect(self.delete_current_page)
        
        button_layout.addWidget(self.btn_move_up)
        button_layout.addWidget(self.btn_move_down)
        button_layout.addWidget(self.btn_delete)
        left_panel.addLayout(button_layout)
        
        # 페이지 추가 버튼
        self.btn_add_pages = QPushButton("페이지 추가")
        self.btn_add_pages.clicked.connect(self.insert_pages_from_other_pdf)
        left_panel.addWidget(self.btn_add_pages)
        
        # Undo 버튼 (저장/다른 이름으로 저장은 파일 메뉴에 있으므로 제거)
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.clicked.connect(self.undo_last_action)
        left_panel.addWidget(self.btn_undo)
        
        # 우측: PDF 뷰어
        right_panel = QVBoxLayout()
        
        # 그리기 도구 툴바 (컴팩트하게 재구성)
        tool_layout = QHBoxLayout()
        
        # 커서 버튼 (항상 표시)
        self.btn_tool_cursor = QPushButton("커서")
        self.btn_tool_cursor.setCheckable(True)
        self.btn_tool_cursor.setChecked(True)  # 디폴트로 커서 활성화
        self.btn_tool_cursor.clicked.connect(lambda: self._set_drawing_mode("cursor"))
        tool_layout.addWidget(self.btn_tool_cursor)
        
        # 필기 도구 드롭다운 메뉴
        from PySide6.QtWidgets import QComboBox
        self.drawing_tool_combo = QComboBox()
        self.drawing_tool_combo.addItem("선택", "select")
        self.drawing_tool_combo.addItem("펜", "pen")
        self.drawing_tool_combo.addItem("하이라이터", "highlighter")
        self.drawing_tool_combo.addItem("사각형", "rectangle")
        self.drawing_tool_combo.addItem("원", "ellipse")
        self.drawing_tool_combo.addItem("텍스트", "text")
        self.drawing_tool_combo.currentIndexChanged.connect(self._on_drawing_tool_changed)
        tool_layout.addWidget(QLabel("필기:"))
        tool_layout.addWidget(self.drawing_tool_combo)
        
        self.btn_clear_drawing = QPushButton("지우기")
        self.btn_clear_drawing.clicked.connect(self._clear_drawings)
        
        self.btn_delete_selected = QPushButton("선택 삭제")
        self.btn_delete_selected.clicked.connect(self._delete_selected_drawing)
        self.btn_delete_selected.setEnabled(False)
        
        self.btn_save_drawings = QPushButton("저장")
        self.btn_save_drawings.clicked.connect(self._save_drawings_to_pdf)
        
        # 색상 선택
        tool_layout.addWidget(QLabel("색상:"))
        self.color_group = QButtonGroup(self)
        self.btn_color_red = QPushButton("빨강")
        self.btn_color_red.setCheckable(True)
        self.btn_color_red.setChecked(True)
        self.btn_color_red.clicked.connect(lambda: self._set_drawing_color(QColor(255, 0, 0)))
        
        self.btn_color_blue = QPushButton("파랑")
        self.btn_color_blue.setCheckable(True)
        self.btn_color_blue.clicked.connect(lambda: self._set_drawing_color(QColor(0, 0, 255)))
        
        self.btn_color_black = QPushButton("검정")
        self.btn_color_black.setCheckable(True)
        self.btn_color_black.clicked.connect(lambda: self._set_drawing_color(QColor(0, 0, 0)))
        
        self.color_group.addButton(self.btn_color_red, 0)
        self.color_group.addButton(self.btn_color_blue, 1)
        self.color_group.addButton(self.btn_color_black, 2)
        
        tool_layout.addWidget(self.btn_color_red)
        tool_layout.addWidget(self.btn_color_blue)
        tool_layout.addWidget(self.btn_color_black)
        
        # 굵기 조절
        tool_layout.addWidget(QLabel("굵기:"))
        self.pen_width_spin = QSpinBox()
        self.pen_width_spin.setMinimum(1)
        self.pen_width_spin.setMaximum(20)
        self.pen_width_spin.setValue(3)
        self.pen_width_spin.valueChanged.connect(self._set_pen_width)
        tool_layout.addWidget(self.pen_width_spin)
        
        tool_layout.addWidget(self.btn_clear_drawing)
        tool_layout.addWidget(self.btn_delete_selected)
        tool_layout.addWidget(self.btn_save_drawings)
        tool_layout.addStretch()
        
        right_panel.addLayout(tool_layout)
        
        # 줌 컨트롤
        zoom_layout = QHBoxLayout()
        self.btn_zoom_out = QPushButton("−")
        self.btn_zoom_in = QPushButton("+")
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(60)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        
        self.btn_zoom_out.clicked.connect(self.zoom_out)
        self.btn_zoom_in.clicked.connect(self.zoom_in)
        
        zoom_layout.addWidget(self.btn_zoom_out)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(self.btn_zoom_in)
        zoom_layout.addStretch()
        
        right_panel.addLayout(zoom_layout)
        
        # PDF 뷰어와 그리기 레이어를 담을 컨테이너
        self.pdf_container = QWidget()
        pdf_container_layout = QVBoxLayout(self.pdf_container)
        pdf_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.pdf_view = QPdfView()
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.Custom)
        self.pdf_view.setZoomFactor(self._current_zoom)
        
        # 스크롤바 값 변경 감지
        scrollbar = self.pdf_view.verticalScrollBar()
        if scrollbar:
            scrollbar.valueChanged.connect(self._on_scroll_changed)
        
        pdf_container_layout.addWidget(self.pdf_view)
        
        # 그리기 레이어 (PDF 위에 올라감) - 컨테이너의 자식으로 생성하여 PDF 뷰어 위에 올림
        self.drawing_layer = DrawingLayer(self.pdf_container, pdf_view=self.pdf_view, pdf_doc=self._pdf_doc)
        self.drawing_layer.set_drawing_mode("cursor")  # 디폴트로 커서 모드
        self.drawing_layer.lower()  # 먼저 아래에 배치
        
        self.placeholder_label = QLabel("PDF를 열어주세요.")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        
        right_panel.addWidget(self.pdf_container)
        right_panel.addWidget(self.placeholder_label)
        
        # 좌우 크기 조절 가능하도록 위젯으로 감싸기
        # 좌측 패널: 고정 크기 (창 크기 조절 시 변하지 않음)
        left_panel_widget = QWidget()
        left_panel_widget.setLayout(left_panel)
        left_panel_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        left_panel_widget.setFixedWidth(200)  # 고정 너비 설정
        
        # 우측 패널: 확장 가능 (창 크기 조절 시 이 부분만 변함)
        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel)
        right_panel_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 우측 패널이 확장되도록 설정
        right_panel_widget.setMinimumWidth(400)  # 최소 너비만 설정
        
        root_layout.addWidget(left_panel_widget, 0)  # stretch factor 0 (고정)
        root_layout.addWidget(right_panel_widget, 1)  # stretch factor 1 (확장)
        
        self._update_placeholder_visibility()
    
    def _on_drawing_tool_changed(self, index):
        """필기 도구 드롭다운 변경 시 호출"""
        mode = self.drawing_tool_combo.itemData(index)
        if mode:
            self._set_drawing_mode(mode)
            # 커서 버튼 해제
            self.btn_tool_cursor.setChecked(False)
    
    def _on_scroll_changed(self, value):
        """스크롤 값 변경 시 현재 페이지 업데이트"""
        if not hasattr(self, 'drawing_layer') or self._pdf_doc.pageCount() == 0:
            return
        
        # 스크롤 위치를 기반으로 현재 보이는 페이지 계산
        # MultiPage 모드에서는 각 페이지가 세로로 배치됨
        scrollbar = self.pdf_view.verticalScrollBar()
        if scrollbar:
            scroll_pos = scrollbar.value()
            viewport_height = self.pdf_view.viewport().height()
            
            # 현재 보이는 영역의 중앙에 있는 페이지를 현재 페이지로 간주
            visible_center = scroll_pos + viewport_height / 2
            
            # 각 페이지의 대략적인 높이 계산 (정확하지 않을 수 있음)
            # PDF 뷰어의 전체 높이를 페이지 수로 나눔
            total_height = scrollbar.maximum() + viewport_height
            if total_height > 0 and self._pdf_doc.pageCount() > 0:
                page_height = total_height / self._pdf_doc.pageCount()
                estimated_page = int(visible_center / page_height) if page_height > 0 else 0
                estimated_page = max(0, min(estimated_page, self._pdf_doc.pageCount() - 1))
                
                # DrawingLayer의 현재 페이지 업데이트
                self.drawing_layer.set_current_page(estimated_page)
                
                # 필기 레이어 다시 그리기 (스크롤 위치 변경 반영)
                self.drawing_layer.update()
                
                # 왼쪽 리스트의 선택도 업데이트 (선택적으로)
                if self.page_list.currentRow() != estimated_page:
                    self.page_list.blockSignals(True)  # 시그널 차단하여 무한 루프 방지
                    self.page_list.setCurrentRow(estimated_page)
                    self.page_list.blockSignals(False)
    
    def get_file_path(self) -> Path | None:
        """현재 열린 파일 경로 반환"""
        return self._current_path
    
    def get_file_name(self) -> str:
        """탭 제목에 사용할 파일명 반환"""
        if self._current_path:
            return self._current_path.name
        return "새 문서"
    
    def load_pdf(self, file_path: Path):
        """PDF 파일 로드"""
        self._pdf_doc.load(str(file_path))
        
        if self._pdf_doc.pageCount() <= 0:
            return False
        
        self._current_path = file_path
        self.pdf_view.setDocument(self._pdf_doc)
        
        self._populate_page_list()
        if self._pdf_doc.pageCount() > 0:
            self.page_list.setCurrentRow(0)
        
        self._current_zoom = 1.0
        self.pdf_view.setZoomFactor(self._current_zoom)
        self._update_zoom_label()
        self._update_placeholder_visibility()
        
        # 그리기 레이어 초기화 및 첫 페이지 설정
        if hasattr(self, 'drawing_layer'):
            self.drawing_layer.pdf_doc = self._pdf_doc
            self.drawing_layer.pdf_view = self.pdf_view
            self.drawing_layer.set_pdf_path(file_path)
            self.drawing_layer.set_current_page(0)
        self._update_drawing_layer_size()
        
        return True
    
    def _populate_page_list(self):
        """페이지 번호 리스트 구성"""
        self.page_list.clear()
        if self._pdf_doc.pageCount() <= 0:
            return
        
        for i in range(self._pdf_doc.pageCount()):
            item = QListWidgetItem(f"페이지 {i + 1}")
            self.page_list.addItem(item)
    
    def _on_page_selected(self, index: int):
        """선택된 페이지 보여주기"""
        if index < 0 or index >= self._pdf_doc.pageCount():
            return
        
        nav = self.pdf_view.pageNavigator()
        if nav is not None:
            nav.jump(index, QPointF(0, 0), 0.0)
        
        # DrawingLayer의 현재 페이지 업데이트
        if hasattr(self, 'drawing_layer'):
            self.drawing_layer.set_current_page(index)
        
        self._update_placeholder_visibility()
    
    def _save_state_to_undo(self):
        """현재 상태를 undo 스택에 저장"""
        if self._current_path is None:
            return
        
        # 현재 PDF의 페이지 순서 저장
        reader = PdfReader(str(self._current_path))
        page_order = list(range(len(reader.pages)))
        
        # Undo 스택에 추가 (최대 10개)
        self._undo_stack.append({
            "path": Path(self._current_path),
            "page_order": page_order
        })
        
        if len(self._undo_stack) > self._max_undo:
            self._undo_stack.pop(0)  # 가장 오래된 것 제거
    
    def _rewrite_pdf_with_order(self, new_order: list[int], save_to_file: bool = False):
        """현재 PDF를 new_order 순서대로 다시 만든 파일로 교체하고 다시 로드"""
        if self._current_path is None:
            return
        
        # Undo 스택에 현재 상태 저장
        self._save_state_to_undo()
        
        reader = PdfReader(str(self._current_path))
        writer = PdfWriter()
        
        for idx in new_order:
            if 0 <= idx < len(reader.pages):
                writer.add_page(reader.pages[idx])
        
        if save_to_file:
            # 실제 파일로 저장
            edited_path = self._current_path.with_name(self._current_path.stem + "_edited.pdf")
            with edited_path.open("wb") as f:
                writer.write(f)
            self._current_path = edited_path
        else:
            # 임시 파일로 저장 (메모리만)
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.close()
            with open(temp_file.name, "wb") as f:
                writer.write(f)
            self._current_path = Path(temp_file.name)
        
        self._pdf_doc.load(str(self._current_path))
        
        self._populate_page_list()
        if self._pdf_doc.pageCount() > 0:
            self.page_list.setCurrentRow(0)
        self._update_placeholder_visibility()
        
        # 탭 제목 업데이트
        parent = self.parent()
        if parent:
            tab_widget = None
            while parent:
                if isinstance(parent, QTabWidget):
                    tab_widget = parent
                    break
                parent = parent.parent()
            
            if tab_widget:
                for i in range(tab_widget.count()):
                    if tab_widget.widget(i) == self:
                        tab_widget.setTabText(i, self.get_file_name())
                        break
    
    def delete_current_page(self):
        """현재 선택된 페이지 삭제"""
        if self._pdf_doc.pageCount() <= 1:
            QMessageBox.information(self, "안내", "삭제할 페이지가 없습니다.")
            return
        
        current = self.page_list.currentRow()
        if current < 0:
            return
        
        reply = QMessageBox.question(
            self,
            "페이지 삭제",
            f"{current + 1} 페이지를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        
        count = self._pdf_doc.pageCount()
        new_order = [i for i in range(count) if i != current]
        self._rewrite_pdf_with_order(new_order)
    
    def move_page_up(self):
        """현재 페이지를 한 칸 위로 이동"""
        current = self.page_list.currentRow()
        count = self._pdf_doc.pageCount()
        if current <= 0 or count <= 1:
            return
        
        order = list(range(count))
        order[current - 1], order[current] = order[current], order[current - 1]
        self._rewrite_pdf_with_order(order)
        self.page_list.setCurrentRow(current - 1)
    
    def move_page_down(self):
        """현재 페이지를 한 칸 아래로 이동"""
        current = self.page_list.currentRow()
        count = self._pdf_doc.pageCount()
        if current < 0 or current >= count - 1 or count <= 1:
            return
        
        order = list(range(count))
        order[current + 1], order[current] = order[current], order[current + 1]
        self._rewrite_pdf_with_order(order)
        self.page_list.setCurrentRow(current + 1)
    
    def insert_pages_from_other_pdf(self):
        """다른 PDF에서 페이지를 가져와서 삽입"""
        if self._current_path is None:
            QMessageBox.information(self, "안내", "먼저 PDF 파일을 열어주세요.")
            return
        
        source_file, _ = QFileDialog.getOpenFileName(
            self,
            "페이지를 가져올 PDF 선택",
            "",
            "PDF 파일 (*.pdf)",
        )
        if not source_file:
            return
        
        try:
            source_reader = PdfReader(source_file)
            source_page_count = len(source_reader.pages)
            if source_page_count == 0:
                QMessageBox.warning(self, "오류", "선택한 PDF에 페이지가 없습니다.")
                return
        except Exception as e:
            QMessageBox.critical(self, "오류", f"PDF 파일을 읽는 중 오류가 발생했습니다:\n{str(e)}")
            return
        
        dialog = InsertPagesDialog(self, source_page_count)
        if dialog.exec() != QDialog.Accepted:
            return
        
        page_range = dialog.get_page_range()
        if page_range is None:
            QMessageBox.warning(self, "오류", "잘못된 페이지 범위입니다.")
            return
        
        start_idx, end_idx = page_range
        if start_idx < 0 or end_idx >= source_page_count or start_idx > end_idx:
            QMessageBox.warning(self, "오류", "잘못된 페이지 범위입니다.")
            return
        
        insert_pos = dialog.get_insert_position()
        current_idx = self.page_list.currentRow()
        
        current_reader = PdfReader(str(self._current_path))
        writer = PdfWriter()
        
        if insert_pos == 'end':
            for page in current_reader.pages:
                writer.add_page(page)
            for i in range(start_idx, end_idx + 1):
                writer.add_page(source_reader.pages[i])
            new_selection = len(current_reader.pages) + (end_idx - start_idx)
        elif insert_pos == 'before':
            for i, page in enumerate(current_reader.pages):
                if i == current_idx:
                    for j in range(start_idx, end_idx + 1):
                        writer.add_page(source_reader.pages[j])
                writer.add_page(page)
            new_selection = current_idx + (end_idx - start_idx + 1)
        else:  # 'after'
            for i, page in enumerate(current_reader.pages):
                writer.add_page(page)
                if i == current_idx:
                    for j in range(start_idx, end_idx + 1):
                        writer.add_page(source_reader.pages[j])
            new_selection = current_idx + 1
        
        # Undo 스택에 현재 상태 저장
        self._save_state_to_undo()
        
        # 임시 파일로 저장 (자동 저장하지 않음)
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        with open(temp_file.name, "wb") as f:
            writer.write(f)
        
        self._current_path = Path(temp_file.name)
        self._pdf_doc.load(str(self._current_path))
        self.pdf_view.setDocument(self._pdf_doc)
        
        self._populate_page_list()
        if 0 <= new_selection < self._pdf_doc.pageCount():
            self.page_list.setCurrentRow(new_selection)
        
        self.pdf_view.setZoomFactor(self._current_zoom)
        self._update_placeholder_visibility()
        self._update_drawing_layer_size()
        
        # 탭 제목 업데이트
        parent = self.parent()
        if parent:
            tab_widget = None
            while parent:
                if isinstance(parent, QTabWidget):
                    tab_widget = parent
                    break
                parent = parent.parent()
            
            if tab_widget:
                for i in range(tab_widget.count()):
                    if tab_widget.widget(i) == self:
                        tab_widget.setTabText(i, self.get_file_name())
                        break
        
        QMessageBox.information(
            self,
            "완료",
            f"{end_idx - start_idx + 1}개의 페이지가 추가되었습니다.\n저장 버튼을 눌러 저장하세요."
        )
    
    def zoom_in(self):
        """확대"""
        self._current_zoom = min(self._current_zoom * 1.2, 5.0)
        self.pdf_view.setZoomFactor(self._current_zoom)
        self._update_zoom_label()
        self._update_drawing_layer_size()
        # 필기 레이어 다시 그리기 (줌 변경 반영)
        if hasattr(self, 'drawing_layer'):
            self.drawing_layer.update()
    
    def zoom_out(self):
        """축소"""
        self._current_zoom = max(self._current_zoom / 1.2, 0.1)
        self.pdf_view.setZoomFactor(self._current_zoom)
        self._update_zoom_label()
        self._update_drawing_layer_size()
        # 필기 레이어 다시 그리기 (줌 변경 반영)
        if hasattr(self, 'drawing_layer'):
            self.drawing_layer.update()
    
    def _update_zoom_label(self):
        """줌 레벨 표시 업데이트"""
        zoom_percent = int(self._current_zoom * 100)
        self.zoom_label.setText(f"{zoom_percent}%")
    
    def _update_placeholder_visibility(self):
        has_doc = self._pdf_doc.pageCount() > 0
        self.pdf_view.setVisible(has_doc)
        self.pdf_container.setVisible(has_doc)
        self.placeholder_label.setVisible(not has_doc)
        if not has_doc:
            self.placeholder_label.setText("PDF를 열어주세요.")
        else:
            # 그리기 레이어 크기 조정
            self._update_drawing_layer_size()
    
    def _update_drawing_layer_size(self):
        """그리기 레이어 크기를 PDF 뷰어와 동일하게 조정"""
        if self.drawing_layer and self.pdf_view and self.pdf_container:
            # PDF 뷰어의 위치와 크기를 컨테이너 기준으로 가져옴
            view_rect = self.pdf_view.geometry()
            # 컨테이너 내에서의 상대 위치
            self.drawing_layer.setGeometry(view_rect)
            self.drawing_layer.raise_()  # PDF 뷰어 위에 올림
            self.drawing_layer.show()
    
    def _set_drawing_mode(self, mode: str):
        """그리기 모드 설정"""
        self.drawing_layer.set_drawing_mode(mode)
        
        # 커서 모드일 때는 커서 버튼 활성화, 필기 도구 드롭다운은 초기화
        if mode == "cursor":
            self.btn_tool_cursor.setChecked(True)
            self.drawing_tool_combo.setCurrentIndex(0)  # 첫 번째 항목으로 초기화
        else:
            # 필기 모드일 때는 커서 버튼 해제, 드롭다운에서 해당 모드 선택
            self.btn_tool_cursor.setChecked(False)
            # 드롭다운에서 해당 모드 찾기
            for i in range(self.drawing_tool_combo.count()):
                if self.drawing_tool_combo.itemData(i) == mode:
                    self.drawing_tool_combo.setCurrentIndex(i)
                    break
        
        # 선택 모드로 전환 시 선택 삭제 버튼 상태 업데이트
        if mode == "select":
            if hasattr(self.drawing_layer, 'selected_drawing_index'):
                self.btn_delete_selected.setEnabled(self.drawing_layer.selected_drawing_index is not None)
        else:
            # 다른 모드로 전환 시 선택 해제
            if hasattr(self.drawing_layer, 'selected_drawing_index'):
                self.drawing_layer.selected_drawing_index = None
            self.btn_delete_selected.setEnabled(False)
    
    def _set_drawing_color(self, color: QColor):
        """그리기 색상 설정"""
        self.drawing_layer.set_color(color)
    
    def _set_pen_width(self, width: int):
        """펜 굵기 설정"""
        self.drawing_layer.set_pen_width(width)
    
    def _clear_drawings(self):
        """그린 내용 모두 지우기"""
        reply = QMessageBox.question(
            self,
            "확인",
            "그린 내용을 모두 지우시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.drawing_layer.clear_drawings()
    
    def _delete_selected_drawing(self):
        """선택된 필기 삭제 (같은 그룹의 모든 필기 함께 삭제)"""
        if hasattr(self.drawing_layer, 'selected_drawing_index') and self.drawing_layer.selected_drawing_index is not None:
            current_drawings = self.drawing_layer.get_current_page_drawings()
            if 0 <= self.drawing_layer.selected_drawing_index < len(current_drawings):
                # 같은 그룹의 모든 필기 찾기
                selected_group_id = self.drawing_layer.selected_group_id
                indices_to_delete = []
                
                if selected_group_id is not None:
                    # 같은 그룹의 모든 필기 인덱스 찾기
                    page_groups = self.drawing_layer._drawing_groups.get(self.drawing_layer.current_page_index, {})
                    if selected_group_id in page_groups:
                        indices_to_delete = sorted(page_groups[selected_group_id], reverse=True)  # 역순으로 정렬 (뒤에서부터 삭제)
                else:
                    # 그룹 ID가 없으면 선택된 필기만 삭제
                    indices_to_delete = [self.drawing_layer.selected_drawing_index]
                
                if indices_to_delete:
                    reply = QMessageBox.question(
                        self,
                        "확인",
                        f"선택된 필기{'들' if len(indices_to_delete) > 1 else ''}을 삭제하시겠습니까?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No,
                    )
                    if reply == QMessageBox.Yes:
                        # 같은 그룹의 모든 필기 삭제
                        for idx in indices_to_delete:
                            if 0 <= idx < len(current_drawings):
                                current_drawings.pop(idx)
                        
                        # 그룹 정보에서 삭제
                        if selected_group_id is not None:
                            page_groups = self.drawing_layer._drawing_groups.get(self.drawing_layer.current_page_index, {})
                            if selected_group_id in page_groups:
                                del page_groups[selected_group_id]
                        
                        # 다른 그룹의 인덱스들 재조정 (삭제된 필기 이후의 인덱스들을 조정)
                        for group_id, indices in self.drawing_layer._drawing_groups.get(self.drawing_layer.current_page_index, {}).items():
                            for i in range(len(indices)):
                                deleted_count = sum(1 for del_idx in indices_to_delete if del_idx < indices[i])
                                indices[i] -= deleted_count
                        
                        self.drawing_layer.selected_drawing_index = None
                        self.drawing_layer.selected_group_id = None
                        self.drawing_layer.update()
                        self.btn_delete_selected.setEnabled(False)
                        QMessageBox.information(self, "완료", f"선택된 필기{'들' if len(indices_to_delete) > 1 else ''}이 삭제되었습니다.")
    
    def _save_drawings_to_pdf(self):
        """그린 내용을 PDF에 저장"""
        if self._current_path is None:
            QMessageBox.information(self, "안내", "먼저 PDF 파일을 열어주세요.")
            return
        
        drawings = self.drawing_layer.get_drawings()
        if not drawings:
            QMessageBox.information(self, "안내", "저장할 그린 내용이 없습니다.")
            return
        
        try:
            # PyMuPDF로 PDF 열기
            doc = fitz.open(str(self._current_path))
            
            # 현재 보이는 페이지에 그린 내용 추가
            current_page_idx = self.page_list.currentRow()
            if 0 <= current_page_idx < len(doc):
                page = doc[current_page_idx]
                
                # 모든 페이지의 필기를 저장
                for page_idx, page_drawings in self.drawing_layer.drawn_paths_by_page.items():
                    if 0 <= page_idx < len(doc):
                        page = doc[page_idx]
                        
                        for drawing in page_drawings:
                            color = drawing["color"]
                            width = drawing["width"]
                            
                            # 색상 변환 (QColor -> fitz color)
                            fitz_color = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0)
                            
                            if drawing["type"] in ["pen", "highlighter"]:
                                # 자유 그리기 (이미 PDF 좌표)
                                path = drawing["path"]
                                if len(path) > 1:
                                    points = []
                                    for pt in path:
                                        # QPointF를 튜플로 변환
                                        points.append((pt.x(), pt.y()))
                                    
                                    if drawing["type"] == "highlighter":
                                        # 하이라이터는 두꺼운 선
                                        page.draw_polyline(points, color=fitz_color, width=width, closePath=False)
                                    else:
                                        # 펜은 일반 선
                                        page.draw_polyline(points, color=fitz_color, width=width, closePath=False)
                            
                            elif drawing["type"] == "rectangle":
                                # 이미 PDF 좌표
                                start = drawing["start"]
                                end = drawing["end"]
                                rect = fitz.Rect(
                                    start.x(),
                                    start.y(),
                                    end.x(),
                                    end.y()
                                )
                                page.draw_rect(rect, color=fitz_color, width=width)
                            
                            elif drawing["type"] == "ellipse":
                                # 이미 PDF 좌표
                                start = drawing["start"]
                                end = drawing["end"]
                                rect = fitz.Rect(
                                    min(start.x(), end.x()),
                                    min(start.y(), end.y()),
                                    max(start.x(), end.x()),
                                    max(start.y(), end.y())
                                )
                                page.draw_oval(rect, color=fitz_color, width=width)
                            
                            elif drawing["type"] == "text":
                                # 텍스트 추가 (이미 PDF 좌표)
                                pos = drawing["position"]
                                text = drawing["text"]
                                point = fitz.Point(pos.x(), pos.y())
                                # width가 폰트 크기 (포인트)
                                page.insert_text(
                                    point,
                                    text,
                                    fontsize=width,
                                    color=fitz_color
                                )
            
            # 저장
            edited_path = self._current_path.with_name(self._current_path.stem + "_edited.pdf")
            doc.save(str(edited_path))
            doc.close()
            
            # 다시 로드
            self._current_path = edited_path
            self._pdf_doc.load(str(self._current_path))
            self.pdf_view.setDocument(self._pdf_doc)
            
            self._populate_page_list()
            if 0 <= current_page_idx < self._pdf_doc.pageCount():
                self.page_list.setCurrentRow(current_page_idx)
            
            # 그린 내용 지우기
            self.drawing_layer.clear_drawings()
            
            # 탭 제목 업데이트
            parent = self.parent()
            if parent:
                tab_widget = None
                while parent:
                    if isinstance(parent, QTabWidget):
                        tab_widget = parent
                        break
                    parent = parent.parent()
                
                if tab_widget:
                    for i in range(tab_widget.count()):
                        if tab_widget.widget(i) == self:
                            tab_widget.setTabText(i, self.get_file_name())
                            break
            
            QMessageBox.information(self, "완료", "그린 내용이 PDF에 저장되었습니다.")
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "오류",
                f"PDF 저장 중 오류가 발생했습니다:\n{str(e)}"
            )
    
    def extract_page_range(self):
        """현재 PDF의 특정 페이지 범위만 저장"""
        if self._current_path is None:
            QMessageBox.information(self, "안내", "먼저 PDF 파일을 열어주세요.")
            return
        
        total_pages = self._pdf_doc.pageCount()
        if total_pages == 0:
            QMessageBox.information(self, "안내", "저장할 페이지가 없습니다.")
            return
        
        dialog = ExtractPagesDialog(self, total_pages)
        if dialog.exec() != QDialog.Accepted:
            return
        
        page_range = dialog.get_page_range()
        if page_range is None:
            QMessageBox.warning(self, "오류", "잘못된 페이지 범위입니다.")
            return
        
        start_page, end_page = page_range
        if start_page < 1 or end_page > total_pages or start_page > end_page:
            QMessageBox.warning(self, "오류", "잘못된 페이지 범위입니다.")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "페이지 범위 저장",
            "",
            "PDF 파일 (*.pdf)",
        )
        
        if not save_path:
            return
        
        try:
            reader = PdfReader(str(self._current_path))
            writer = PdfWriter()
            
            start_idx = start_page - 1
            end_idx = end_page - 1
            
            for i in range(start_idx, end_idx + 1):
                writer.add_page(reader.pages[i])
            
            with open(save_path, "wb") as f:
                writer.write(f)
            
            QMessageBox.information(
                self,
                "완료",
                f"{start_page}페이지부터 {end_page}페이지까지 저장되었습니다.\n총 {end_page - start_page + 1}페이지입니다."
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "오류",
                f"페이지 범위를 저장하는 중 오류가 발생했습니다:\n{str(e)}"
            )
    
    def undo_last_action(self):
        """마지막 작업 취소"""
        if not self._undo_stack:
            QMessageBox.information(self, "안내", "취소할 작업이 없습니다.")
            return
        
        # 마지막 상태 복원
        last_state = self._undo_stack.pop()
        
        try:
            # 이전 상태로 복원
            self._current_path = last_state["path"]
            self._pdf_doc.load(str(self._current_path))
            self.pdf_view.setDocument(self._pdf_doc)
            
            self._populate_page_list()
            if self._pdf_doc.pageCount() > 0:
                self.page_list.setCurrentRow(0)
            
            self._update_placeholder_visibility()
            self._update_drawing_layer_size()
            
            # 탭 제목 업데이트
            parent = self.parent()
            if parent:
                tab_widget = None
                while parent:
                    if isinstance(parent, QTabWidget):
                        tab_widget = parent
                        break
                    parent = parent.parent()
                
                if tab_widget:
                    for i in range(tab_widget.count()):
                        if tab_widget.widget(i) == self:
                            tab_widget.setTabText(i, self.get_file_name())
                            break
            
            QMessageBox.information(self, "완료", "작업이 취소되었습니다.")
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "오류",
                f"작업 취소 중 오류가 발생했습니다:\n{str(e)}"
            )
    
    def save_pdf(self):
        """현재 PDF 저장 (필기 내용 포함)"""
        if self._current_path is None:
            QMessageBox.information(self, "안내", "저장할 파일이 없습니다.")
            return
        
        try:
            # 임시 파일이면 다른 이름으로 저장 다이얼로그 표시
            if "temp" in str(self._current_path) or not self._current_path.name.endswith(".pdf"):
                self.save_pdf_as()
                return
            
            # PyMuPDF로 PDF 열기 (필기 내용 포함)
            doc = fitz.open(str(self._current_path))
            
            # 모든 페이지의 필기를 저장
            if hasattr(self, 'drawing_layer'):
                for page_idx, page_drawings in self.drawing_layer.drawn_paths_by_page.items():
                    if 0 <= page_idx < len(doc):
                        page = doc[page_idx]
                        
                        for drawing in page_drawings:
                            color = drawing["color"]
                            width = drawing["width"]
                            
                            # 색상 변환 (QColor -> fitz color)
                            fitz_color = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0)
                            
                            if drawing["type"] in ["pen", "highlighter"]:
                                # 자유 그리기 (이미 PDF 좌표)
                                path = drawing["path"]
                                if len(path) > 1:
                                    points = []
                                    for pt in path:
                                        # QPointF를 튜플로 변환
                                        points.append((pt.x(), pt.y()))
                                    
                                    if drawing["type"] == "highlighter":
                                        # 하이라이터는 두꺼운 선
                                        page.draw_polyline(points, color=fitz_color, width=width, closePath=False)
                                    else:
                                        # 펜은 일반 선
                                        page.draw_polyline(points, color=fitz_color, width=width, closePath=False)
                            
                            elif drawing["type"] == "rectangle":
                                # 이미 PDF 좌표
                                start = drawing["start"]
                                end = drawing["end"]
                                rect = fitz.Rect(
                                    start.x(),
                                    start.y(),
                                    end.x(),
                                    end.y()
                                )
                                page.draw_rect(rect, color=fitz_color, width=width)
                            
                            elif drawing["type"] == "ellipse":
                                # 이미 PDF 좌표
                                start = drawing["start"]
                                end = drawing["end"]
                                rect = fitz.Rect(
                                    min(start.x(), end.x()),
                                    min(start.y(), end.y()),
                                    max(start.x(), end.x()),
                                    max(start.y(), end.y())
                                )
                                page.draw_oval(rect, color=fitz_color, width=width)
                            
                            elif drawing["type"] == "text":
                                # 텍스트 추가 (이미 PDF 좌표)
                                pos = drawing["position"]
                                text = drawing["text"]
                                point = fitz.Point(pos.x(), pos.y())
                                # width가 폰트 크기 (포인트)
                                page.insert_text(
                                    point,
                                    text,
                                    fontsize=width,
                                    color=fitz_color
                                )
            
            # 원본 파일에 저장
            doc.save(str(self._current_path))
            doc.close()
            
            QMessageBox.information(self, "완료", "파일이 저장되었습니다.")
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "오류",
                f"파일 저장 중 오류가 발생했습니다:\n{str(e)}"
            )
    
    def save_pdf_as(self):
        """다른 이름으로 저장 (필기 내용 포함)"""
        if self._current_path is None:
            QMessageBox.information(self, "안내", "저장할 파일이 없습니다.")
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "다른 이름으로 저장",
            str(self._current_path) if self._current_path else "",
            "PDF 파일 (*.pdf)",
        )
        
        if not save_path:
            return
        
        try:
            # PyMuPDF로 PDF 열기 (필기 내용 포함)
            doc = fitz.open(str(self._current_path))
            
            # 모든 페이지의 필기를 저장
            if hasattr(self, 'drawing_layer'):
                for page_idx, page_drawings in self.drawing_layer.drawn_paths_by_page.items():
                    if 0 <= page_idx < len(doc):
                        page = doc[page_idx]
                        
                        for drawing in page_drawings:
                            color = drawing["color"]
                            width = drawing["width"]
                            
                            # 색상 변환 (QColor -> fitz color)
                            fitz_color = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0)
                            
                            if drawing["type"] in ["pen", "highlighter"]:
                                # 자유 그리기 (이미 PDF 좌표)
                                path = drawing["path"]
                                if len(path) > 1:
                                    points = []
                                    for pt in path:
                                        # QPointF를 튜플로 변환
                                        points.append((pt.x(), pt.y()))
                                    
                                    if drawing["type"] == "highlighter":
                                        # 하이라이터는 두꺼운 선
                                        page.draw_polyline(points, color=fitz_color, width=width, closePath=False)
                                    else:
                                        # 펜은 일반 선
                                        page.draw_polyline(points, color=fitz_color, width=width, closePath=False)
                            
                            elif drawing["type"] == "rectangle":
                                # 이미 PDF 좌표
                                start = drawing["start"]
                                end = drawing["end"]
                                rect = fitz.Rect(
                                    start.x(),
                                    start.y(),
                                    end.x(),
                                    end.y()
                                )
                                page.draw_rect(rect, color=fitz_color, width=width)
                            
                            elif drawing["type"] == "ellipse":
                                # 이미 PDF 좌표
                                start = drawing["start"]
                                end = drawing["end"]
                                rect = fitz.Rect(
                                    min(start.x(), end.x()),
                                    min(start.y(), end.y()),
                                    max(start.x(), end.x()),
                                    max(start.y(), end.y())
                                )
                                page.draw_oval(rect, color=fitz_color, width=width)
                            
                            elif drawing["type"] == "text":
                                # 텍스트 추가 (이미 PDF 좌표)
                                pos = drawing["position"]
                                text = drawing["text"]
                                point = fitz.Point(pos.x(), pos.y())
                                # width가 폰트 크기 (포인트)
                                page.insert_text(
                                    point,
                                    text,
                                    fontsize=width,
                                    color=fitz_color
                                )
            
            # 저장
            doc.save(str(save_path))
            doc.close()
            
            self._current_path = Path(save_path)
            self._pdf_doc.load(str(self._current_path))
            self.pdf_view.setDocument(self._pdf_doc)
            
            # DrawingLayer의 PDF 경로 업데이트
            if hasattr(self, 'drawing_layer'):
                self.drawing_layer.set_pdf_path(self._current_path)
            
            # 탭 제목 업데이트
            parent = self.parent()
            if parent:
                tab_widget = None
                while parent:
                    if isinstance(parent, QTabWidget):
                        tab_widget = parent
                        break
                    parent = parent.parent()
                
                if tab_widget:
                    for i in range(tab_widget.count()):
                        if tab_widget.widget(i) == self:
                            tab_widget.setTabText(i, self.get_file_name())
                            break
            
            QMessageBox.information(self, "완료", "파일이 저장되었습니다.")
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "오류",
                f"파일 저장 중 오류가 발생했습니다:\n{str(e)}"
            )


class PdfEditorMainWindow(QMainWindow):
    """
    탭 기반 PDF 편집기 메인 윈도우
    - 여러 PDF 문서를 탭으로 관리
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("서울자가김부장용PDF편집기 Ver 1.3")
        self.resize(1200, 800)

        self._setup_ui()
        self._create_actions()
        self._create_menus()
        
        # 초기 탭 추가
        self._add_new_tab()

    # ---------- UI 구성 ----------
    def _setup_ui(self):
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        # 크기 정책 설정 (좌우 확장 가능)
        from PySide6.QtWidgets import QSizePolicy
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab_widget.setSizePolicy(size_policy)
        self.setCentralWidget(self.tab_widget)

    def _create_actions(self):
        self.open_action = QAction("열기(&O)", self)
        self.open_action.triggered.connect(self.open_pdf)
        
        self.new_tab_action = QAction("새 탭(&N)", self)
        self.new_tab_action.triggered.connect(self._add_new_tab)

        self.merge_pdfs_action = QAction("여러 PDF 합치기(&M)", self)
        self.merge_pdfs_action.triggered.connect(self.merge_multiple_pdfs)

        self.extract_pages_action = QAction("페이지 범위 저장(&E)", self)
        self.extract_pages_action.triggered.connect(self.extract_page_range)
        
        self.save_action = QAction("저장(&S)", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self._save_current_tab)
        
        self.save_as_action = QAction("다른 이름으로 저장(&A)", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.triggered.connect(self._save_as_current_tab)

        self.exit_action = QAction("종료(&X)", self)
        self.exit_action.triggered.connect(self.close)

    def _create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("파일(&F)")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.new_tab_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.merge_pdfs_action)
        file_menu.addAction(self.extract_pages_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
    
    # ---------- 탭 관리 ----------
    def _add_new_tab(self, file_path: Path | None = None):
        """새 탭 추가"""
        tab = PdfEditorTab(self)
        tab_index = self.tab_widget.addTab(tab, "새 문서")
        self.tab_widget.setCurrentIndex(tab_index)
        
        if file_path:
            if tab.load_pdf(file_path):
                self.tab_widget.setTabText(tab_index, tab.get_file_name())
            else:
                QMessageBox.critical(
                    self,
                    "오류",
                    "PDF를 여는 중 오류가 발생했습니다.\n다른 파일로 다시 시도해 보세요.",
                )
                self._close_tab(tab_index)
                return
        
        return tab
    
    def _close_tab(self, index: int):
        """탭 닫기"""
        if self.tab_widget.count() <= 1:
            QMessageBox.information(self, "안내", "최소 하나의 탭은 열려있어야 합니다.")
            return
        
        self.tab_widget.removeTab(index)
    
    def _on_tab_changed(self, index: int):
        """탭 변경 시 호출"""
        if index >= 0:
            tab = self.tab_widget.widget(index)
            if tab and isinstance(tab, PdfEditorTab):
                # 탭 제목 업데이트
                self.tab_widget.setTabText(index, tab.get_file_name())
    
    def _get_current_tab(self) -> PdfEditorTab | None:
        """현재 활성 탭 반환"""
        current_index = self.tab_widget.currentIndex()
        if current_index < 0:
            return None
        tab = self.tab_widget.widget(current_index)
        if isinstance(tab, PdfEditorTab):
            return tab
        return None

    # ---------- 동작 ----------
    def open_pdf(self):
        """새 탭에 PDF 열기"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "PDF 열기",
            "",
            "PDF 파일 (*.pdf)",
        )
        if not file_path:
            return
        
        file_path_obj = Path(file_path)
        # 항상 새 탭에 열기
        self._add_new_tab(file_path_obj)
    
    # ---------- PDF 합치기 / 나누기 ----------
    def merge_multiple_pdfs(self):
        """여러 PDF 파일을 하나로 합치기"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "합칠 PDF 파일 선택",
            "",
            "PDF 파일 (*.pdf)",
        )
        
        if len(file_paths) < 2:
            QMessageBox.information(
                self,
                "안내",
                "합치려면 최소 2개 이상의 PDF 파일을 선택해야 합니다."
            )
            return
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "합친 PDF 저장",
            "",
            "PDF 파일 (*.pdf)",
        )
        
        if not save_path:
            return
        
        writer = PdfWriter()
        total_pages = 0
        
        try:
            for file_path in file_paths:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    writer.add_page(page)
                    total_pages += 1
            
            with open(save_path, "wb") as f:
                writer.write(f)
            
            QMessageBox.information(
                self,
                "완료",
                f"{len(file_paths)}개의 PDF 파일이 합쳐져서 저장되었습니다.\n총 {total_pages}페이지입니다."
            )
            
            reply = QMessageBox.question(
                self,
                "파일 열기",
                "합친 PDF 파일을 지금 열까요?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            
            if reply == QMessageBox.Yes:
                self._add_new_tab(Path(save_path))
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "오류",
                f"PDF 파일을 합치는 중 오류가 발생했습니다:\n{str(e)}"
            )
    
    def extract_page_range(self):
        """현재 탭의 PDF에서 특정 페이지 범위만 저장"""
        tab = self._get_current_tab()
        if not tab:
            return
        
        tab.extract_page_range()
    
    def _save_current_tab(self):
        """현재 탭의 PDF 저장"""
        tab = self._get_current_tab()
        if not tab:
            QMessageBox.information(self, "안내", "저장할 파일이 없습니다.")
            return
        
        tab.save_pdf()
    
    def _save_as_current_tab(self):
        """현재 탭의 PDF를 다른 이름으로 저장"""
        tab = self._get_current_tab()
        if not tab:
            QMessageBox.information(self, "안내", "저장할 파일이 없습니다.")
            return
        
        tab.save_pdf_as()


def main():
    app = QApplication(sys.argv)
    window = PdfEditorMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()



