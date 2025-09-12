import fitz  # PyMuPDF 라이브러리

# 분석하고 싶은 PDF 파일 경로를 지정해주세요.
pdf_path = "HIQL.pdf"

try:
    doc = fitz.open(pdf_path)
    print(f"'{pdf_path}' 파일의 문단별 특징 분석 시작...")

    # 문서의 모든 페이지를 순회합니다.
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        print(f"\n--- [{page_num + 1} 페이지] ---")

        # 페이지의 상세 텍스트 정보를 사전(dict) 형태로 가져옵니다.
        blocks = page.get_text("dict").get("blocks", [])

        # 텍스트 블록(문단)만 필터링합니다.
        text_blocks = [b for b in blocks if b["type"] == 0]

        if not text_blocks:
            print("  -> 이 페이지에는 텍스트 문단이 없습니다.")
            continue

        # 각 텍스트 문단을 순회하면서 가장 많이 사용된 폰트의 크기를 확인합니다.
        font_count = {}
        for i, block in enumerate(text_blocks):
            if not block["lines"] or not block["lines"][0]["spans"]:
                continue

            first_span = block["lines"][0]["spans"][0]

            font_size = round(first_span["spans"][0])

        # 각 텍스트 문단을 순회합니다.
        for i, block in enumerate(text_blocks):
            # 문단의 첫 줄, 첫 스팬(글자 형식 단위)에서 주요 특징을 추출합니다.
            if not block["lines"] or not block["lines"][0]["spans"]:
                continue

            first_span = block["lines"][0]["spans"][0]

            # 특징 추출
            font_size = round(first_span["size"], 1)
            font_name = first_span["font"]
            # 폰트 플래그 '16'은 'bold'를 의미합니다.
            is_bold = "Bold" in font_name or (first_span["flags"] & 16)
            bbox = [round(c) for c in block["bbox"]]  # 위치 좌표 (반올림)

            # 문단 전체 텍스트를 조합하고 첫 3단어를 추출합니다.
            full_text = " ".join(
                span["text"] for line in block["lines"] for span in line["spans"]
            )
            words = full_text.replace("\n", " ").split()
            first_three_words = " ".join(words[:3])

            # 특징들을 보기 좋게 출력합니다.
            style = "Bold" if is_bold else "Regular"
            print(f'  문단 #{i+1}: "{first_three_words}..."')
            print(
                f"    - 특징: 크기({font_size}pt), 스타일({style}), 글꼴({font_name}), 위치({bbox})"
            )

    doc.close()

except FileNotFoundError:
    print(f"오류: '{pdf_path}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
except Exception as e:
    print(f"오류가 발생했습니다: {e}")
