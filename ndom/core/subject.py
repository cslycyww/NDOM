from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid


@dataclass
class NDOMSubject:
    """受试者信息，兼容 PyNWB Subject 语义并扩展。"""

    subject_id: str
    age: Optional[str] = None
    sex: Optional[str] = None          # "F", "M", "U", "O"
    species: Optional[str] = None    # e.g., "Homo sapiens"
    genotype: Optional[str] = None
    strain: Optional[str] = None
    weight: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    description: Optional[str] = None

    # NDOM 新增
    pseudonym_id: Optional[str] = None
    vulnerability_tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.object_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "age": self.age,
            "sex": self.sex,
            "species": self.species,
            "genotype": self.genotype,
            "strain": self.strain,
            "weight": self.weight,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "description": self.description,
            "pseudonym_id": self.pseudonym_id,
            "vulnerability_tags": self.vulnerability_tags,
            "object_id": self.object_id,
        }
