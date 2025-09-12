import fitz

pdf_path = "HIQL.pdf"

# list of tuples that store the information as (text, font size, font name)
results = []

pdf = fitz.open(pdf_path)  # filePath is a string that contains the path to the pdf
# for page in pdf:
for page_num in range(min(2, len(pdf))):
    print(f"--- [{page_num + 1} 페이지] ---")
    page = pdf.load_page(page_num)
    blocks = page.get_text("dict").get("blocks", [])
    text_blocks = [b for b in blocks if b["type"] == 0]

    if not text_blocks:
        print("  -> 이 페이지에는 텍스트 문단이 없습니다.")
        continue

    for i, block in enumerate(text_blocks):
        if not block["lines"] or not block["lines"][0]["spans"]:
            continue

        first_span = block["lines"][0]["spans"][0]
        results.append((first_span["text"], first_span["size"], first_span["font"]))

    # dict = page.get_text("dict")
    # blocks = dict["blocks"]
    # for block in blocks:
    #     if "lines" in block.keys():
    #         spans = block["lines"]
    #         for span in spans:
    #             data = span["spans"]
    #             for lines in data:
    #                 # lines['text'] -> string, lines['size'] -> font size, lines['font'] -> font name
    #                 results.append((lines["text"], lines["size"], lines["font"]))

pdf.close()

for text, size, font in results:
    print(f"{round(size)}pt, {font} : {text}")
