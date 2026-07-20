from pathlib import Path

from app.schemas.portfolio_import_schema import (
    PortfolioImportPreviewResponse,
)
from app.services.import_parsers.csv_parser import (
    CSVPortfolioParser,
)
from app.services.portfolio_normalizer import (
    PortfolioNormalizer,
)


class PortfolioImportService:
    @staticmethod
    def preview(
        file_path: str,
    ) -> PortfolioImportPreviewResponse:
        """
        Parse, validate, and normalize an uploaded portfolio file.

        This method only returns a preview.
        It does not save holdings to the database.
        """

        path = Path(file_path)
        extension = path.suffix.lower()

        if extension != ".csv":
            raise ValueError(
                f"Unsupported file type: {extension or 'unknown'}"
            )

        result = CSVPortfolioParser.parse(
            file_path,
        )

        normalized_preview = PortfolioNormalizer.normalize(
            result["preview"],
        )

        warnings = result["warnings"]

        if result["valid_rows"] == 0:
            status = "failed"
            message = (
                "The file could not be imported because "
                "it contained no valid portfolio rows."
            )
        elif warnings:
            status = "ready_with_warnings"
            message = (
                "Portfolio parsed successfully with "
                f"{len(warnings)} warning(s)."
            )
        else:
            status = "ready"
            message = "Portfolio parsed successfully."

        return PortfolioImportPreviewResponse(
            file_name=path.name,
            file_type="csv",
            detected_broker=None,
            status=status,
            total_rows=result["total_rows"],
            valid_rows=result["valid_rows"],
            invalid_rows=result["invalid_rows"],
            preview=normalized_preview,
            warnings=warnings,
            metadata={
                "parser": "Generic CSV Parser",
                "normalizer": "Portfolio Normalizer",
                "parser_version": "1.0",
                "normalizer_version": "1.0",
            },
            message=message,
        )