class SentimentService:

    POSITIVE_WORDS = [
        "beat", "beats", "growth", "surge", "rises", "gain", "record",
        "strong", "upgrade", "bullish", "profit", "outperform"
    ]

    NEGATIVE_WORDS = [
        "miss", "misses", "fall", "falls", "drop", "drops", "lawsuit",
        "weak", "downgrade", "bearish", "loss", "warning", "cuts"
    ]

    @staticmethod
    def analyze(text: str):
        text = (text or "").lower()

        positive_score = sum(word in text for word in SentimentService.POSITIVE_WORDS)
        negative_score = sum(word in text for word in SentimentService.NEGATIVE_WORDS)

        if positive_score > negative_score:
            return "positive"

        if negative_score > positive_score:
            return "negative"

        return "neutral"