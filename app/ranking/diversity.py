def diversify(candidates: list[dict], limit: int) -> list[dict]:
    """
    Phase-2 extension point.
    In V1 this keeps ranking order unchanged.
    Later use Buckil categories/creator to cap repeated topics and creators.
    """
    return candidates[:limit]
