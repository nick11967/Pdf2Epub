import fitz
import os
import re

pdf_file_path = "HIQL.pdf"
image_output_folder = "extracted_images"
HEADER_MARGIN_Y = 50  # Area considered as header (y < 50)

# Create dir to save images if it doesn't exist
if not os.path.exists(image_output_folder):
    os.makedirs(image_output_folder)

caption_regex = re.compile(r"^\s*(figure|fig)\s+\d+", re.IGNORECASE)

try:
    doc = fitz.open(pdf_file_path)
    print(f"Start extracting figures from'{pdf_file_path}'...")

    total_captures = 0
    failed_captures = 0

    # Iterate through each page in the PDF
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)

        # Separate and collect text, drawing, and image elements from the page
        text_blocks = [
            b for b in page.get_text("dict").get("blocks", []) if b["type"] == 0
        ]
        drawing_blocks = [d["rect"] for d in page.get_drawings()]
        image_blocks = []
        for img in page.get_images(full=True):
            try:
                image_blocks.append(page.get_image_bbox(img))
            except ValueError:
                continue

        # Process each text block to find captions
        for i, block in enumerate(text_blocks):
            block_text = "".join(
                s["text"] for l in block.get("lines", []) for s in l.get("spans", [])
            )

            if caption_regex.match(block_text.strip()):
                caption_bbox = fitz.Rect(block["bbox"])
                print(
                    f"\nCaption found on page {page_num+1}: '{block_text.strip()[:60]}...'"
                )

                # 1. Determine the upper boundary (ceiling) for searching related blocks
                upper_boundary_y = HEADER_MARGIN_Y
                for j, other_block in enumerate(text_blocks):
                    if i == j:
                        continue
                    other_bbox = fitz.Rect(other_block["bbox"])
                    if other_bbox.y1 <= caption_bbox.y0:
                        other_text = "".join(
                            s["text"]
                            for l in other_block.get("lines", [])
                            for s in l.get("spans", [])
                        )
                        if caption_regex.match(other_text.strip()):
                            upper_boundary_y = max(upper_boundary_y, other_bbox.y1)

                print(
                    f"  ->  Upper boundary (ceiling) y-coordinate for capture: {upper_boundary_y:.2f}"
                )

                target_block_bbox = None

                # 2. (1st priority) Find the largest drawing block within the defined area
                max_area = 0
                for drawing_bbox in drawing_blocks:
                    if (
                        drawing_bbox.y0 >= upper_boundary_y
                        and drawing_bbox.y1 <= caption_bbox.y0
                        and (
                            max(caption_bbox.x0, drawing_bbox.x0)
                            < min(caption_bbox.x1, drawing_bbox.x1)
                        )
                    ):
                        area = drawing_bbox.width * drawing_bbox.height
                        if area > max_area:
                            max_area = area
                            target_block_bbox = drawing_bbox

                if target_block_bbox:
                    print(
                        f"  -> 1st priority: Found the largest drawing block. (area: {max_area:.0f})"
                    )

                # 3. (2nd priority) If no drawing block found, search for the largest image block
                if not target_block_bbox:
                    max_area = 0
                    for image_bbox in image_blocks:
                        if (
                            image_bbox.y0 >= upper_boundary_y
                            and image_bbox.y1 <= caption_bbox.y0
                            and (
                                max(caption_bbox.x0, image_bbox.x0)
                                < min(caption_bbox.x1, image_bbox.x1)
                            )
                        ):
                            area = image_bbox.width * image_bbox.height
                            if area > max_area:
                                max_area = area
                                target_block_bbox = image_bbox

                    if target_block_bbox:
                        print(
                            f"  -> 2nd priority: Found the largest image block. (area: {max_area:.0f})"
                        )

                # 4. Final capture
                if target_block_bbox:
                    final_capture_bbox = target_block_bbox.include_rect(caption_bbox)

                    final_capture_bbox += (-10, -10, 10, 10)  # Margin
                    pix = page.get_pixmap(clip=final_capture_bbox.irect, dpi=200)

                    safe_filename = re.sub(r'[\\/*?:"<>|]', "", block_text.strip())[:40]
                    image_filename = f"{safe_filename.replace(' ', '_')}.png"

                    pix.save(os.path.join(image_output_folder, image_filename))
                    total_captures += 1
                else:
                    failed_captures += 1
                    print(
                        "  -> [Warning] No matching drawing or image block found within the area."
                    )

    print(
        f"\n{'='*30}\n[Final Result] Successfully saved a total of {total_captures} captures."
    )
    print(f"[Final Result] Failed to capture a total of {failed_captures} instances.")
    doc.close()

except Exception as e:
    print(f"[Error]: {e}")
