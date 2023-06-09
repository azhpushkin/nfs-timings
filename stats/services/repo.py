from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

from django.db.models import QuerySet
from django.db.models.expressions import RawSQL

from stats.models import Race, StintInfo


class SortOrder(Enum):
    BEST = 'best'
    AVERAGE = 'average'
    SECTOR_1 = 'sector_1'
    SECTOR_2 = 'sector_2'
    KART = 'kart'


SORT_MAPPING = {
    SortOrder.BEST: 'best_lap',
    SortOrder.AVERAGE: 'avg_80',
    SortOrder.SECTOR_1: 'best_sector_1',
    SortOrder.SECTOR_2: 'best_sector_2',
    SortOrder.KART: 'kart',
}


def get_stints(
    race: Race,
    team: Optional[int] = None,
    kart: Optional[int] = None,
    sort_by: Optional[SortOrder] = None,
) -> QuerySet[StintInfo]:
    stints = StintInfo.objects.all()

    if team:
        stints = stints.filter(team)
    if kart:
        stints = stints.filter(kart=kart)
    if sort_by:
        field = SORT_MAPPING[sort_by]
        stints = stints.order_by(field)

    return stints


def pick_best_kart_by(qs: QuerySet[StintInfo], sort_by: SortOrder) -> List[StintInfo]:
    field = SORT_MAPPING[sort_by]
    qs = qs.annotate(
        index=RawSQL(f'ROW_NUMBER() OVER(partition by kart ORDER BY {field})', ())
    )
    return [stint for stint in qs if stint.index == 1]
