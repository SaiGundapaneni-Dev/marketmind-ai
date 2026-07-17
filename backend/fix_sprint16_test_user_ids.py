from pathlib import Path
import re
import shutil


BACKEND_ROOT = Path(__file__).resolve().parent

TARGETS = [
    BACKEND_ROOT / "tests" / "test_copilot_service.py",
    BACKEND_ROOT / "tests" / "test_portfolio_history_service.py",
    BACKEND_ROOT / "tests" / "test_stock_analysis_service.py",
]


def add_keyword_argument(
    text: str,
    function_name: str,
    keyword: str,
    value: str,
) -> str:
    """
    Add a keyword argument to calls of function_name when that keyword
    is not already present. Handles single-line and multi-line calls.
    """
    pattern = re.compile(
        rf"({re.escape(function_name)}\()"
        rf"(?P<args>.*?)"
        rf"(\))",
        re.DOTALL,
    )

    def replace(match: re.Match[str]) -> str:
        args = match.group("args")

        if re.search(rf"\b{re.escape(keyword)}\s*=", args):
            return match.group(0)

        stripped = args.rstrip()
        trailing = args[len(stripped):]

        if not stripped:
            new_args = f"{keyword}={value}"
        elif "\n" in args:
            # Preserve the existing indentation of the closing call.
            lines = args.splitlines()
            non_empty = [line for line in lines if line.strip()]
            indent = "    "

            if non_empty:
                indent_match = re.match(r"(\s*)", non_empty[-1])
                if indent_match:
                    indent = indent_match.group(1)

            if stripped.endswith(","):
                new_args = f"{stripped}\n{indent}{keyword}={value},{trailing}"
            else:
                new_args = f"{stripped},\n{indent}{keyword}={value},{trailing}"
        else:
            separator = "" if stripped.endswith(",") else ","
            new_args = (
                f"{stripped}{separator} "
                f"{keyword}={value}{trailing}"
            )

        return (
            match.group(1)
            + new_args
            + match.group(3)
        )

    previous = None

    # Apply repeatedly because a file may contain many calls.
    while previous != text:
        previous = text
        text = pattern.sub(replace, text)

    return text


def update_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing test file: {path}")

    backup = path.with_suffix(path.suffix + ".bak")

    if not backup.exists():
        shutil.copy2(path, backup)

    text = path.read_text(encoding="utf-8")

    if path.name == "test_copilot_service.py":
        text = add_keyword_argument(
            text,
            "CopilotService.answer",
            "user_id",
            "1",
        )

    elif path.name == "test_portfolio_history_service.py":
        for function_name in [
            "PortfolioHistoryService.get_performance",
            "PortfolioHistoryService.get_contributors",
            "PortfolioHistoryService.get_changes",
            "PortfolioHistoryService.create_daily_snapshot",
            "PortfolioHistoryService.get_history",
        ]:
            text = add_keyword_argument(
                text,
                function_name,
                "user_id",
                "1",
            )

    elif path.name == "test_stock_analysis_service.py":
        text = add_keyword_argument(
            text,
            "StockAnalysisService.analyze",
            "user_id",
            "1",
        )

    path.write_text(text, encoding="utf-8")
    print(f"Updated: {path}")
    print(f"Backup:  {backup}")


def main() -> None:
    for target in TARGETS:
        update_file(target)

    print("\nDone. Run:")
    print("python -m pytest -v")


if __name__ == "__main__":
    main()
