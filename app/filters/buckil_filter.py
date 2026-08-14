from app.config import RECENT_VIEW_EXCLUDE_HOURS
from app.repositories.buckil_repository import BuckilRepository


class BuckilFilter:
    def __init__(self):
        self.buckil_repository = BuckilRepository()

    def apply(self, user_id: int, candidates: list[dict]) -> list[dict]:
        if not candidates:
            return []

        ordered_ids = [int(item["buckil_id"]) for item in candidates]
        eligible = self.buckil_repository.get_eligible_ids(
            user_id=user_id,
            buckil_ids=ordered_ids,
            recent_hours=RECENT_VIEW_EXCLUDE_HOURS,
        )
        return [item for item in candidates if int(item["buckil_id"]) in eligible]
