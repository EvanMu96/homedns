from collections import namedtuple
from dataclasses import dataclass
from typing import List, Optional, Tuple

EnableMode = namedtuple("EnableMode", ["DoH", "DoT", "Plain"])

# a example of root hints
@dataclass
class Config:
    roots: List[Tuple[str, Optional[int]]]
    encrypted_roots: Optional[List[Tuple[str, str, Optional[int]]]]
    db_path: str
    client_denylist: List[Tuple[str, str]]
