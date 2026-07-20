import pymupdf  # PyMuPDF


def read_pdf_text(pdf_path: str) -> str:
    text_parts = []

    with pymupdf.open(pdf_path) as doc:
        for page_number, page in enumerate(doc, start=1):
            page_text = page.get_text()
            text_parts.append(f"\n--- Page {page_number} ---\n")
            text_parts.append(page_text)

    return "\n".join(text_parts)


if __name__ == "__main__":
    pdf_text = read_pdf_text("report.pdf")
    print(pdf_text[:3000])  # 先只打印前 3000 个字符，避免刷屏