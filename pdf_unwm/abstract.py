from abc import ABC, abstractmethod

import attrs
from path import Path


@attrs.define(auto_attribs=True)
class PDFOptimizer(ABC):
    path: Path
    denylist_strs: list[str] = attrs.field(factory=list)
    denylist_bytes: list[bytes] = attrs.field(factory=list)

    @abstractmethod
    def clean_kind(self) -> None: ...

    def clean_generic(self) -> None:
        pass

    def save(path: Path) -> None:
        pass
