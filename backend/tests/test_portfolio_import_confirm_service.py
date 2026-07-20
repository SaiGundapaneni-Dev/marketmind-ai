import pytest

from app.services.portfolio_import_confirm_service import (
    PortfolioImportConfirmService,
)


def test_calculate_merged_average_price():
    result = (
        PortfolioImportConfirmService
        .calculate_merged_average_price(
            existing_quantity=10,
            existing_average_price=100,
            imported_quantity=5,
            imported_average_price=130,
        )
    )

    assert result == pytest.approx(110.0)


def test_calculate_merged_average_price_equal_cost():
    result = (
        PortfolioImportConfirmService
        .calculate_merged_average_price(
            existing_quantity=5,
            existing_average_price=200,
            imported_quantity=5,
            imported_average_price=200,
        )
    )

    assert result == pytest.approx(200.0)


def test_calculate_merged_average_price_rejects_zero_total():
    with pytest.raises(
        ValueError,
        match="merged quantity must be greater than zero",
    ):
        (
            PortfolioImportConfirmService
            .calculate_merged_average_price(
                existing_quantity=0,
                existing_average_price=100,
                imported_quantity=0,
                imported_average_price=120,
            )
        )