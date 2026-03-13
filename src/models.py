from dataclasses import dataclass


@dataclass
class CandidateImage:
    dish_name: str
    source_url: str


@dataclass
class ManifestRow:
    image_id: str
    dish_name: str
    file_path: str
    width: int
    height: int
    source_url: str
    status: str = "ok"
