from __future__ import annotations

from pathlib import Path
import shutil
import tokenize
from io import StringIO


ROOT = Path(__file__).resolve().parent

TARGETS = {
    ROOT / "tests" / "test_copilot_service.py": {
        "CopilotService.answer",
    },
    ROOT / "tests" / "test_portfolio_history_service.py": {
        "PortfolioHistoryService.get_performance",
        "PortfolioHistoryService.get_contributors",
        "PortfolioHistoryService.get_changes",
        "PortfolioHistoryService.create_daily_snapshot",
        "PortfolioHistoryService.get_history",
    },
    ROOT / "tests" / "test_stock_analysis_service.py": {
        "StockAnalysisService.analyze",
    },
}


def line_offsets(text: str) -> list[int]:
    offsets = [0]
    total = 0

    for line in text.splitlines(keepends=True):
        total += len(line)
        offsets.append(total)

    return offsets


def absolute_offset(
    offsets: list[int],
    position: tuple[int, int],
) -> int:
    line, column = position
    return offsets[line - 1] + column


def restore_backup(path: Path) -> None:
    backup = path.with_suffix(path.suffix + ".bak")

    if backup.exists():
        shutil.copy2(backup, path)
        print(f"Restored backup: {path.name}")
    else:
        print(
            f"No backup found for {path.name}; "
            "using the current file."
        )


def add_user_id_to_calls(
    text: str,
    target_names: set[str],
) -> str:
    tokens = list(
        tokenize.generate_tokens(
            StringIO(text).readline
        )
    )
    offsets = line_offsets(text)
    insertions: list[tuple[int, str]] = []

    index = 0

    while index < len(tokens):
        token = tokens[index]

        if token.type != tokenize.NAME:
            index += 1
            continue

        parts = [token.string]
        cursor = index + 1

        while (
            cursor + 1 < len(tokens)
            and tokens[cursor].string == "."
            and tokens[cursor + 1].type == tokenize.NAME
        ):
            parts.append(tokens[cursor + 1].string)
            cursor += 2

        qualified_name = ".".join(parts)

        if (
            qualified_name not in target_names
            or cursor >= len(tokens)
            or tokens[cursor].string != "("
        ):
            index += 1
            continue

        open_index = cursor
        depth = 0
        close_index = None

        for scan in range(open_index, len(tokens)):
            current = tokens[scan]

            if current.string == "(":
                depth += 1
            elif current.string == ")":
                depth -= 1

                if depth == 0:
                    close_index = scan
                    break

        if close_index is None:
            raise RuntimeError(
                f"Could not find closing parenthesis for "
                f"{qualified_name}"
            )

        open_offset = absolute_offset(
            offsets,
            tokens[open_index].end,
        )
        close_offset = absolute_offset(
            offsets,
            tokens[close_index].start,
        )
        arguments = text[open_offset:close_offset]

        if "user_id" not in arguments:
            stripped = arguments.rstrip()

            if not stripped:
                insertion = "user_id=1"
            elif "\n" in arguments:
                close_line = tokens[close_index].start[0]
                close_line_start = offsets[close_line - 1]
                close_column = tokens[close_index].start[1]
                indent = text[
                    close_line_start:
                    close_line_start + close_column
                ]

                if stripped.endswith(","):
                    insertion = (
                        f"\n{indent}user_id=1,"
                    )
                else:
                    insertion = (
                        f",\n{indent}user_id=1,"
                    )
            else:
                if stripped.endswith(","):
                    insertion = " user_id=1"
                else:
                    insertion = ", user_id=1"

            insertions.append(
                (close_offset, insertion)
            )

        index = close_index + 1

    for position, insertion in sorted(
        insertions,
        reverse=True,
    ):
        text = (
            text[:position]
            + insertion
            + text[position:]
        )

    return text


def main() -> None:
    for path, target_names in TARGETS.items():
        if not path.exists():
            raise FileNotFoundError(
                f"Missing test file: {path}"
            )

        restore_backup(path)

        source = path.read_text(
            encoding="utf-8"
        )
        updated = add_user_id_to_calls(
            source,
            target_names,
        )
        path.write_text(
            updated,
            encoding="utf-8",
        )

        print(f"Updated safely: {path.name}")

    print("\nRun these checks:")
    print(
        "python -m py_compile "
        "tests/test_copilot_service.py "
        "tests/test_portfolio_history_service.py "
        "tests/test_stock_analysis_service.py"
    )
    print("python -m pytest -v")


if __name__ == "__main__":
    main()
