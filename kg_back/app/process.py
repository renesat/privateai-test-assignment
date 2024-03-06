from pathlib import Path
from typing import Any, List

import attrs
import pdf2bib
import spacy
from pdfminer.high_level import extract_text
from spacy_llm.util import assemble

from .config import PipelineConfig


@attrs.define
class Processor:
    config: PipelineConfig
    _nlp: Any = attrs.field(init=False)
    _llm: Any = attrs.field(init=False)

    def __attrs_post_init__(self):
        self._nlp = spacy.load("en_core_sci_lg")
        nfig = {
            "task": {
                "@llm_tasks": "spacy.REL.v1",
                "labels": self.config.rel_labels,
                "template": self.config.rel_template_path.read_text(),
            },
            "cache": {
                "@llm_misc": "spacy.BatchCache.v1",
                "path": "/tmp/llm_rel_cache",
            },
            "model": {
                "@llm_models": self.config.model,
                "name": self.config.model_name,
            },
        }
        self._llm = self._nlp.add_pipe("llm_rel", config=nfig)

    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        return extract_text(pdf_path)

    def _result_to_json(self, result) -> List[dict]:
        return [
            {
                "source": str(result.ents[rel.dep]).replace("\n", " "),
                "target": str(result.ents[rel.dest]).replace("\n", " "),
                "relation": rel.relation,
            }
            for rel in result._.rel
        ]

    async def get_paper_kg(self, paper_path: Path, title: str) -> List[dict]:
        del title
        paper_text = self._extract_text_from_pdf(paper_path)
        nlp_sent = spacy.blank("en")
        nlp_sent.add_pipe("sentencizer")
        doc = nlp_sent(paper_text)

        txt = []
        results = []
        for sents in doc.sents:
            if len(" ".join(txt)) + len(str(sents)) < self.config.batch_size:
                txt.append(str(sents))
                continue
            try:
                result = self._nlp(" ".join(txt))
                results.extend(self._result_to_json(result))
            except:
                pass
            txt = txt[max(-5, len(txt) - 2) :]
        try:
            result = self._nlp(" ".join(txt))
            results.extend(self._result_to_json(result))
        except:
            pass
        kg = {
            "nodes": [
                {"id": x}
                for x in list(
                    set(
                        [
                            x
                            for link in results
                            for x in [link["source"], link["target"]]
                        ]
                    )
                )
            ],
            "links": results,
        }
        return kg

    async def get_paper_meta(self, paper_path: Path):
        return pdf2bib.pdf2bib(str(paper_path))["metadata"]
