from unittest.mock import patch

from app.services.copilot_service import CopilotService


SAMPLE_PORTFOLIO = {
    "summary": {
        "total_cost": 1000.0,
        "total_value": 1250.0,
        "total_profit": 250.0,
        "total_return_percent": 25.0,
        "holdings_count": 4,
        "priced_holdings_count": 4,
        "unpriced_holdings_count": 0,
    },
    "allocation": {
        "by_asset_type": [
            {
                "asset_type": "US",
                "value": 1250.0,
                "allocation_percent": 100.0,
            }
        ],
        "largest_holding": {
            "symbol": "AAPL",
            "name": "Apple",
            "current_value": 400.0,
            "allocation_percent": 32.0,
        },
    },
    "concentration_risk": {
        "risk_level": "medium",
        "largest_position_percent": 32.0,
        "top_three_percent": 72.0,
        "concentrated_positions": [
            {
                "symbol": "AAPL",
                "name": "Apple",
                "allocation_percent": 32.0,
            }
        ],
        "message": "Moderate concentration risk.",
    },
    "performance_insights": {
        "top_performer": {
            "symbol": "NVDA",
            "name": "NVIDIA",
            "profit": 180.0,
            "profit_percent": 60.0,
        },
        "weakest_performer": {
            "symbol": "MSFT",
            "name": "Microsoft",
            "profit": -40.0,
            "profit_percent": -8.0,
        },
        "largest_profit_contributor": {
            "symbol": "NVDA",
            "name": "NVIDIA",
            "profit": 180.0,
            "profit_percent": 60.0,
        },
        "largest_loss_contributor": {
            "symbol": "MSFT",
            "name": "Microsoft",
            "profit": -40.0,
            "profit_percent": -8.0,
        },
        "profitable_holdings_count": 3,
        "losing_holdings_count": 1,
        "breakeven_holdings_count": 0,
        "message": "3 profitable and 1 losing.",
    },
    "health_score": {
        "score": 72.5,
        "rating": "good",
        "components": {
            "diversification_score": 15.0,
            "concentration_score": 15.0,
            "profitability_score": 17.5,
            "pricing_coverage_score": 25.0,
        },
        "message": "Good portfolio health.",
    },
    "actionable_insights": {
        "count": 1,
        "items": [],
        "disclaimer": "Informational only.",
    },
    "holdings": [],
}

SAMPLE_INTELLIGENCE = {
    "portfolio_status": "fair",
    "executive_summary": (
        "Your portfolio contains 4 holdings and is "
        "valued at $1,250.00."
    ),
    "priority_insights": [
        {
            "priority": 1,
            "category": "concentration",
            "severity": "high",
            "title": "High concentration risk",
            "message": (
                "The top three holdings represent 72.00% "
                "of portfolio value."
            ),
            "evidence": [
                "Largest position: 32.00%",
            ],
            "suggested_action": (
                "Review whether your largest positions "
                "still match your risk tolerance."
            ),
            "affected_symbols": ["AAPL"],
        }
    ],
    "strengths": [],
    "risks": [],
    "opportunities": [],
    "holdings_to_watch": [
        {
            "symbol": "AAPL",
            "name": "Apple",
            "allocation_percent": 32.0,
            "profit": 100.0,
            "profit_percent": 25.0,
            "reason": "Large portfolio allocation",
        }
    ],
    "recent_changes": [
        "Portfolio value increased by $50.00."
    ],
    "recommended_questions": [],
    "disclaimer": "Informational only.",
}



def test_detect_portfolio_intent():
    assert CopilotService.detect_intent("Summarize my portfolio") == "portfolio"


def test_detect_stock_intent():
    assert CopilotService.detect_intent("Analyze Microsoft stock") == "stock"


def test_detect_news_intent():
    assert CopilotService.detect_intent(
        "Show me the latest news about Nvidia"
    ) == "news"


