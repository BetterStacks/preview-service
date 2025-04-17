import os
import hashlib
import uuid

import uvicorn
import httpx

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette import status
from starlette.responses import (
    FileResponse,
    JSONResponse,
    PlainTextResponse,
)
from starlette.datastructures import UploadFile

from preview_generator.manager import PreviewManager


UPLOAD_DIR = "/tmp/files/"
CACHE_PATH = "/tmp/cache/"


app = Starlette()
app.mount("/cache", StaticFiles(directory=CACHE_PATH), name="cache")


manager = PreviewManager(CACHE_PATH, create_folder=True)


def error_response(error_message, status=None):
    return JSONResponse({"error": error_message}, status_code=status)


async def _store_uploaded_file(file) -> str:
    contents = await file.read()
    h = hashlib.md5(contents).hexdigest()
    upload_dest = os.path.join(UPLOAD_DIR, ".".join([h, file.filename]))

    with open(upload_dest, "wb+") as f:
        f.write(contents)

    return upload_dest


async def _download_file_from_url(url, filename=None) -> str:
    if not filename:
        filename = str(uuid.uuid4())
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        
        contents = response.content
        h = hashlib.md5(contents).hexdigest()
        
        if not filename:
            ext = url.split(".")[-1] if "." in url else ""
            filename = f"{h}.{ext}"
        else:
            filename = h + "." + filename
            
        upload_dest = os.path.join(UPLOAD_DIR, filename)
        
        with open(upload_dest, "wb+") as f:
            f.write(contents)
            
        return upload_dest


@app.route("/")
async def health_endpoint(request):
    return PlainTextResponse("OK")


@app.route("/preview/{width:int}x{height:int}", methods=["POST"])
async def preview_endpoint(request):
    width = request.path_params["width"]
    height = request.path_params["height"]

    form = await request.form()
    file = form.get("file", None)
    file_url = form.get("file_url", None)
    
    if file is None and file_url is None:
        return error_response('"file" or "file_url" is required', status.HTTP_400_BAD_REQUEST)
    
    try:
        # if file is not None:
        #     if not isinstance(file, UploadFile):
        #         return error_response('"file" must be a file', status.HTTP_400_BAD_REQUEST)
        #     file_path = await _store_uploaded_file(file)
        # else:
        #     file_path = await _download_file_from_url(file_url)
            
        image = manager.get_jpeg_preview(file_url, width=width, height=height)
    except httpx.HTTPError as e:
        return error_response(f"Error downloading file: {str(e)}", status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

    return FileResponse(image)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
