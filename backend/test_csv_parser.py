from pprint import pprint

from app.services.import_parsers.csv_parser import (
    CSVPortfolioParser,
)

result = CSVPortfolioParser.parse(
    "sample_portfolio.csv"
)

pprint(result)