def test_detect_ipo_intent():
    assert CopilotService.detect_intent("Analyze the IPO for Stripe") == "ipo"


def test_detect_general_intent():
    assert CopilotService.detect_intent("What can you help me with?") == "general"


def test_extract_microsoft_symbol():
    assert CopilotService.extract_symbol("Analyze Microsoft stock") == "MSFT"


def test_extract_nvidia_symbol():
    assert (
        CopilotService.extract_symbol("Show me the latest news about Nvidia")
        == "NVDA"
    )


def test_extract_apple_symbol():
    assert CopilotService.extract_symbol("Analyze Apple stock") == "AAPL"


def test_extract_tesla_symbol():
    assert CopilotService.extract_symbol("Show me Tesla news") == "TSLA"


def test_extract_uppercase_ticker():
    assert CopilotService.extract_symbol("Analyze NVDA stock") == "NVDA"


def test_extract_lowercase_ticker():
    assert CopilotService.extract_symbol("Show news about nvda") == "NVDA"


def test_ignore_show_as_symbol():
    assert (
        CopilotService.extract_symbol("Show me the latest news about Nvidia")
        != "SHOW"
    )


def test_missing_symbol():
    assert CopilotService.extract_symbol("Analyze this stock") is None


def test_extract_stripe_ipo_company():
    assert (
        CopilotService.extract_ipo_company("Analyze the IPO for Stripe")
        == "Stripe"
    )


def test_extract_multiword_ipo_company():
    assert (
        CopilotService.extract_ipo_company(
            "Research the IPO for Space Exploration Technologies"
        )
        == "Space Exploration Technologies"
    )


def test_portfolio_question_type_summary():
    assert (
        CopilotService.detect_portfolio_question_type("Analyze my portfolio")
        == "summary"
    )


def test_portfolio_question_type_strengths():
    assert (
        CopilotService.detect_portfolio_question_type(
            "What are the strengths of my portfolio?"
        )
        == "strengths"
    )


def test_portfolio_question_type_risks():
    assert (
        CopilotService.detect_portfolio_question_type(
            "What is my biggest portfolio risk?"
        )
        == "risks"
    )


def test_portfolio_question_type_recommendations():
    assert (
        CopilotService.detect_portfolio_question_type(
            "How can I improve my portfolio?"
        )
        == "recommendations"
    )


def test_portfolio_question_type_diversification():
    assert (
        CopilotService.detect_portfolio_question_type(
            "Is my portfolio diversified?"
        )
        == "diversification"
    )


def test_portfolio_question_type_health():
    assert (
        CopilotService.detect_portfolio_question_type(
            "Is my portfolio healthy?"
        )
        == "health"
    )


@patch(
    "app.services.copilot_service.PortfolioService.calculate",
    return_value=SAMPLE_PORTFOLIO,
)
def test_answer_portfolio_summary(mock_calculate):
    response = CopilotService.answer(
        "Analyze my portfolio",
        db=None,
        user_id=1,
    )

    assert response["intent"] == "portfolio"
    assert response["portfolio_question_type"] == "summary"
    assert response["status"] == "success"
    assert response["answer"]
    assert "portfolio contains 4 holdings" in response["answer"].lower()
    mock_calculate.assert_called_once_with(
        None,
        1,
    )


@patch(
    "app.services.copilot_service.PortfolioService.calculate",
    return_value=SAMPLE_PORTFOLIO,
)
def test_answer_portfolio_strengths(mock_calculate):
    response = CopilotService.answer(
        "What are the strengths of my portfolio?",
        db=None,
        user_id=1,
    )

    assert response["portfolio_question_type"] == "strengths"
    assert response["answer"].startswith(
        "The main strengths of your portfolio are:"
    )


@patch(
    "app.services.copilot_service.PortfolioService.calculate",
    return_value=SAMPLE_PORTFOLIO,
)
def test_answer_portfolio_risks(mock_calculate):
    response = CopilotService.answer(
        "What is my biggest portfolio risk?",
        db=None,
        user_id=1,
    )

    assert response["portfolio_question_type"] == "risks"
    assert response["answer"].startswith(
        "The main risks in your portfolio are:"
    )
    assert "-$40.00" in response["answer"]


