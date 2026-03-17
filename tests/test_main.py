from src.main import main


def test_main_uses_requested_category(monkeypatch, tmp_path):
    loaded_paths = []

    def fake_load_items(path):
        loaded_paths.append(path)
        return ["可乐"]

    captured = {}

    def fake_run_pipeline(**kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr("src.main.load_dishes", fake_load_items)
    monkeypatch.setattr("src.main.run_pipeline", fake_run_pipeline)
    monkeypatch.setattr("src.main.OUTPUT_DIR", tmp_path)
    monkeypatch.setattr("src.main.MANIFEST_PATH", tmp_path / "manifest.csv")
    monkeypatch.setattr(
        "src.main.write_manifest", lambda path, rows: path.write_text("", encoding="utf-8")
    )
    monkeypatch.setattr("src.main.ensure_search_providers_reachable", lambda providers: None)

    assert main(["--type", "beverage"]) == 0
    assert loaded_paths == ["data/categories/beverage.txt"]
    assert captured["category_type"] == "beverage"
    assert captured["items"] == ["可乐"]
    assert captured["output_dir"] == tmp_path / "beverage"
    assert captured["search_provider"].query_suffixes[0] == "饮料 酒水 实拍 产品图"


def test_main_rejects_unknown_category(capsys):
    exit_code = main(["--type", "unknown"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "supported types" in captured.err


def test_main_prefers_official_api_providers_when_keys_are_configured(
    monkeypatch, tmp_path
):
    captured = {}

    def fake_run_pipeline(**kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr("src.main.load_dishes", lambda _path: ["可乐"])
    monkeypatch.setattr("src.main.run_pipeline", fake_run_pipeline)
    monkeypatch.setattr("src.main.OUTPUT_DIR", tmp_path)
    monkeypatch.setattr("src.main.MANIFEST_PATH", tmp_path / "manifest.csv")
    monkeypatch.setattr(
        "src.main.write_manifest", lambda path, rows: path.write_text("", encoding="utf-8")
    )
    monkeypatch.setattr("src.main.PIXABAY_API_KEY", "pixabay-key")
    monkeypatch.setattr("src.main.PEXELS_API_KEY", "pexels-key")
    monkeypatch.setattr("src.main.ensure_search_providers_reachable", lambda providers: None)

    assert main(["--type", "beverage"]) == 0
    provider_names = [
        provider.__class__.__name__
        for provider in captured["search_provider"].provider.providers
    ]
    assert provider_names[:2] == [
        "PixabayImageSearchProvider",
        "PexelsImageSearchProvider",
    ]


def test_main_continues_when_any_search_probe_succeeds(monkeypatch, tmp_path):
    captured = {}

    def fake_run_pipeline(**kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr("src.main.load_dishes", lambda _path: ["可乐"])
    monkeypatch.setattr("src.main.run_pipeline", fake_run_pipeline)
    monkeypatch.setattr("src.main.OUTPUT_DIR", tmp_path)
    monkeypatch.setattr("src.main.MANIFEST_PATH", tmp_path / "manifest.csv")
    monkeypatch.setattr(
        "src.main.write_manifest", lambda path, rows: path.write_text("", encoding="utf-8")
    )
    monkeypatch.setattr(
        "src.main.ensure_search_providers_reachable",
        lambda providers: None,
    )

    assert main(["--type", "beverage"]) == 0
    assert captured["items"] == ["可乐"]


def test_main_fails_fast_when_all_search_probes_are_unreachable(
    monkeypatch, tmp_path, capsys
):
    monkeypatch.setattr("src.main.load_dishes", lambda _path: ["可乐"])
    monkeypatch.setattr("src.main.OUTPUT_DIR", tmp_path)
    monkeypatch.setattr("src.main.MANIFEST_PATH", tmp_path / "manifest.csv")
    monkeypatch.setattr(
        "src.main.ensure_search_providers_reachable",
        lambda providers: (_ for _ in ()).throw(
            RuntimeError(
                "search providers are unreachable; network access may be blocked in the current environment\n"
                "duckduckgo: operation not permitted\n"
                "wikimedia: operation not permitted"
            )
        ),
    )

    exit_code = main(["--type", "beverage"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert (
        "search providers are unreachable; network access may be blocked in the current environment"
        in captured.err
    )
    assert "duckduckgo: operation not permitted" in captured.err
    assert "wikimedia: operation not permitted" in captured.err
