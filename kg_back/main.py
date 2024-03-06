from typing import Union

try:
    from typing import Annotated
except:
    from typing_extensions import Annotated

import os
import tempfile

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import Config
from app.db import StoreProcessor
from app.process import Processor

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = Config.load(os.environ.get("APP_CONFIG_PATH", "app-config.toml"))
store = StoreProcessor(config.store)
processor = Processor(config.pipeline)


@app.get("/api/v1/paper/extract_meta")
async def get_metadata(
    file: Annotated[UploadFile, File()],
):
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(file.file.read())
        return await processor.get_paper_meta(f.name)


@app.get("/api/v1/paper", response_class=JSONResponse)
async def list_of_papers():
    return await store.list_papers()


@app.post("/api/v1/paper", response_class=JSONResponse)
async def upload_paper(
    file: Annotated[UploadFile, File()],
):
    paper_id = await store.upload_paper(file.file, processor)
    return {
        "paper_id": paper_id,
    }


@app.get("/api/v1/paper/{paper_id}", response_class=JSONResponse)
async def get_paper_info(paper_id: str):
    info = await store.get_paper_info(paper_id)
    info["id"] = paper_id
    return info
