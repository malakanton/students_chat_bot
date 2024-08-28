from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class File:
    subj_id: int
    subj_name: str
    file_type: str
    file_name: str
    s3_path: str = Field(default_factory=str)

    def __post_init__(self):
        self.s3_path = f"{self.subj_name}/{self.file_type}/{self.file_name}"
