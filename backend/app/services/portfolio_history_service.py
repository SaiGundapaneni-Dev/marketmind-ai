from datetime import date

from sqlalchemy.orm import Session

from app.repositories.portfolio_snapshot_repository import PortfolioSnapshotRepository
from app.services.portfolio_service import PortfolioService


class PortfolioHistoryService:

    @staticmethod
    def create_daily_snapshot(db: Session, force: bool = False):
        existing = PortfolioSnapshotRepository.get_for_day(db, date.today())

        if existing and not force:
            return existing

        portfolio = PortfolioService.calculate(db)
        return PortfolioSnapshotRepository.create(db, portfolio)

    @staticmethod
    def get_history(db: Session, limit: int = 365):
        return PortfolioSnapshotRepository.list_history(db, limit)

    @staticmethod
    def get_performance(db: Session, limit: int = 365) -> dict:
        snapshots = PortfolioSnapshotRepository.list_history(db, limit)

        if not snapshots:
            return {
                "current_value": 0.0,
                "previous_value": None,
                "change": 0.0,
                "change_percent": 0.0,
                "highest_value": 0.0,
                "lowest_value": 0.0,
                "best_day_change": 0.0,
                "worst_day_change": 0.0,
                "snapshot_count": 0,
            }

        current = snapshots[-1]
        previous = snapshots[-2] if len(snapshots) > 1 else None
        change = current.total_value - previous.total_value if previous else 0.0
        change_percent = (
            (change / previous.total_value) * 100
            if previous and previous.total_value > 0
            else 0.0
        )

        daily_changes = [
            snapshots[index].total_value - snapshots[index - 1].total_value
            for index in range(1, len(snapshots))
        ]

        return {
            "current_value": round(current.total_value, 2),
            "previous_value": round(previous.total_value, 2) if previous else None,
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "highest_value": round(max(item.total_value for item in snapshots), 2),
            "lowest_value": round(min(item.total_value for item in snapshots), 2),
            "best_day_change": round(max(daily_changes) if daily_changes else 0.0, 2),
            "worst_day_change": round(min(daily_changes) if daily_changes else 0.0, 2),
            "snapshot_count": len(snapshots),
        }

    @staticmethod
    def get_contributors(db: Session) -> dict:
        portfolio = PortfolioService.calculate(db)
        holdings = portfolio["holdings"]
        total_absolute_profit = sum(
            abs(item["profit"])
            for item in holdings
            if item["price_status"] == "available"
        )

        contributors = []
        for item in holdings:
            if item["price_status"] != "available":
                continue

            contributors.append({
                "symbol": item["symbol"],
                "name": item["name"],
                "profit": item["profit"],
                "profit_percent": item["profit_percent"],
                "contribution_percent": round(
                    (item["profit"] / total_absolute_profit) * 100
                    if total_absolute_profit > 0 else 0.0,
                    2,
                ),
            })

        return {
            "top_contributors": sorted(
                contributors,
                key=lambda item: item["profit"],
                reverse=True,
            )[:3],
            "bottom_contributors": sorted(
                contributors,
                key=lambda item: item["profit"],
            )[:3],
        }

    @staticmethod
    def get_changes(db: Session) -> dict:
        current = PortfolioSnapshotRepository.get_latest(db)
        previous = PortfolioSnapshotRepository.get_previous(db)

        if current is None:
            return {
                "has_previous_snapshot": False,
                "value_change": 0.0,
                "value_change_percent": 0.0,
                "profit_change": 0.0,
                "return_change": 0.0,
                "health_score_change": 0.0,
                "holdings_count_change": 0,
                "summary": ["Create a portfolio snapshot to begin tracking changes."],
            }

        if previous is None:
            return {
                "has_previous_snapshot": False,
                "value_change": 0.0,
                "value_change_percent": 0.0,
                "profit_change": 0.0,
                "return_change": 0.0,
                "health_score_change": 0.0,
                "holdings_count_change": 0,
                "summary": ["A baseline snapshot exists. More history is needed for comparison."],
            }

        value_change = current.total_value - previous.total_value
        value_change_percent = (
            (value_change / previous.total_value) * 100
            if previous.total_value > 0 else 0.0
        )
        profit_change = current.total_profit - previous.total_profit
        return_change = current.total_return_percent - previous.total_return_percent
        health_change = current.health_score - previous.health_score
        holdings_change = current.holdings_count - previous.holdings_count

        summary = [
            f"Portfolio value changed by ${value_change:,.2f} ({value_change_percent:.2f}%).",
            f"Unrealized profit changed by ${profit_change:,.2f}.",
            f"Portfolio return changed by {return_change:.2f} percentage points.",
            f"Health score changed by {health_change:.2f} points.",
        ]

        if holdings_change != 0:
            summary.append(f"Holdings count changed by {holdings_change}.")

        return {
            "has_previous_snapshot": True,
            "value_change": round(value_change, 2),
            "value_change_percent": round(value_change_percent, 2),
            "profit_change": round(profit_change, 2),
            "return_change": round(return_change, 2),
            "health_score_change": round(health_change, 2),
            "holdings_count_change": holdings_change,
            "summary": summary,
        }
