import csv
from pathlib import Path

from app.schemas.portfolio_import_schema import (
    ImportWarning,
    NormalizedHoldingPreview,
)


class CSVPortfolioParser:
    """
    Generic CSV portfolio parser.

    Expected minimum columns:

    symbol
    quantity
    average_price

    Optional columns:

    name
    asset_type
    currency
    """

    REQUIRED_COLUMNS = {
        "symbol",
        "quantity",
        "average_price",
    }

    OPTIONAL_COLUMNS = {
        "name",
        "asset_type",
        "currency",
    }

    @staticmethod
    def parse(file_path: str):

        preview = []

        warnings = []

        path = Path(file_path)

        with open(
            path,
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:

            reader = csv.DictReader(csv_file)

            headers = {
                h.strip().lower()
                for h in reader.fieldnames or []
            }

            missing = (
                CSVPortfolioParser.REQUIRED_COLUMNS
                - headers
            )

            if missing:

                raise ValueError(
                    f"Missing required columns: {', '.join(sorted(missing))}"
                )

            total_rows = 0
            valid_rows = 0

            for row_number, row in enumerate(
                reader,
                start=2,
            ):

                total_rows += 1

                try:

                    symbol = row["symbol"].strip().upper()

                    quantity = float(
                        row["quantity"]
                    )

                    average_price = float(
                        row["average_price"]
                    )

                    if quantity <= 0:

                        raise ValueError(
                            "Quantity must be greater than zero."
                        )

                    preview.append(

                        NormalizedHoldingPreview(

                            symbol=symbol,

                            name=row.get("name"),

                            asset_type=row.get(
                                "asset_type",
                                "stock",
                            ),

                            quantity=quantity,

                            average_price=average_price,

                            currency=row.get(
                                "currency",
                                "USD",
                            ),

                            source_row=row_number,
                        )

                    )

                    valid_rows += 1

                except Exception as exc:

                    warnings.append(

                        ImportWarning(

                            row=row_number,

                            code="INVALID_ROW",

                            message=str(exc),
                        )

                    )

        return {

            "total_rows": total_rows,

            "valid_rows": valid_rows,

            "invalid_rows": total_rows
            - valid_rows,

            "preview": preview,

            "warnings": warnings,
        }