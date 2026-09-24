import json
from pathlib import Path

from ebrains_explorer.ingestion.ebrains import (
    create_client,
    fetch_dataset_versions,
)

OUTPUT_PATH = Path("data/raw/dataset_versions_sample.json")


def main() -> None:
    client = create_client()
    datasets = fetch_dataset_versions(client, limit=5)

    print(f"Retrieved {len(datasets)} dataset versions from EBRAINS")

    for index, dataset in enumerate(datasets, start=1):
        print()
        print(f"{index}. {dataset.full_name or dataset.short_name}")
        print(f"   UUID: {dataset.uuid}")
        print(f"   Released: {dataset.release_date}")
        print(f"   Version: {dataset.version_identifier}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    payload = [dataset.to_jsonld() for dataset in datasets]

    OUTPUT_PATH.write_text(
        json.dumps(payload, indent=2, default=str),
        encoding="utf-8",
    )

    print()
    print(f"Raw metadata written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
