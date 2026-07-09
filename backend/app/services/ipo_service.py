from app.data.ipo_data import SAMPLE_IPOS
from app.services.ipo_score_service import IPOScoreService


class IPOService:

    @staticmethod
    def search_ipo(company_name: str):
        search_term = company_name.strip().lower()

        matched_ipo = None

        for ipo in SAMPLE_IPOS:
            if search_term in ipo["company_name"].lower():
                matched_ipo = ipo
                break

        if matched_ipo is None:
            return {
                "company_name": company_name.strip().title(),
                "status": "not_found",
                "ipo_available": False,
                "message": "No IPO information found in the current data source.",
                "analysis": {
                    "score": 0,
                    "rating": "Insufficient Data",
                    "recommendation": "Not enough data",
                    "confidence": 0,
                    "reasons": [
                        "Company was not found in the current IPO dataset.",
                        "Live IPO data source is not connected yet.",
                    ],
                    "warnings": [
                        "This result is based only on the current sample IPO dataset.",
                    ],
                },
            }

        is_available = matched_ipo["status"] in ["upcoming", "rumored"]

        analysis = IPOScoreService.calculate_score(matched_ipo)

        return {
            "company_name": matched_ipo["company_name"],
            "symbol": matched_ipo["symbol"],
            "status": matched_ipo["status"],
            "sector": matched_ipo["sector"],
            "exchange": matched_ipo["exchange"],
            "ipo_year": matched_ipo["ipo_year"],
            "description": matched_ipo["description"],
            "ipo_available": is_available,
            "message": f"IPO information found for {matched_ipo['company_name']}.",
            "analysis": analysis,
        }