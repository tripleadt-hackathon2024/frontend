import os
import shutil

from fastapi import UploadFile, HTTPException


def get_filesize(file: UploadFile):
    # Get the file size (in bytes)
    file.file.seek(0, 2)
    file.file.seek(0)
    file_size = file.file.tell()

    return file_size


def save_file(mimetype: list[str], file: UploadFile) -> str:
    file_size = get_filesize(file)

    if file_size > 10 * 1024 * 1024:
        # more than 2 MB
        raise HTTPException(status_code=400, detail="File too large")

    # check the content type (MIME type)
    content_type = file.content_type
    if content_type not in mimetype:
        raise HTTPException(status_code=400, detail="Invalid file type")

    upload_dir = os.path.join(os.getcwd(), "uploads")
    # Create the upload directory if it doesn't exist
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # get the destination path
    dest = os.path.join(upload_dir, file.filename)

    # copy the file contents
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return dest
