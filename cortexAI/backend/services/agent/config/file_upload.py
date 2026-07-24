import os
import shutil
import time
from pathlib import Path
from fastapi import File, UploadFile, HTTPException, status

# 1. Setup temp upload directory (equivalent to path.resolve("./temp") & fs.mkdirSync)
UPLOAD_DIR = Path("./temp").resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Constants (equivalent to limits: { fileSize: 20 * 1024 * 1024 })
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


def file_filter(content_type: str) -> bool:
    """
    Equivalent to Multer's fileFilter function:
    Checks if the file is a PDF or an Image.
    """
    if not content_type:
        return False

    is_pdf = content_type == "application/pdf"
    is_image = content_type.startswith("image/")

    return is_pdf or is_image


async def save_uploaded_file(file: UploadFile = File(...)) -> dict:
    """
    Handles file validation, timestamp filename generation, 
    and saves the file to disk.
    """
    # 1. Check file type (fileFilter logic)
    if not file_filter(file.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and Images are allowed."
        )

    # 2. Read contents to enforce file size limit (limits.fileSize logic)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 20MB limit."
        )

    # 3. Generate unique filename (equivalent to Date.now() - ${file.originalname})
    timestamp_ms = int(time.time() * 1000)
    saved_filename = f"{timestamp_ms}-{file.filename}"
    file_path = UPLOAD_DIR / saved_filename

    # 4. Save file to disk
    try:
        with open(file_path, "wb") as f:
            f.write(contents)

        return {
            "filename": saved_filename,
            "originalname": file.filename,
            "path": str(file_path),
            "size": len(contents),
            "mimetype": file.content_type
        }
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(err)}"
        )
    finally:
        # Reset file pointer if needed
        await file.seek(0)