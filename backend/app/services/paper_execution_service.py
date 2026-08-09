from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from app.config.settings import settings
from app.execution.calculator import resolvePipSize
from app.journal.models import JournalEntryCreate
from app.journal.models import JournalOutcomeUpdate
from app.journal.models import TradeOutcome
from app.journal.models import TraderDecision
from app.journal.service import JournalService
from app.market.service import MarketService
from app.schemas.decision import DecisionContext
from app.schemas.decision_center import DecisionReport
from app.schemas.decision_execution_bridge import PaperExecutionSummary
from app.schemas.decision_execution_bridge import PaperPositionCloseSummary
from app.schemas.decision_execution_bridge import PaperOrderStatus
from app.schemas.decision_execution_bridge import PaperOrderSummary
from app.schemas.decision_execution_bridge import PaperPositionStatus
from app.schemas.decision_execution_bridge import PaperPositionSummary
from app.schemas.decision_execution_bridge import PaperPositionUpdateSummary


@dataclass(slots=True)
class PaperExecutionState:
    orders: dict[str, PaperOrderSummary]
    positions: dict[str, PaperPositionSummary]


class PaperPositionNotFoundError(KeyError):
    def __init__(self, position_id: str):
        super().__init__(position_id)
        self.position_id = position_id


class PaperMarketTickUnavailableError(RuntimeError):
    def __init__(self, symbol: str):
        super().__init__(symbol)
        self.symbol = symbol


