import argparse
import fitz
import os


def main(file_path):
    ## ---------------- Config ---------------- ##
    source_pdf_path = file_path
    output_pdf_path = file_path.replace(".pdf", "_visualized.pdf")

    # Color of block for each element (R, G, B, 0~1)
    # fitz.utils.getColor("red").
    COLOR_MAP = {
        "text": (1, 0, 0),  # Red
        "image": (0, 0, 1),  # Blue
        "drawing": (0, 1, 0),  # Green
    }
    BORDER_WIDTH = 0.5
    ## ---------------------------------------- ##

    try:
        # Open the source PDF document.
        doc = fitz.open(source_pdf_path)
        print(
            f"'{source_pdf_path}' opened successfully. Starting block visualization..."
        )

        # Iterate through all pages.
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # 1. Collect all visual elements on the page (same as existing logic).
            all_elements = []
            text_blocks = [
                b for b in page.get_text("dict").get("blocks", []) if b["type"] == 0
            ]
            for block in text_blocks:
                all_elements.append({"bbox": fitz.Rect(block["bbox"]), "type": "text"})
            for img in page.get_images(full=True):
                try:
                    all_elements.append(
                        {"bbox": page.get_image_bbox(img), "type": "image"}
                    )
                except ValueError:
                    continue
            for drawing in page.get_drawings():
                all_elements.append({"bbox": drawing["rect"], "type": "drawing"})

            print(
                f"  - Page {page_num + 1}: {len(all_elements)} elements found. Drawing borders..."
            )

            # 2. Draw rectangles around the bounding boxes (bbox) of all collected elements.
            for element in all_elements:
                bbox = element["bbox"]
                element_type = element["type"]
                color = COLOR_MAP.get(
                    element_type, (0, 0, 0)
                )  # If type is not in dict, use black

                # page.draw_rect() draws a rectangle on the page.
                page.draw_rect(bbox, color=color, width=BORDER_WIDTH)

        # 3. Save the changes to a new PDF file.
        # garbage=4, deflate=True options optimize and compress the file to reduce size.
        doc.save(output_pdf_path, garbage=4, deflate=True)
        print(
            f"\n[Success] '{output_pdf_path}' created successfully with borders drawn around all blocks."
        )
        doc.close()

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Block Visualizer")
    parser.add_argument(
        "pdf_file",
        type=str,
        help="Name of the PDF file",
    )
    args = parser.parse_args()
    file_path = os.path.join("data", args.pdf_file + ".pdf")
    main(file_path)
