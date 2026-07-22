from datetime import date


class ThesisReviewService:

    @staticmethod
    def analyze(thesis, current_price):
        observations = []

        if thesis.target_price:
            if current_price >= thesis.target_price:
                observations.append(
                    "The stock has reached or exceeded your target price."
                )
            elif current_price >= thesis.target_price * 0.9:
                observations.append(
                    "The stock is approaching your target price."
                )

        if thesis.review_date:
            if thesis.review_date <= date.today():
                observations.append(
                    "Your thesis review date has arrived."
                )

        if not observations:
            observations.append(
                "Your investment thesis currently appears unchanged."
            )

        return observations