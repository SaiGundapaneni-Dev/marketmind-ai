from app.services.copilot_service import CopilotService


def test_detect_portfolio_intent():
    question = "Summarize my portfolio"

    intent = CopilotService.detect_intent(question)

    assert intent == "portfolio"


def test_detect_stock_intent():
    question = "Analyze Microsoft stock"

    intent = CopilotService.detect_intent(question)

    assert intent == "stock"


def test_detect_news_intent():
    question = "Show me the latest news about Nvidia"

    intent = CopilotService.detect_intent(question)

    assert intent == "news"


def test_detect_ipo_intent():
    question = "Analyze the IPO for Stripe"

    intent = CopilotService.detect_intent(question)

    assert intent == "ipo"


def test_detect_general_intent():
    question = "What can you help me with?"

    intent = CopilotService.detect_intent(question)

    assert intent == "general"


def test_extract_microsoft_symbol():
    question = "Analyze Microsoft stock"

    symbol = CopilotService.extract_symbol(question)

    assert symbol == "MSFT"


def test_extract_nvidia_symbol():
    question = "Show me the latest news about Nvidia"

    symbol = CopilotService.extract_symbol(question)

    assert symbol == "NVDA"


def test_extract_apple_symbol():
    question = "Analyze Apple stock"

    symbol = CopilotService.extract_symbol(question)

    assert symbol == "AAPL"


def test_extract_tesla_symbol():
    question = "Show me Tesla news"

    symbol = CopilotService.extract_symbol(question)

    assert symbol == "TSLA"


def test_extract_uppercase_ticker():
    question = "Analyze NVDA stock"

    symbol = CopilotService.extract_symbol(question)

    assert symbol == "NVDA"


def test_extract_lowercase_ticker():
    question = "Show news about nvda"

    symbol = CopilotService.extract_symbol(question)

    assert symbol == "NVDA"


def test_ignore_show_as_symbol():
    question = "Show me the latest news about Nvidia"

    symbol = CopilotService.extract_symbol(question)

    assert symbol != "SHOW"


def test_missing_symbol():
    question = "Analyze this stock"

    symbol = CopilotService.extract_symbol(question)

    assert symbol is None


def test_extract_stripe_ipo_company():
    question = "Analyze the IPO for Stripe"

    company_name = CopilotService.extract_ipo_company(question)

    assert company_name == "Stripe"


def test_extract_multiword_ipo_company():
    question = "Research the IPO for Space Exploration Technologies"

    company_name = CopilotService.extract_ipo_company(question)

    assert company_name == "Space Exploration Technologies"