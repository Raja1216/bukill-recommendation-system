from collections import defaultdict

import pandas as pd

from app.config import (
    MAX_PER_CATEGORY,
    MAX_PER_CREATOR,
)
from app.repositories.buckil_repository import BuckilRepository


def safe_int(value):
    """
    Convert DB/Pandas numeric value to int safely.

    Handles:
    None
    NaN
    pd.NA
    """

    if value is None:
        return None

    if pd.isna(value):
        return None

    return int(value)


def diversify(
    candidates: list[dict],
    limit: int,
) -> list[dict]:

    if not candidates:
        return []

    repository = BuckilRepository()

    ids = [
        int(item["buckil_id"])
        for item in candidates
        if item.get("buckil_id") is not None
        and not pd.isna(item.get("buckil_id"))
    ]

    if not ids:
        return []

    metadata = repository.get_diversity_metadata(ids)

    if metadata.empty:
        return candidates[:limit]

    metadata_map = {}

    for row in metadata.itertuples(index=False):

        buckil_id = safe_int(row.buckil_id)

        if buckil_id is None:
            continue

        metadata_map[buckil_id] = {
            "creator_id": safe_int(
                row.creator_id
            ),
            "category_id": safe_int(
                row.primary_category_id
            ),
        }

    creator_count = defaultdict(int)
    category_count = defaultdict(int)

    selected = []
    skipped = []

    for candidate in candidates:

        buckil_id = safe_int(
            candidate.get("buckil_id")
        )

        if buckil_id is None:
            continue

        meta = metadata_map.get(
            buckil_id,
            {},
        )

        creator_id = meta.get(
            "creator_id"
        )

        category_id = meta.get(
            "category_id"
        )

        # Creator diversity
        if (
            creator_id is not None
            and creator_count[creator_id]
            >= MAX_PER_CREATOR
        ):
            skipped.append(candidate)
            continue

        # Category diversity
        if (
            category_id is not None
            and category_count[category_id]
            >= MAX_PER_CATEGORY
        ):
            skipped.append(candidate)
            continue

        selected.append(candidate)

        if creator_id is not None:
            creator_count[creator_id] += 1

        if category_id is not None:
            category_count[category_id] += 1

        if len(selected) >= limit:
            break

    # Fill remaining positions if diversity filtering
    # removed too many candidates
    if len(selected) < limit:

        selected_ids = {
            int(item["buckil_id"])
            for item in selected
        }

        for candidate in skipped:

            buckil_id = safe_int(
                candidate.get("buckil_id")
            )

            if buckil_id is None:
                continue

            if buckil_id in selected_ids:
                continue

            selected.append(candidate)
            selected_ids.add(buckil_id)

            if len(selected) >= limit:
                break

    return selected[:limit]