from pathlib import Path

from src.manifest import write_manifest
from src.models import ManifestRow


def test_write_manifest_creates_csv_with_header(tmp_path: Path):
    target = tmp_path / "manifest.csv"
    rows = [
        ManifestRow(
            image_id="img_000001",
            category_type="home_cooking",
            item_name="鱼香肉丝",
            file_path="output/images/home_cooking/鱼香肉丝/001.jpg",
            width=800,
            height=800,
            source_url="https://example.com/1.jpg",
        )
    ]

    write_manifest(target, rows)

    content = target.read_text(encoding="utf-8")
    assert (
        "image_id,category_type,item_name,file_path,width,height,source_url,status" in content
    )
    assert "img_000001,home_cooking,鱼香肉丝" in content
