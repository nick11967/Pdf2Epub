import argparse
import subprocess
import os
import shutil


def convert_md_to_epub(md_file_path):
    """
    Converts a Markdown file to a polished EPUB file using Pandoc.
    This version renders math as images for maximum compatibility.
    """
    # 1. Check if Pandoc is installed
    if not shutil.which("pandoc"):
        print("❌ Error: 'pandoc' is not installed or not in PATH.")
        return

    # 2. Check if the input .md file actually exists
    if not os.path.exists(md_file_path):
        print(f"❌ Error: Input file '{md_file_path}' not found.")
        return

    # 3. Set up input and output file paths
    base_path = os.path.splitext(md_file_path)[0]
    output_epub_path = base_path + ".epub"

    print(f"Converting '{md_file_path}' to EPUB (rendering math as images)...")

    # 4. Build the Pandoc command
    command = [
        "pandoc",
        md_file_path,
        "--standalone",
        "--table-of-contents",
        # --- Key Change: Use --webtex instead of --katex ---
        "--webtex",
        "-o",
        output_epub_path,
    ]

    # 5. Execute the Pandoc command
    print("\n🚀 Running Pandoc...")
    print(f"  > {' '.join(command)}")
    try:
        # This process requires an internet connection
        print("  - Note: An internet connection is required for --webtex.")
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        print(f"\n✨ [SUCCESS] EPUB file successfully created at '{output_epub_path}'")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: Pandoc conversion failed.")
        print("--- Pandoc Error Message ---")
        print(e.stderr)
        print("--- End Pandoc Error Message ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts a structured Markdown (.md) file to a polished EPUB (.epub) file.",
    )
    parser.add_argument("md_file", help="The .md file to convert.")

    args = parser.parse_args()
    convert_md_to_epub(args.md_file)
