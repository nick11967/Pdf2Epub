import argparse
import subprocess
import os
import shutil


def convert_tex_to_epub(tex_file_path):
    """
    Converts a TeX source file to a polished EPUB file,
    expanding custom LaTeX macros and rendering math correctly.
    """
    # 1. Check if Pandoc is installed
    if not shutil.which("pandoc"):
        print("❌ Error: 'pandoc' is not installed or not in PATH.")
        return

    # 2. Check if the input .tex file actually exists
    if not os.path.exists(tex_file_path):
        print(f"❌ Error: Input file '{tex_file_path}' not found.")
        return

    # 3. Set up file paths
    base_path = os.path.splitext(tex_file_path)[0]
    output_epub_path = base_path + ".epub"
    bib_file_path = base_path + ".bib"  # Look for .bib, not .bbl

    print(f"Directly converting '{tex_file_path}' to EPUB...")

    # 4. Build the Pandoc command with macro expansion
    command = [
        "pandoc",
        # --- Key Change: Use '-f latex+latex_macros' ---
        # This tells Pandoc to enable the LaTeX macro expansion extension.
        "-f",
        "latex+latex_macros",
        tex_file_path,
        "--standalone",
        "--table-of-contents",
        "--katex",  # or "--webtex" for image-based math
        "-o",
        output_epub_path,
    ]

    # Auto-detect .bib file and add citation processing
    if os.path.exists(bib_file_path):
        print(f"  - Found '{bib_file_path}', enabling citation processing.")
        command.extend(["--bibliography", bib_file_path, "--citeproc"])
    else:
        # If no .bib, we assume .bbl is included via \input in the .tex
        print(
            "  - No .bib file found. Assuming bibliography is included in the TeX file."
        )

    # 5. Execute the Pandoc command
    print("\n🚀 Running Pandoc with macro expansion...")
    print(f"  > {' '.join(command)}")
    try:
        result = subprocess.run(
            command, check=True, capture_output=True, text=True, encoding="utf-8"
        )
        print(f"\n✨ [SUCCESS] EPUB file successfully created at '{output_epub_path}'")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error: Pandoc conversion failed.")
        print("--- Pandoc Error Message ---")
        print(e.stderr)
        print("--- End Pandoc Error Message ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts a TeX file to a polished EPUB with math macro expansion.",
    )
    parser.add_argument("tex_file", help="The .tex file to convert.")
    args = parser.parse_args()
    convert_tex_to_epub(args.tex_file)