@patch(
    "app.services.copilot_service.PortfolioService.calculate",
    return_value=SAMPLE_PORTFOLIO,
)
def test_answer_portfolio_recommendations(mock_calculate):
    response = CopilotService.answer(
        "How can I improve my portfolio?",
        db=None,
        user_id=1,
    )

    assert response["portfolio_question_type"] == "recommendations"
    assert response["answer"].startswith(
        "Here are the main areas to improve:"
    )


@patch(
    "app.services.copilot_service.PortfolioService.calculate",
    return_value=SAMPLE_PORTFOLIO,
)
def test_answer_portfolio_diversification(mock_calculate):
    response = CopilotService.answer(
        "Is my portfolio diversified?",
        db=None,
        user_id=1,
    )

    assert response["portfolio_question_type"] == "diversification"
    assert response["answer"] is not None
    assert "diversification score" in response["answer"].lower()


@patch(
    "app.services.copilot_service.PortfolioService.calculate",
    return_value=SAMPLE_PORTFOLIO,
)
def test_answer_portfolio_health(mock_calculate):
    response = CopilotService.answer(
        "Is my portfolio healthy?",
        db=None,
        user_id=1,
    )

    assert response["portfolio_question_type"] == "health"
    assert response["answer"] is not None
    assert "health score" in response["answer"].lower()


def test_empty_question():
    response = CopilotService.answer(
        "   ",
        db=None,
        user_id=1,
    )
    assert response["intent"] == "general"
    assert response["status"] == "needs_more_info"


def test_portfolio_question_type_focus():
    assert (
        CopilotService.detect_portfolio_question_type(
            "What should I focus on today?"
        )
        == "focus"
    )


def test_portfolio_question_type_holdings_to_watch():
    assert (
        CopilotService.detect_portfolio_question_type(
            "Which holding deserves attention?"
        )
        == "holdings_to_watch"
    )


def test_portfolio_question_type_changes():
    assert (
        CopilotService.detect_portfolio_question_type(
            "What changed since yesterday?"
        )
        == "changes"
    )


@patch(
    "app.services.copilot_service."
    "PortfolioIntelligenceService.generate",
    return_value=SAMPLE_INTELLIGENCE,
)
def test_answer_daily_focus(
    mock_generate,
):
    response = CopilotService.answer(
        "What should I focus on today?",
        db=None,
        user_id=1,
    )

    assert response["intent"] == "portfolio"
    assert (
        response["portfolio_question_type"]
        == "focus"
    )
    assert response["status"] == "success"
    assert "highest-priority" in response[
        "answer"
    ].lower()

    mock_generate.assert_called_once_with(
        None,
        1,
    )


@patch(
    "app.services.copilot_service."
    "PortfolioIntelligenceService.generate",
    return_value=SAMPLE_INTELLIGENCE,
)
def test_answer_holdings_to_watch(
    mock_generate,
):
    response = CopilotService.answer(
        "Which holding deserves attention?",
        db=None,
        user_id=1,
    )

    assert (
        response["portfolio_question_type"]
        == "holdings_to_watch"
    )
    assert "AAPL" in response["answer"]

    mock_generate.assert_called_once_with(
        None,
        1,
    )


@patch(
    "app.services.copilot_service."
    "PortfolioIntelligenceService.generate",
    return_value=SAMPLE_INTELLIGENCE,
)
def test_answer_recent_changes(
    mock_generate,
):
    response = CopilotService.answer(
        "What changed since yesterday?",
        db=None,
        user_id=1,
    )

    assert (
        response["portfolio_question_type"]
        == "changes"
    )
    assert "$50.00" in response["answer"]

    mock_generate.assert_called_once_with(
        None,
        1,
    )
