import fitz  # PyMuPDF
import os

## ----------------- 설정 ----------------- ##
source_pdf_path = "Diffusion Policy.pdf"
output_pdf_path = "Diffusion Policy_blocks_highlighted.pdf"

# 각 요소 타입별 테두리 색상 (R, G, B 형식, 0~1 사이 값)
# fitz.utils.getColor("red") 와 같이 색상 이름을 사용할 수도 있습니다.
COLOR_MAP = {
    "text": (1, 0, 0),  # Red
    "image": (0, 0, 1),  # Blue
    "drawing": (0, 1, 0),  # Green
}
BORDER_WIDTH = 0.5  # 테두리 두께
## ---------------------------------------- ##

try:
    # 원본 PDF 문서를 엽니다.
    doc = fitz.open(source_pdf_path)
    print(f"'{source_pdf_path}' 파일을 열었습니다. 블록 시각화 작업을 시작합니다...")

    # 모든 페이지를 순회합니다.
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # 1. 페이지의 모든 시각적 요소를 수집합니다 (기존 로직과 동일).
        all_elements = []
        text_blocks = [
            b for b in page.get_text("dict").get("blocks", []) if b["type"] == 0
        ]
        for block in text_blocks:
            all_elements.append({"bbox": fitz.Rect(block["bbox"]), "type": "text"})
        for img in page.get_images(full=True):
            try:
                all_elements.append({"bbox": page.get_image_bbox(img), "type": "image"})
            except ValueError:
                continue
        for drawing in page.get_drawings():
            all_elements.append({"bbox": drawing["rect"], "type": "drawing"})

        print(
            f"  - {page_num + 1} 페이지: {len(all_elements)}개의 요소를 발견했습니다. 테두리를 그립니다..."
        )

        # 2. 수집된 모든 요소의 경계 상자(bbox)에 사각형을 그립니다.
        for element in all_elements:
            bbox = element["bbox"]
            element_type = element["type"]
            color = COLOR_MAP.get(
                element_type, (0, 0, 0)
            )  # 딕셔너리에 없는 타입은 검은색

            # page.draw_rect() 함수로 사각형을 그립니다.
            page.draw_rect(bbox, color=color, width=BORDER_WIDTH)

    # 3. 변경사항을 새로운 PDF 파일로 저장합니다.
    # garbage=4, deflate=True 옵션은 파일을 최적화하고 압축하여 용량을 줄여줍니다.
    doc.save(output_pdf_path, garbage=4, deflate=True)
    print(
        f"\n[성공] 모든 블록에 테두리를 그린 '{output_pdf_path}' 파일을 생성했습니다."
    )
    doc.close()

except Exception as e:
    print(f"오류가 발생했습니다: {e}")
