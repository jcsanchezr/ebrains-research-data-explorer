from fairgraph import KGClient
from fairgraph.openminds.core import DatasetVersion

PRODUCTION_HOST = "core.kg.ebrains.eu"


def create_client() -> KGClient:
    """Create an authenticated client for the production EBRAINS KG."""
    return KGClient(host=PRODUCTION_HOST)


def fetch_dataset_versions(
    client: KGClient,
    limit: int = 5,
) -> list[DatasetVersion]:
    """Retrieve released dataset versions from EBRAINS."""
    return DatasetVersion.list(
        client,
        size=limit,
        release_status="released",
    )
