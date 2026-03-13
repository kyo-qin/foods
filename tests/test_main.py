from src.main import main


def test_main_returns_zero_for_success(monkeypatch, tmp_path):
    monkeypatch.setattr("src.main.load_dishes", lambda _path: ["鱼香肉丝"])
    monkeypatch.setattr("src.main.run_pipeline", lambda **_kwargs: [])
    monkeypatch.setattr("src.main.OUTPUT_DIR", tmp_path)
    monkeypatch.setattr("src.main.MANIFEST_PATH", tmp_path / "manifest.csv")
    monkeypatch.setattr("src.main.write_manifest", lambda path, rows: path.write_text("", encoding="utf-8"))
    assert main() == 0
