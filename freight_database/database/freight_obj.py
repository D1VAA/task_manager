from dataclasses import dataclass
from typing import Optional


@dataclass
class FreightOBJ:
    origem: str
    destino: str
    client: str
    link: Optional[str] = None
