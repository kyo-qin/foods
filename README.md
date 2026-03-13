# Foods Image Crawler

Local CLI tool for collecting Chinese dish images for restaurant ordering systems.

## Requirements

- Python 3.9+
- `Pillow`

## Install

```bash
python3 -m pip install -r requirements-dev.txt
```

## Run

```bash
python -m src.main
```

## Output

```text
output/
├── images/
│   └── 鱼香肉丝/
│       ├── 001.jpg
│       ├── 002.jpg
│       └── 003.jpg
└── manifest.csv
```

`manifest.csv` includes:

- `image_id`
- `dish_name`
- `file_path`
- `width`
- `height`
- `source_url`
- `status`

## Notes

- The default provider uses public web image search results, so quality can vary by dish.
- Some dishes may produce fewer than 3 valid images if search results are weak or downloads fail.
- Review image copyright and source compliance before using the assets in production.
