from pathlib import Path

import attrs
import cattrs
import toml


@attrs.define
class StoreConfig:
    storage_path: Path = attrs.field(converter=Path)
    db_name: str


@attrs.define
class PipelineConfig:
    rel_template_path: Path = attrs.field(converter=Path)
    rel_labels: list[str]
    model: str
    model_name: str
    batch_size: int = 20


@attrs.define
class Config:
    store: StoreConfig
    pipeline: PipelineConfig

    @classmethod
    def load(cls, path: str):
        with open(path, "r") as f:
            return cattrs.structure(
                toml.load(f),
                cls,
            )
