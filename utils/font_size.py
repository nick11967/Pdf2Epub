import fitz

pdf_path = "HIQL.pdf"

# List of tuples to store text and font information: (text, size, font)
results = []

pdf = fitz.open(pdf_path)

# Process the first 2 pages for a quick analysis
for page_num in range(min(2, len(pdf))):
    page = pdf.load_page(page_num)
    print(f"--- [Page {page_num + 1}] ---")

    blocks = page.get_text("dict").get("blocks", [])
    text_blocks = [b for b in blocks if b["type"] == 0]

    if not text_blocks:
        print("  -> No text blocks found on this page.")
        continue

    # Extract text and font info from each span in each block
    for block in text_blocks:
        for line in block["lines"]:
            for span in line["spans"]:
                results.append((span["text"], span["size"], span["font"]))

pdf.close()

# Print the collected results
for text, size, font in results:
    print(f"{round(size)}pt, {font}: {text}")