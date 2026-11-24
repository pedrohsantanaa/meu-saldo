from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.movement import MovementRow
from app.services import movements as movements_service

router = APIRouter(prefix="/movements", tags=["movimentações"])


@router.get("", response_model=list[MovementRow])
def list_movements(
    date_from: date | None = None,
    date_to: date | None = None,
    type: Literal["income", "expense", "investment", "card_purchase"] | None = None,
    category_id: int | None = None,
    payment_method: Literal["dinheiro", "pix", "debito", "outra", "credito"]
    | None = None,
    card_id: int | None = None,
    search: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Movimentações unificadas: transações comuns e compras no cartão.

    As compras aparecem identificadas por `source: "card_purchase"`, com
    o cartão utilizado e a fatura em que consolidam; nunca viram
    movimentação comum (`spec.md` §7.2).
    """
    return movements_service.list_movements(
        db,
        current_user,
        date_from=date_from,
        date_to=date_to,
        movement_type=type,
        category_id=category_id,
        payment_method=payment_method,
        card_id=card_id,
        search=search,
    )
