"""Test snapshots and database."""
from typing import List

import pytest
from wbm_snapshot.db.client import DbClient, SnapshotCollectionClient
from wbm_snapshot.snapshot import Snapshot, SnapshotData
# pylint: disable: redefined-outer-name


@pytest.fixture(autouse=True, name="client")
def get_client():
    """Create and finally drop collection."""
    database = DbClient(connection='mongodb://localhost',
                        database='pytest_test')
    collection = SnapshotCollectionClient(database, "test")
    yield collection
    database.db.drop_collection('test')


def generate_snapshots(num: int):
    """Generate `num` snapshots."""
    snapshots_fields = SnapshotData.fields()

    snapshots_list = [
        Snapshot.from_dict(
            {
                field: f"{field} {index}" for field in snapshots_fields
            }
        )
        for index in range(num)
    ]

    return snapshots_list


@pytest.fixture(name="snapshots")
def get_snapshots():
    """Fixture to generate snapshots."""
    return generate_snapshots(3)


def test_insert_snapshots(client: SnapshotCollectionClient,
                          snapshots: List[Snapshot]):
    """Test insert snapshots"""

    for item in snapshots:
        client.insert(item)

    for item in snapshots:
        result = client.find_field('title', item.data.title)

        assert result.count() == 1, \
            f"Results count {result.count()} != 1"


def test_insert_duplicated_snapshots(client: SnapshotCollectionClient,
                                     snapshots: List[Snapshot]):
    """Test if insert duplicated snapshots."""
    snapshots += [snapshots[0]]

    for item in snapshots:
        client.insert(item)

    for item in snapshots:
        result = client.find_field('title', item.data.title)

        assert result.count() == 1, \
            f"Results count {result.count()} != 1"
