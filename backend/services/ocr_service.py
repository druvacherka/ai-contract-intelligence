from docx import Document
import pdfplumber


def extract_docx(file_path):

    doc = Document(file_path)

    text = []

    for para in doc.paragraphs:

        text.append(
            para.text
        )

    return "\n".join(text)


def extract_pdf(file_path):

    text = []

    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:

                text.append(
                    page_text
                )

    return "\n".join(text)


def extract_text(file_path):

    if file_path.endswith(".docx"):

        return extract_docx(
            file_path
        )

    if file_path.endswith(".pdf"):

        return extract_pdf(
            file_path
        )

    return ""