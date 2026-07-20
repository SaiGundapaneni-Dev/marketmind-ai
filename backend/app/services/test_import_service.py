from pprint import pprint

from app.services.portfolio_import_service import (
    PortfolioImportService,
)

result = PortfolioImportService.preview(
    "sample_portfolio.csv"
)

pprint(result.model_dump())