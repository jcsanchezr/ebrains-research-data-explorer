from ebrains_explorer.ingestion.ebrains import (
    create_client,
    fetch_dataset_versions,
)
from ebrains_explorer.ingestion.resolver import resolve_relation


RELATIONS = (
    "license",
    "repository",
    "keywords",
    "data_types",
    "study_targets",
    "techniques",
)


def main() -> None:
    client = create_client()
    dataset = fetch_dataset_versions(client, limit=1)[0]

    print(f"Dataset: {dataset.short_name}")
    print()

    for relation_name in RELATIONS:
        entities = resolve_relation(
            getattr(dataset, relation_name, None),
            client,
        )

        print(relation_name)

        for entity in entities:
            print(
                f"  {entity.entity_type:24} "
                f"{entity.label!r}"
            )

        print()


if __name__ == "__main__":
    main()
