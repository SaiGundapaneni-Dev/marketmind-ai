from sqlalchemy.orm import Session

from app.repositories.portfolio_repository import PortfolioRepository
from app.schemas.portfolio_import_schema import (
    ImportWarning,
    PortfolioImportConfirmRequest,
    PortfolioImportConfirmResponse,
)


class PortfolioImportConfirmService:
    @staticmethod
    def calculate_merged_average_price(
        existing_quantity: float,
        existing_average_price: float,
        imported_quantity: float,
        imported_average_price: float,
    ) -> float:
        total_quantity = existing_quantity + imported_quantity

        if total_quantity <= 0:
            raise ValueError(
                "The merged quantity must be greater than zero."
            )

        existing_cost = existing_quantity * existing_average_price
        imported_cost = imported_quantity * imported_average_price

        return (existing_cost + imported_cost) / total_quantity

    @staticmethod
    def confirm(
        db: Session,
        request: PortfolioImportConfirmRequest,
        user_id: int,
    ) -> PortfolioImportConfirmResponse:
        portfolio = (
            PortfolioRepository.get_or_create_default_portfolio(
                db,
                user_id,
            )
        )

        imported_count = 0
        skipped_count = 0
        failed_count = 0

        imported_symbols: list[str] = []
        warnings: list[ImportWarning] = []

        try:
            for holding_data in request.holdings:
                symbol = holding_data.symbol.strip().upper()

                try:
                    existing_holding = (
                        PortfolioRepository.get_holding_by_symbol(
                            db,
                            user_id,
                            symbol,
                        )
                    )

                    if existing_holding is None:
                        PortfolioRepository.add_holding_without_commit(
                            db=db,
                            portfolio_id=portfolio.id,
                            holding_data=holding_data,
                        )

                        imported_count += 1
                        imported_symbols.append(symbol)
                        continue

                    if request.duplicate_strategy == "skip":
                        skipped_count += 1

                        warnings.append(
                            ImportWarning(
                                row=holding_data.source_row,
                                code="DUPLICATE_SKIPPED",
                                message=(
                                    f"{symbol} already exists and "
                                    "was skipped."
                                ),
                            )
                        )
                        continue

                    if request.duplicate_strategy == "replace":
                        existing_holding.asset_type = (
                            holding_data.asset_type.strip().lower()
                        )
                        existing_holding.symbol = symbol
                        existing_holding.name = (
                            holding_data.name.strip()
                            if holding_data.name
                            else symbol
                        )
                        existing_holding.quantity = float(
                            holding_data.quantity
                        )
                        existing_holding.average_price = float(
                            holding_data.average_price
                        )
                        existing_holding.currency = (
                            holding_data.currency.strip().upper()
                        )

                        imported_count += 1
                        imported_symbols.append(symbol)
                        continue

                    if request.duplicate_strategy == "merge":
                        existing_quantity = float(
                            existing_holding.quantity
                        )
                        imported_quantity = float(
                            holding_data.quantity
                        )

                        merged_average_price = (
                            PortfolioImportConfirmService
                            .calculate_merged_average_price(
                                existing_quantity=existing_quantity,
                                existing_average_price=float(
                                    existing_holding.average_price
                                ),
                                imported_quantity=imported_quantity,
                                imported_average_price=float(
                                    holding_data.average_price
                                ),
                            )
                        )

                        existing_holding.quantity = (
                            existing_quantity + imported_quantity
                        )
                        existing_holding.average_price = (
                            merged_average_price
                        )
                        existing_holding.asset_type = (
                            holding_data.asset_type.strip().lower()
                        )
                        existing_holding.currency = (
                            holding_data.currency.strip().upper()
                        )

                        if holding_data.name:
                            existing_holding.name = (
                                holding_data.name.strip()
                            )

                        imported_count += 1
                        imported_symbols.append(symbol)
                        continue

                    raise ValueError(
                        "Unsupported duplicate strategy: "
                        f"{request.duplicate_strategy}"
                    )

                except Exception as exc:
                    failed_count += 1

                    warnings.append(
                        ImportWarning(
                            row=holding_data.source_row,
                            code="IMPORT_ROW_FAILED",
                            message=(
                                f"{symbol} could not be imported: "
                                f"{exc}"
                            ),
                        )
                    )

            db.commit()

        except Exception:
            db.rollback()
            raise

        if failed_count > 0:
            message = (
                "Portfolio import completed with "
                f"{failed_count} failed holding(s)."
            )
        elif skipped_count > 0:
            message = (
                "Portfolio import completed with "
                f"{skipped_count} skipped duplicate(s)."
            )
        else:
            message = "Portfolio holdings imported successfully."

        return PortfolioImportConfirmResponse(
            imported_count=imported_count,
            skipped_count=skipped_count,
            failed_count=failed_count,
            imported_symbols=imported_symbols,
            warnings=warnings,
            message=message,
        )