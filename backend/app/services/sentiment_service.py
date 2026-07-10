import re


class SentimentService:

    POSITIVE_WORDS = {
        "beat": 2,
        "beats": 2,
        "growth": 1,
        "surge": 2,
        "surges": 2,
        "rise": 1,
        "rises": 1,
        "gain": 1,
        "gains": 1,
        "record": 1,
        "strong": 1,
        "upgrade": 2,
        "upgraded": 2,
        "bullish": 2,
        "profit": 1,
        "profits": 1,
        "outperform": 2,
        "rally": 2,
        "rallies": 2,
        "rebound": 1,
        "recovery": 1,
        "expansion": 1,
        "partnership": 1,
        "deal": 1,
        "approval": 2,
    }

    NEGATIVE_WORDS = {
        "miss": 2,
        "misses": 2,
        "fall": 1,
        "falls": 1,
        "drop": 1,
        "drops": 1,
        "lawsuit": 2,
        "weak": 1,
        "downgrade": 2,
        "downgraded": 2,
        "bearish": 2,
        "loss": 1,
        "losses": 1,
        "warning": 2,
        "cuts": 1,
        "cut": 1,
        "decline": 1,
        "declines": 1,
        "plunge": 2,
        "plunges": 2,
        "risk": 1,
        "concern": 1,
        "concerns": 1,
        "investigation": 2,
        "recall": 2,
    }

    @staticmethod
    def analyze(text: str):
        cleaned_text = (text or "").lower()

        words = re.findall(r"\b[a-z]+\b", cleaned_text)

        positive_score = sum(
            SentimentService.POSITIVE_WORDS.get(word, 0)
            for word in words
        )

        negative_score = sum(
            SentimentService.NEGATIVE_WORDS.get(word, 0)
            for word in words
        )

        total_score = positive_score + negative_score

        if total_score == 0:
            return {
                "label": "neutral",
                "confidence": 0.50,
                "reason": "No strong positive or negative financial signals were detected.",
            }

        if positive_score > negative_score:
            confidence = positive_score / total_score

            return {
                "label": "positive",
                "confidence": round(confidence, 2),
                "reason": "Positive financial or market signals were stronger than negative signals.",
            }

        if negative_score > positive_score:
            confidence = negative_score / total_score

            return {
                "label": "negative",
                "confidence": round(confidence, 2),
                "reason": "Negative financial or market signals were stronger than positive signals.",
            }

        return {
            "label": "neutral",
            "confidence": 0.50,
            "reason": "Positive and negative financial signals were balanced.",
        }