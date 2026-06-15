from fastapi import APIRouter
from fastapi import UploadFile

import os

from services.ocr_service import (
    extract_text
)

from services.nlp_service import (
    analyze_text
)

router = APIRouter()


@router.post("/analyze-file")
async def analyze_file(
    file: UploadFile
):

    upload_dir = "uploads"

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    file_path = os.path.join(
        upload_dir,
        file.filename
    )

    contents = await file.read()

    with open(
        file_path,
        "wb"
    ) as f:

        f.write(contents)

    text = extract_text(
        file_path
    )

    result = analyze_text(
        text
    )

    result["filename"] = (
        file.filename
    )

    return result