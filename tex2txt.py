import argparse
import subprocess
import os
import shutil
import json


def get_text_from_inlines(inlines):
    """
    Pandoc's JSON AST inline elements to a Markdown string.
    This version handles rich formatting, math, and internal links.
    """
    # This helper function remains the same.
    markdown_text = ""
    for inline in inlines:
        if inline["t"] == "Str":
            markdown_text += inline["c"]
        elif inline["t"] in ["Space", "SoftBreak", "LineBreak"]:
            markdown_text += " "
        elif inline["t"] == "Math":
            math_type = inline["c"][0]["t"]
            math_content = inline["c"][1]
            if math_type == "InlineMath":
                markdown_text += f"${math_content}$"
            elif math_type == "DisplayMath":
                markdown_text += f"$$ {math_content} $$"
        elif inline["t"] in ["Strong", "Emph"]:
            markdown_text += (
                f"**{get_text_from_inlines(inline['c'])}**"
                if inline["t"] == "Strong"
                else f"*{get_text_from_inlines(inline['c'])}*"
            )
        elif inline["t"] == "Link":
            link_text_inlines = inline["c"][1]
            markdown_text += get_text_from_inlines(link_text_inlines)
    return markdown_text


def collect_text_content_recursively(blocks, stream):
    """
    Recursively traverses Pandoc AST blocks to build a sequential stream
    of text-only content (Headers and Paragraphs).
    """
    for block in blocks:
        block_type = block["t"]

        if block_type == "Header":
            stream.append(
                {
                    "type": "header",
                    "level": block["c"][0],
                    "content": get_text_from_inlines(block["c"][2]),
                }
            )
        elif block_type == "Para":
            stream.append(
                {"type": "paragraph", "content": get_text_from_inlines(block["c"])}
            )
        elif block_type == "Div":
            # Recursively process the children of the Div to find text within.
            child_blocks = block["c"][1]
            collect_text_content_recursively(child_blocks, stream)
        # --- Key Change: Figure, Table, and other non-text blocks are now ignored ---


def extract_text_only(tex_file_path):
    """
    Main function to create a text-only Markdown file from a TeX file.
    """
    if not shutil.which("pandoc"):
        print("❌ Error: 'pandoc' is not installed or not in PATH.")
        return
    if not os.path.exists(tex_file_path):
        print(f"❌ Error: Input file '{tex_file_path}' not found.")
        return

    base_path = os.path.splitext(tex_file_path)[0]
    output_md_path = base_path + "_text_only.md"

    print(f"Extracting text content from '{tex_file_path}'...")
    command = ["pandoc", tex_file_path, "-t", "json"]

    try:
        result = subprocess.run(
            command, check=True, capture_output=True, text=True, encoding="utf-8"
        )
        doc_ast = json.loads(result.stdout)

        content_stream = []

        # --- Pass 1: Recursively collect text content ---
        print("  - Collecting all text blocks...")
        collect_text_content_recursively(doc_ast["blocks"], content_stream)
        print(f"  - Collected {len(content_stream)} text blocks.")

        # --- Pass 2: Write the collected text to the Markdown file ---
        print("  - Writing content to Markdown file...")
        with open(output_md_path, "w", encoding="utf-8") as f:
            meta = doc_ast.get("meta", {})
            if "title" in meta:
                f.write(f"# {get_text_from_inlines(meta['title']['c'])}\n\n")
            if "author" in meta:
                f.write(
                    f"**Authors:** {'; '.join([get_text_from_inlines(a['c']) for a in meta['author']['c']])}\n\n"
                )
            if "abstract" in meta:
                f.write(f"## Abstract\n\n")
                for para_block in meta["abstract"]["c"]:
                    f.write(f"{get_text_from_inlines(para_block['c'])}\n\n")
            f.write("---\n\n")

            for item in content_stream:
                item_type = item.get("type")

                if item_type == "header":
                    f.write(f"{'#' * item['level']} {item['content']}\n\n")
                elif item_type == "paragraph":
                    f.write(f"{item['content']}\n\n")

        print(f"\n✨ [SUCCESS] Text-only Markdown file saved to '{output_md_path}'")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: Pandoc failed during parsing.")
        print(
            "--- Pandoc Error Message ---",
            e.stderr,
            "--- End Pandoc Error Message ---",
            sep="\n",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a text-only Markdown file from a TeX file."
    )
    parser.add_argument("tex_file", help="The .tex file to process.")
    args = parser.parse_args()
    extract_text_only(args.tex_file)
