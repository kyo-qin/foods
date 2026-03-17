from dataclasses import dataclass


@dataclass
class CandidateImage:
    item_name: str
    source_url: str


@dataclass
class ManifestRow:
    image_id: str
    category_type: str
    item_name: str
    file_path: str
    width: int
    height: int
    source_url: str
    status: str = "ok"
