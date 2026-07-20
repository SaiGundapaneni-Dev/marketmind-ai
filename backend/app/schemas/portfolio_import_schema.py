from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class NormalizedHoldingPreview(BaseModel):
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Normalized investment symbol.",
    )

    name: str | None = Field(
        default=None,
        description="Investment or company name when available.",
    )

    asset_type: str = Field(
        default="stock",
        description="Normalized asset type.",
    )

    quantity: float = Field(
        ...,
        gt=0,
        description="Number of units held.",
    )

    average_price: float = Field(
        ...,
        ge=0,
        description="Average purchase price per unit.",
    )

    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        description="Three-letter currency code.",
    )

    source_row: int | None = Field(
        default=None,
        ge=1,
        description="Original row number from the imported file.",
    )
    
    @field_validator(
        "symbol",
        "name",
        "asset_type",
        "currency",
        mode="before",
    )
    @classmethod
    def strip_text_values(cls, value):
        """
        Remove surrounding whitespace before Pydantic applies
        length validation.
        """

        if isinstance(value, str):
            stripped_value = value.strip()

            if not stripped_value:
                return None

            return stripped_value

        return value


class ImportWarning(BaseModel):
    row: int | None = Field(
        default=None,
        ge=1,
    )

    code: str = Field(
        ...,
        min_length=1,
        description="Machine-readable warning code.",
    )

    message: str = Field(
        ...,
        min_length=1,
        description="Human-readable warning description.",
    )


class PortfolioImportPreviewResponse(BaseModel):
    file_name: str

    file_type: Literal["csv", "pdf", "unknown"]

    detected_broker: str | None = None

    status: Literal[
        "ready",
        "ready_with_warnings",
        "failed",
    ]

    total_rows: int = Field(
        default=0,
        ge=0,
    )

    valid_rows: int = Field(
        default=0,
        ge=0,
    )

    invalid_rows: int = Field(
        default=0,
        ge=0,
    )

    preview: list[NormalizedHoldingPreview] = Field(
        default_factory=list,
    )

    warnings: list[ImportWarning] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    message: str


class PortfolioImportConfirmRequest(BaseModel):
    holdings: list[NormalizedHoldingPreview] = Field(
        ...,
        min_length=1,
    )

    duplicate_strategy: Literal[
        "skip",
        "replace",
        "merge",
    ] = "skip"


class PortfolioImportConfirmResponse(BaseModel):
    imported_count: int = Field(
        default=0,
        ge=0,
    )

    skipped_count: int = Field(
        default=0,
        ge=0,
    )

    failed_count: int = Field(
        default=0,
        ge=0,
    )

    imported_symbols: list[str] = Field(
        default_factory=list,
    )

    warnings: list[ImportWarning] = Field(
        default_factory=list,
    )

    message: str