class PaperExecutionService:
    """Session-scoped in-memory paper execution lifecycle isolated from live broker infrastructure."""

    def __init__(self):
        self._state = PaperExecutionState(orders={}, positions={})

    def execute(
        self,
        *,
        decision: DecisionContext,
        lot_size: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        decision_reference_id: str | None = None,
        decision_report: DecisionReport | None = None,
        journal_service: JournalService | None = None,
        timeframe: str | None = None,
        session: str | None = None,
        risk_percent: float | None = None,
        expected_rr: float | None = None,
        notes: str = "",
        tags: list[str] | None = None,
    ) -> PaperExecutionSummary:
        created_at = self._utc_now()
        order_id = f"paper-order-{uuid4()}"
        status_flow = [PaperOrderStatus.PREPARED]

        order = PaperOrderSummary(
            order_id=order_id,
            symbol=decision.symbol,
            side=decision.side.value,
            requested_volume=lot_size,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            status=PaperOrderStatus.PREPARED,
            created_at=created_at,
            decision_reference_id=decision_reference_id,
        )
        self._state.orders[order_id] = order

        status_flow.append(PaperOrderStatus.SUBMITTED)
        order = order.model_copy(update={"status": PaperOrderStatus.SUBMITTED})
        self._state.orders[order_id] = order

        filled_at = self._utc_now()
        status_flow.append(PaperOrderStatus.FILLED)
        order = order.model_copy(
            update={
                "status": PaperOrderStatus.FILLED,
                "filled_at": filled_at,
            }
        )
        self._state.orders[order_id] = order

        position_id = f"paper-position-{uuid4()}"
        position = PaperPositionSummary(
            position_id=position_id,
            symbol=decision.symbol,
            side=decision.side.value,
            volume=lot_size,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            status=PaperPositionStatus.OPEN,
            opened_at=filled_at,
            updated_at=filled_at,
            originating_order_id=order_id,
        )

        if decision_report is not None and journal_service is not None:
            journal_entry = journal_service.createEntry(
                JournalEntryCreate(
                    symbol=decision.symbol,
                    timeframe=timeframe or settings.defaultTimeframe,
                    session=session or "UNSPECIFIED",
                    entryPrice=entry_price,
                    stopLoss=stop_loss,
                    takeProfit=take_profit,
                    positionSize=lot_size,
                    riskPercent=risk_percent or 0.0,
                    expectedRR=expected_rr or 0.0,
                    traderDecision=TraderDecision.FOLLOWED_OSCAR,
                    decisionReport=decision_report,
                    personalNotes=notes,
                    tags=self._journal_tags(tags or []),
                )
            )
            position = position.model_copy(update={"journal_entry_id": journal_entry.id})

        self._state.positions[position_id] = position

        return PaperExecutionSummary(
            order=order,
            position=position,
            deterministic_fill_price=entry_price,
            order_status_flow=status_flow,
        )

    @property
    def state(self) -> PaperExecutionState:
        return self._state

    def update_position(self, *, position_id: str) -> PaperPositionUpdateSummary:
        position = self._require_position(position_id)
        marked_at = self._utc_now()

        if position.status == PaperPositionStatus.CLOSED:
            mark_price = float(position.close_price or position.last_mark_price or position.entry_price)
            unrealized_pnl = float(position.unrealized_pnl or 0.0)
            return PaperPositionUpdateSummary(
                position=position,
                mark_price=mark_price,
                unrealized_pnl=unrealized_pnl,
                marked_at=position.last_marked_at or position.closed_at or marked_at,
            )

        tick = MarketService.latest_tick(position.symbol)
        if tick is None:
            raise PaperMarketTickUnavailableError(position.symbol)

        mark_price = self._mark_price(position.side, tick.bid, tick.ask)
        unrealized_pnl = self._calculate_pnl(
            side=position.side,
            symbol=position.symbol,
            entry_price=position.entry_price,
            exit_price=mark_price,
            volume=position.volume,
        )
        updated = position.model_copy(
            update={
                "last_mark_price": mark_price,
                "last_marked_at": marked_at,
                "updated_at": marked_at,
                "unrealized_pnl": unrealized_pnl,
            }
        )
        self._state.positions[position_id] = updated

        return PaperPositionUpdateSummary(
            position=updated,
            mark_price=mark_price,
            unrealized_pnl=unrealized_pnl,
            marked_at=marked_at,
        )

    def close_position(
        self,
        *,
        position_id: str,
        journal_service: JournalService | None = None,
    ) -> PaperPositionCloseSummary:
        position = self._require_position(position_id)

        if position.status == PaperPositionStatus.CLOSED:
            realized_pnl = round(float(position.realized_pnl or 0.0), 2)
            realized_rr = round(float(position.realized_rr or 0.0), 2)
            close_price = float(position.close_price or position.last_mark_price or position.entry_price)
            closed_at = position.closed_at or position.updated_at or position.opened_at
            return PaperPositionCloseSummary(
                position=position,
                close_price=close_price,
                realized_pnl=realized_pnl,
                realized_rr=realized_rr,
                closed_at=closed_at,
                outcome=self._outcome_from_pnl(realized_pnl).value,
                journal_entry_id=position.journal_entry_id,
                already_closed=True,
            )

        tick = MarketService.latest_tick(position.symbol)
        if tick is None:
            raise PaperMarketTickUnavailableError(position.symbol)

        closed_at = self._utc_now()
        close_price = self._mark_price(position.side, tick.bid, tick.ask)
        realized_pnl = self._calculate_pnl(
            side=position.side,
            symbol=position.symbol,
            entry_price=position.entry_price,
            exit_price=close_price,
            volume=position.volume,
        )
        realized_rr = self._calculate_rr(
            symbol=position.symbol,
            entry_price=position.entry_price,
            stop_loss=position.stop_loss,
            realized_pnl=realized_pnl,
            volume=position.volume,
        )
        updated = position.model_copy(
            update={
                "status": PaperPositionStatus.CLOSED,
                "close_price": close_price,
                "closed_at": closed_at,
                "updated_at": closed_at,
                "last_mark_price": close_price,
                "last_marked_at": closed_at,
                "unrealized_pnl": 0.0,
                "realized_pnl": realized_pnl,
                "realized_rr": realized_rr,
            }
        )
        self._state.positions[position_id] = updated

        if journal_service is not None and updated.journal_entry_id is not None:
            journal_service.updateOutcome(
                updated.journal_entry_id,
                JournalOutcomeUpdate(
                    tradeOutcome=self._outcome_from_pnl(realized_pnl),
                    profitLoss=realized_pnl,
                    realizedRR=realized_rr,
                    durationMinutes=self._duration_minutes(updated.opened_at, closed_at),
                    closeReason="Paper position closed manually",
                ),
            )

        return PaperPositionCloseSummary(
            position=updated,
            close_price=close_price,
            realized_pnl=realized_pnl,
            realized_rr=realized_rr,
            closed_at=closed_at,
            outcome=self._outcome_from_pnl(realized_pnl).value,
            journal_entry_id=updated.journal_entry_id,
            already_closed=False,
        )

    def _require_position(self, position_id: str) -> PaperPositionSummary:
        position = self._state.positions.get(position_id)
        if position is None:
            raise PaperPositionNotFoundError(position_id)
        return position

    @staticmethod
    def _mark_price(side: str, bid: float, ask: float) -> float:
        return float(bid if side.upper() == "BUY" else ask)

    @staticmethod
    def _calculate_pnl(*, side: str, symbol: str, entry_price: float, exit_price: float, volume: float) -> float:
        pip_size = resolvePipSize(symbol)
        if pip_size <= 0 or volume <= 0:
            return 0.0

        if side.upper() == "BUY":
            signed_pips = (exit_price - entry_price) / pip_size
        else:
            signed_pips = (entry_price - exit_price) / pip_size

        realized_pnl = signed_pips * 10.0 * volume
        return round(realized_pnl, 2)

    @staticmethod
    def _calculate_rr(*, symbol: str, entry_price: float, stop_loss: float, realized_pnl: float, volume: float) -> float:
        pip_size = resolvePipSize(symbol)
        if pip_size <= 0 or volume <= 0:
            return 0.0

        risk_pips = abs(entry_price - stop_loss) / pip_size
        risk_money = risk_pips * 10.0 * volume
        if risk_money <= 0:
            return 0.0

        return round(realized_pnl / risk_money, 2)

    @staticmethod
    def _outcome_from_pnl(realized_pnl: float) -> TradeOutcome:
        if realized_pnl > 0:
            return TradeOutcome.WIN
        if realized_pnl < 0:
            return TradeOutcome.LOSS
        return TradeOutcome.BREAK_EVEN

    @staticmethod
    def _duration_minutes(opened_at: str, closed_at: str) -> int:
        opened = datetime.fromisoformat(opened_at)
        closed = datetime.fromisoformat(closed_at)
        duration = closed - opened
        return max(int(duration.total_seconds() // 60), 0)

    @staticmethod
    def _journal_tags(tags: list[str]) -> list[str]:
        normalized = list(tags)
        if "paper-execution" not in normalized:
            normalized.append("paper-execution")
        return normalized

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()


_paper_execution_service = PaperExecutionService()


def get_paper_execution_service() -> PaperExecutionService:
    return _paper_execution_service
