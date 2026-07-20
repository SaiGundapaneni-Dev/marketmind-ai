from pathlib import Path

import pytest

from app.schemas.portfolio_import_schema import (
    NormalizedHoldingPreview,
)
from app.services.portfolio_import_service import (
    PortfolioImportService,
)
from app.services.portfolio_normalizer import (
    PortfolioNormalizer,
)


def create_csv(
    directory: Path,
    file_name: str,
    content: str,
) -> Path:
    """
    Create a temporary CSV file for import testing.
    """

    file_path = directory / file_name

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return file_path


def test_portfolio_normalizer_standardizes_values():
    holdings = [
        NormalizedHoldingPreview(
            symbol=" aapl ",
            name=" Apple Inc. ",
            asset_type=" STOCK ",
            quantity=10,
            average_price=180.45,
            currency=" usd ",
            source_row=2,
        )
    ]

    result = PortfolioNormalizer.normalize(
        holdings,
    )

    assert len(result) == 1

    holding = result[0]

    assert holding.symbol == "AAPL"
    assert holding.name == "Apple Inc."
    assert holding.asset_type == "stock"
    assert holding.quantity == 10.0
    assert holding.average_price == 180.45
    assert holding.currency == "USD"
    assert holding.source_row == 2


def test_import_service_returns_ready_preview(
    tmp_path: Path,
):
    csv_file = create_csv(
        directory=tmp_path,
        file_name="portfolio.csv",
        content=(
            "symbol,name,quantity,average_price,"
            "asset_type,currency\n"
            "aapl, Apple Inc. ,10,180.45,STOCK,usd\n"
            "nvda,NVIDIA Corp,5,130.20,stock,USD\n"
        ),
    )

    result = PortfolioImportService.preview(
        str(csv_file),
    )

    assert result.file_name == "portfolio.csv"
    assert result.file_type == "csv"
    assert result.detected_broker is None
    assert result.status == "ready"

    assert result.total_rows == 2
    assert result.valid_rows == 2
    assert result.invalid_rows == 0

    assert len(result.preview) == 2
    assert result.warnings == []

    assert result.preview[0].symbol == "AAPL"
    assert result.preview[0].name == "Apple Inc."
    assert result.preview[0].asset_type == "stock"
    assert result.preview[0].currency == "USD"

    assert result.metadata["parser"] == (
        "Generic CSV Parser"
    )

    assert result.metadata["normalizer"] == (
        "Portfolio Normalizer"
    )

    assert result.message == (
        "Portfolio parsed successfully."
    )


def test_import_service_returns_warning_for_invalid_row(
    tmp_path: Path,
):
    csv_file = create_csv(
        directory=tmp_path,
        file_name="portfolio_with_error.csv",
        content=(
            "symbol,name,quantity,average_price,"
            "asset_type,currency\n"
            "AAPL,Apple Inc.,10,180.45,stock,USD\n"
            "NVDA,NVIDIA Corp,0,130.20,stock,USD\n"
        ),
    )

    result = PortfolioImportService.preview(
        str(csv_file),
    )

    assert result.status == "ready_with_warnings"

    assert result.total_rows == 2
    assert result.valid_rows == 1
    assert result.invalid_rows == 1

    assert len(result.preview) == 1
    assert len(result.warnings) == 1

    assert result.preview[0].symbol == "AAPL"

    warning = result.warnings[0]

    assert warning.row == 3
    assert warning.code == "INVALID_ROW"
    assert "Quantity must be greater than zero" in (
        warning.message
    )


def test_import_service_returns_failed_when_all_rows_invalid(
    tmp_path: Path,
):
    csv_file = create_csv(
        directory=tmp_path,
        file_name="invalid_portfolio.csv",
        content=(
            "symbol,name,quantity,average_price,"
            "asset_type,currency\n"
            "AAPL,Apple Inc.,0,180.45,stock,USD\n"
            "NVDA,NVIDIA Corp,-5,130.20,stock,USD\n"
        ),
    )

    result = PortfolioImportService.preview(
        str(csv_file),
    )

    assert result.status == "failed"

    assert result.total_rows == 2
    assert result.valid_rows == 0
    assert result.invalid_rows == 2

    assert result.preview == []
    assert len(result.warnings) == 2

    assert result.message == (
        "The file could not be imported because "
        "it contained no valid portfolio rows."
    )


def test_import_service_rejects_missing_columns(
    tmp_path: Path,
):
    csv_file = create_csv(
        directory=tmp_path,
        file_name="missing_columns.csv",
        content=(
            "symbol,name,quantity\n"
            "AAPL,Apple Inc.,10\n"
        ),
    )

    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        PortfolioImportService.preview(
            str(csv_file),
        )


def test_import_service_rejects_unsupported_file_type(
    tmp_path: Path,
):
    pdf_file = tmp_path / "portfolio.pdf"

    pdf_file.write_bytes(
        b"sample file content",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported file type",
    ):
        PortfolioImportService.preview(
            str(pdf_file),
        )