from collections import defaultdict

from sqlalchemy.orm import Session

from app.repositories.portfolio_repository import PortfolioRepository
from app.services.price_service import PriceService


class PortfolioService:

    @staticmethod
    def create_holding(db: Session, holding_data):
        return PortfolioRepository.create_holding(
            db,
            holding_data,
        )

    @staticmethod
    def update_holding(
        db: Session,
        holding_id: int,
        holding_data,
    ):
        return PortfolioRepository.update_holding(
            db,
            holding_id,
            holding_data,
        )

    @staticmethod
    def get_holding_by_id(
        db: Session,
        holding_id: int,
    ):
        return PortfolioRepository.get_holding_by_id(
            db,
            holding_id,
        )

    @staticmethod
    def delete_holding(
        db: Session,
        holding_id: int,
    ):
        return PortfolioRepository.delete_holding(
            db,
            holding_id,
        )

    @staticmethod
    def calculate_concentration_risk(
        holdings: list[dict],
    ):
        priced_holdings = [
            holding
            for holding in holdings
            if holding["price_status"] == "available"
        ]

        if not priced_holdings:
            return {
                "risk_level": "unknown",
                "largest_position_percent": 0.0,
                "top_three_percent": 0.0,
                "concentrated_positions": [],
                "message": (
                    "Concentration risk could not be calculated "
                    "because no holdings have available prices."
                ),
            }

        sorted_holdings = sorted(
            priced_holdings,
            key=lambda holding: holding[
                "allocation_percent"
            ],
            reverse=True,
        )

        largest_position_percent = sorted_holdings[0][
            "allocation_percent"
        ]

        top_three_percent = round(
            sum(
                holding["allocation_percent"]
                for holding in sorted_holdings[:3]
            ),
            2,
        )

        concentrated_positions = [
            {
                "symbol": holding["symbol"],
                "name": holding["name"],
                "allocation_percent": holding[
                    "allocation_percent"
                ],
            }
            for holding in sorted_holdings
            if holding["allocation_percent"] >= 20
        ]

        if (
            largest_position_percent >= 35
            or top_three_percent >= 75
        ):
            risk_level = "high"
            message = (
                "Your portfolio has high concentration risk. "
                "A large portion of the portfolio is controlled "
                "by one holding or the top three holdings."
            )

        elif (
            largest_position_percent >= 25
            or top_three_percent >= 60
        ):
            risk_level = "medium"
            message = (
                "Your portfolio has moderate concentration risk. "
                "Monitor the largest positions and consider whether "
                "the allocation matches your risk tolerance."
            )

        else:
            risk_level = "low"
            message = (
                "Your portfolio has relatively low concentration "
                "risk based on current holding allocations."
            )

        return {
            "risk_level": risk_level,
            "largest_position_percent": round(
                largest_position_percent,
                2,
            ),
            "top_three_percent": top_three_percent,
            "concentrated_positions": concentrated_positions,
            "message": message,
        }

    @staticmethod
    def calculate_performance_insights(
        holdings: list[dict],
    ):
        priced_holdings = [
            holding
            for holding in holdings
            if holding["price_status"] == "available"
        ]

        profitable_holdings = [
            holding
            for holding in priced_holdings
            if holding["profit"] > 0
        ]

        losing_holdings = [
            holding
            for holding in priced_holdings
            if holding["profit"] < 0
        ]

        breakeven_holdings = [
            holding
            for holding in priced_holdings
            if holding["profit"] == 0
        ]

        if not priced_holdings:
            return {
                "top_performer": None,
                "weakest_performer": None,
                "largest_profit_contributor": None,
                "largest_loss_contributor": None,
                "profitable_holdings_count": 0,
                "losing_holdings_count": 0,
                "breakeven_holdings_count": 0,
                "message": (
                    "Performance insights could not be calculated "
                    "because no holdings have available prices."
                ),
            }

        top_performer = max(
            priced_holdings,
            key=lambda holding: holding[
                "profit_percent"
            ],
        )

        weakest_performer = min(
            priced_holdings,
            key=lambda holding: holding[
                "profit_percent"
            ],
        )

        largest_profit_contributor = None

        if profitable_holdings:
            largest_profit = max(
                profitable_holdings,
                key=lambda holding: holding["profit"],
            )

            largest_profit_contributor = {
                "symbol": largest_profit["symbol"],
                "name": largest_profit["name"],
                "profit": largest_profit["profit"],
                "profit_percent": largest_profit[
                    "profit_percent"
                ],
            }

        largest_loss_contributor = None

        if losing_holdings:
            largest_loss = min(
                losing_holdings,
                key=lambda holding: holding["profit"],
            )

            largest_loss_contributor = {
                "symbol": largest_loss["symbol"],
                "name": largest_loss["name"],
                "profit": largest_loss["profit"],
                "profit_percent": largest_loss[
                    "profit_percent"
                ],
            }

        return {
            "top_performer": {
                "symbol": top_performer["symbol"],
                "name": top_performer["name"],
                "profit": top_performer["profit"],
                "profit_percent": top_performer[
                    "profit_percent"
                ],
            },
            "weakest_performer": {
                "symbol": weakest_performer["symbol"],
                "name": weakest_performer["name"],
                "profit": weakest_performer["profit"],
                "profit_percent": weakest_performer[
                    "profit_percent"
                ],
            },
            "largest_profit_contributor": (
                largest_profit_contributor
            ),
            "largest_loss_contributor": (
                largest_loss_contributor
            ),
            "profitable_holdings_count": len(
                profitable_holdings
            ),
            "losing_holdings_count": len(
                losing_holdings
            ),
            "breakeven_holdings_count": len(
                breakeven_holdings
            ),
            "message": (
                f"{len(profitable_holdings)} holdings are profitable, "
                f"{len(losing_holdings)} are currently at a loss, "
                f"and {len(breakeven_holdings)} are near break-even."
            ),
        }

    @staticmethod
    def calculate_health_score(
        holdings: list[dict],
        concentration_risk: dict,
        performance_insights: dict,
    ):
        total_holdings = len(holdings)

        priced_holdings = [
            holding
            for holding in holdings
            if holding["price_status"] == "available"
        ]

        priced_count = len(priced_holdings)

        # Diversification score: maximum 25 points.
        if total_holdings >= 10:
            diversification_score = 25
        elif total_holdings >= 7:
            diversification_score = 20
        elif total_holdings >= 5:
            diversification_score = 15
        elif total_holdings >= 3:
            diversification_score = 10
        elif total_holdings >= 1:
            diversification_score = 5
        else:
            diversification_score = 0

        # Concentration score: maximum 25 points.
        risk_level = concentration_risk.get(
            "risk_level",
            "unknown",
        )

        concentration_scores = {
            "low": 25,
            "medium": 15,
            "high": 5,
            "unknown": 0,
        }

        concentration_score = concentration_scores.get(
            risk_level,
            0,
        )

        # Profitability score: maximum 25 points.
        profitable_count = performance_insights.get(
            "profitable_holdings_count",
            0,
        )

        profitability_ratio = (
            profitable_count / priced_count
            if priced_count > 0
            else 0.0
        )

        profitability_score = round(
            profitability_ratio * 25,
            2,
        )

        # Pricing coverage score: maximum 25 points.
        pricing_coverage_ratio = (
            priced_count / total_holdings
            if total_holdings > 0
            else 0.0
        )

        pricing_coverage_score = round(
            pricing_coverage_ratio * 25,
            2,
        )

        total_score = round(
            diversification_score
            + concentration_score
            + profitability_score
            + pricing_coverage_score,
            2,
        )

        if total_score >= 85:
            rating = "excellent"
            message = (
                "Your portfolio has strong overall health based on "
                "diversification, concentration, profitability, and "
                "pricing coverage."
            )

        elif total_score >= 70:
            rating = "good"
            message = (
                "Your portfolio is in good condition, with some room "
                "to improve diversification or concentration risk."
            )

        elif total_score >= 50:
            rating = "fair"
            message = (
                "Your portfolio has fair overall health. Review "
                "concentration, losing positions, and diversification."
            )

        else:
            rating = "weak"
            message = (
                "Your portfolio health score is currently weak. "
                "Several risk or data-quality areas may need attention."
            )

        return {
            "score": total_score,
            "rating": rating,
            "components": {
                "diversification_score": diversification_score,
                "concentration_score": concentration_score,
                "profitability_score": profitability_score,
                "pricing_coverage_score": pricing_coverage_score,
            },
            "message": message,
        }
        
    @staticmethod
    def calculate(db: Session):
        db_holdings = PortfolioRepository.get_holdings(db)

        holdings = []

        total_cost = 0.0
        total_value = 0.0

        priced_holdings_count = 0
        unpriced_holdings_count = 0

        for asset in db_holdings:
            current_price = PriceService.get_live_price(
                asset.symbol
            )

            quantity = float(asset.quantity)
            average_price = float(asset.average_price)

            cost = quantity * average_price
            total_cost += cost

            if current_price is None:
                unpriced_holdings_count += 1

                holdings.append({
                    "id": asset.id,
                    "asset_type": asset.asset_type,
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "quantity": quantity,
                    "average_price": round(
                        average_price,
                        2,
                    ),
                    "current_price": None,
                    "cost": round(cost, 2),
                    "current_value": 0.0,
                    "profit": 0.0,
                    "profit_percent": 0.0,
                    "allocation_percent": 0.0,
                    "price_status": "unavailable",
                })

                continue

            priced_holdings_count += 1
            current_price = float(current_price)

            value = quantity * current_price
            profit = value - cost

            profit_percent = (
                (profit / cost) * 100
                if cost > 0
                else 0.0
            )

            total_value += value

            holdings.append({
                "id": asset.id,
                "asset_type": asset.asset_type,
                "symbol": asset.symbol,
                "name": asset.name,
                "quantity": quantity,
                "average_price": round(
                    average_price,
                    2,
                ),
                "current_price": round(
                    current_price,
                    2,
                ),
                "cost": round(cost, 2),
                "current_value": round(value, 2),
                "profit": round(profit, 2),
                "profit_percent": round(
                    profit_percent,
                    2,
                ),
                "allocation_percent": 0.0,
                "price_status": "available",
            })

        allocation_by_asset_type = defaultdict(float)

        for holding in holdings:
            current_value = holding["current_value"]

            allocation_percent = (
                (current_value / total_value) * 100
                if total_value > 0
                else 0.0
            )

            holding["allocation_percent"] = round(
                allocation_percent,
                2,
            )

            asset_type = (
                holding["asset_type"]
                or "unknown"
            )

            allocation_by_asset_type[
                asset_type
            ] += current_value

        asset_type_allocation = []

        for asset_type, value in allocation_by_asset_type.items():
            percentage = (
                (value / total_value) * 100
                if total_value > 0
                else 0.0
            )

            asset_type_allocation.append({
                "asset_type": asset_type,
                "value": round(value, 2),
                "allocation_percent": round(
                    percentage,
                    2,
                ),
            })

        asset_type_allocation.sort(
            key=lambda item: item["value"],
            reverse=True,
        )

        largest_holding = None

        priced_holdings = [
            holding
            for holding in holdings
            if holding["price_status"] == "available"
        ]

        if priced_holdings:
            largest = max(
                priced_holdings,
                key=lambda holding: holding[
                    "current_value"
                ],
            )

            largest_holding = {
                "symbol": largest["symbol"],
                "name": largest["name"],
                "current_value": largest[
                    "current_value"
                ],
                "allocation_percent": largest[
                    "allocation_percent"
                ],
            }

        concentration_risk = (
            PortfolioService.calculate_concentration_risk(
                holdings
            )
        )

        performance_insights = (
            PortfolioService.calculate_performance_insights(
                holdings
            )
        )
        
        health_score = (
            PortfolioService.calculate_health_score(
                holdings,
                concentration_risk,
                performance_insights,
            )
        )       

        total_profit = total_value - total_cost

        total_return = (
            (total_profit / total_cost) * 100
            if total_cost > 0
            else 0.0
        )

        return {
            "summary": {
                "total_cost": round(total_cost, 2),
                "total_value": round(total_value, 2),
                "total_profit": round(
                    total_profit,
                    2,
                ),
                "total_return_percent": round(
                    total_return,
                    2,
                ),
                "holdings_count": len(holdings),
                "priced_holdings_count": (
                    priced_holdings_count
                ),
                "unpriced_holdings_count": (
                    unpriced_holdings_count
                ),
            },
            "allocation": {
                "by_asset_type": asset_type_allocation,
                "largest_holding": largest_holding,
            },
            "concentration_risk": concentration_risk,
            "performance_insights": performance_insights,
            "health_score": health_score,            
            "holdings": holdings,
        }