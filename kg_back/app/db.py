import uuid
from pathlib import Path

import aiofiles
import attrs
from sqlitedict import SqliteDict

from .config import StoreConfig
from .process import Processor


@attrs.define
class StoreProcessor:
    config: StoreConfig
    _con: SqliteDict = attrs.field(init=False)

    def __attrs_post_init__(self):
        self._con = SqliteDict(self.config.storage_path / self.config.db_name)

    def _paper_path(self, paper_id: str) -> Path:
        return self.config.storage_path / f"{paper_id}.pdf"

    async def store_pdf(self, pdf_io) -> str:
        store_id = str(uuid.uuid4())
        async with aiofiles.open(self._paper_path(store_id), "wb") as f:
            await f.write(pdf_io.read())
        return store_id

    async def upload_paper(self, pdf_io, processor: Processor) -> str:
        paper_id = await self.store_pdf(pdf_io)
        paper_path = self._paper_path(paper_id)
        meta = await processor.get_paper_meta(paper_path)
        title = meta["title"]
        kg = await processor.get_paper_kg(paper_path, title)
        self._con[paper_id] = {
            "meta": meta,
            "kg": kg,
            "title": title,
        }
        self._con.commit()
        return paper_id

    async def get_paper_info(self, paper_id: str) -> dict:
        return self._con[paper_id]

    async def list_papers(self) -> list[dict]:
        return [
            {
                "id": k,
                "title": v["title"],
            }
            for k, v in self._con.items()
        ]
