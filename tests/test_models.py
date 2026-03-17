from src.models import CandidateImage, ManifestRow


def test_manifest_row_defaults_to_ok_status():
    row = ManifestRow(
        image_id="img_000001",
        category_type="home_cooking",
        item_name="鱼香肉丝",
        file_path="output/images/home_cooking/鱼香肉丝/001.jpg",
        width=800,
        height=800,
        source_url="https://example.com/1.jpg",
    )
    assert row.status == "ok"


def test_candidate_image_tracks_source_url():
    item = CandidateImage(item_name="鱼香肉丝", source_url="https://example.com/1.jpg")
    assert item.source_url.endswith(".jpg")
