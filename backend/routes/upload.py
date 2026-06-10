from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import HTTPException

import os

router = APIRouter()

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt"
}


@router.post("/upload")
async def upload_contract(
    file: UploadFile
):

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in (
        ALLOWED_EXTENSIONS
    ):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )

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

    if len(contents) == 0:

        raise HTTPException(
            status_code=400,
            detail="Empty file"
        )

    with open(
        file_path,
        "wb"
    ) as f:

        f.write(contents)

    return {
        "filename": file.filename,
        "saved_to": file_path
    }