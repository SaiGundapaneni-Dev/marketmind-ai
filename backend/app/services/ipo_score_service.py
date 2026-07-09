class IPOScoreService:

    @staticmethod
    def calculate_score(ipo: dict):
        score = 0
        reasons = []
        warnings = []

        status = ipo.get("status")
        sector = ipo.get("sector")
        exchange = ipo.get("exchange")
        description = ipo.get("description")

        # IPO status
        if status == "upcoming":
            score += 25
            reasons.append("Company has an upcoming IPO status.")

        elif status == "rumored":
            score += 10
            reasons.append("IPO is currently rumored but not confirmed.")
            warnings.append(
                "IPO plans are not officially confirmed and may change."
            )

        elif status == "listed":
            reasons.append("Company is already publicly listed.")
            warnings.append(
                "This company is no longer an upcoming IPO opportunity."
            )

        # Sector information
        if sector:
            score += 15
            reasons.append("Sector information is available.")
        else:
            warnings.append("Sector information is unavailable.")

        # Exchange information
        if exchange:
            score += 15
            reasons.append("Exchange information is available.")
        else:
            warnings.append(
                "Exchange information has not been confirmed."
            )

        # Company profile
        if description:
            score += 10
            reasons.append("Basic company profile information is available.")
        else:
            warnings.append("Company profile information is missing.")

        # Limit score because financial analysis is not connected yet
        score = min(score, 60)

        if status == "listed":
            rating = "Already Listed"
            recommendation = "Use Stock Research"
            confidence = 100

        elif score >= 50:
            rating = "Research Candidate"
            recommendation = "Research further"
            confidence = 60

        elif score >= 25:
            rating = "Early Stage"
            recommendation = "Monitor"
            confidence = 40

        else:
            rating = "Insufficient Data"
            recommendation = "Not enough data"
            confidence = 20

        warnings.append(
            "Financial statements, IPO pricing, valuation, and risk factors "
            "are not yet included in this analysis."
        )

        return {
            "score": score,
            "rating": rating,
            "recommendation": recommendation,
            "confidence": confidence,
            "reasons": reasons,
            "warnings": warnings,
        }