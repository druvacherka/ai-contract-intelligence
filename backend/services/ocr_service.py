from docx import Document


def extract_text(file_path):

    if file_path.endswith(".docx"):

        doc = Document(file_path)

        text = []

        for para in doc.paragraphs:

            text.append(
                para.text
            )

        return "\n".join(text)

    return ""