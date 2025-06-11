from pdf2image import convert_from_path

pages = convert_from_path("your_file.pdf", dpi=300)
for i, page in enumerate(pages):
    page.save(f"page_{i + 1}.png", "PNG")