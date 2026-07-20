from app.schemas.portfolio_import_schema import (
    NormalizedHoldingPreview,
)


class PortfolioNormalizer:
    @staticmethod
    def normalize(
        holdings: list[NormalizedHoldingPreview],
    ) -> list[NormalizedHoldingPreview]:
        """
        Standardize imported holdings into Vestora's internal format.
        """

        normalized_holdings: list[
            NormalizedHoldingPreview
        ] = []

        for holding in holdings:
            symbol = holding.symbol.strip().upper()

            name = (
                holding.name.strip()
                if holding.name
                else None
            )

            asset_type = (
                holding.asset_type.strip().lower()
                if holding.asset_type
                else "stock"
            )

            currency = (
                holding.currency.strip().upper()
                if holding.currency
                else "USD"
            )

            normalized_holdings.append(
                NormalizedHoldingPreview(
                    symbol=symbol,
                    name=name,
                    asset_type=asset_type,
                    quantity=float(holding.quantity),
                    average_price=float(
                        holding.average_price
                    ),
                    currency=currency,
                    source_row=holding.source_row,
                )
            )

        return normalized_holdings