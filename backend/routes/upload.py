from fastapi import APIRouter, UploadFile

router = APIRouter()

@router.post("/upload")
async def upload_contract(
    file: UploadFile
):

    return {
        "filename": file.filename
    }