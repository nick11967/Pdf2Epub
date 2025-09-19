import fitz  # PyMuPDF library

# Please specify the path to the PDF file you want to analyze.
pdf_path = "HIQL.pdf"

try:
    doc = fitz.open(pdf_path)
    print(f"Starting feature analysis by paragraph for the '{pdf_path}' file...")

    # Iterate through all pages of the document.
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        print(f"\n--- [Page {page_num + 1}] ---")

        # Get detailed text information of the page as a dictionary.
        blocks = page.get_text("dict").get("blocks", [])

        # Filter only text blocks (paragraphs).
        text_blocks = [b for b in blocks if b["type"] == 0]

        if not text_blocks:
            print("  -> This page has no text paragraphs.")
            continue

        # Check the most used font size by iterating through each text paragraph.
        font_count = {}
        for i, block in enumerate(text_blocks):
            if not block["lines"] or not block["lines"][0]["spans"]:
                continue

            first_span = block["lines"][0]["spans"][0]

            font_size = round(first_span["spans"][0])

        # Iterate through each text paragraph.
        for i, block in enumerate(text_blocks):
            # Extract key features from the first line, first span of the paragraph.
            if not block["lines"] or not block["lines"][0]["spans"]:
                continue

            first_span = block["lines"][0]["spans"][0]

            # Feature extraction
            font_size = round(first_span["size"], 1)
            font_name = first_span["font"]
            # Font flag '16' means 'bold'.
            is_bold = "Bold" in font_name or (first_span["flags"] & 16)
            bbox = [round(c) for c in block["bbox"]]  # Positional coordinates (rounded)

            # Combine the entire paragraph text and extract the first 3 words.
            full_text = " ".join(
                span["text"] for line in block["lines"] for span in line["spans"]
            )
            words = full_text.replace("\n", " ").split()
            first_three_words = " ".join(words[:3])

            # Print the features in a readable format.
            style = "Bold" if is_bold else "Regular"
            print(f'  Paragraph #{i+1}: "{first_three_words}..."')
            print(
                f"    - Features: Size({font_size}pt), Style({style}), Font({font_name}), Position({bbox})"
            )

    doc.close()

except FileNotFoundError:
    print(f"Error: '{pdf_path}' file not found. Please check the path.")
except Exception as e:
    print(f"An error occurred: {e}")