from app.data.ipo_data import SAMPLE_IPOS


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
                    "recommendation": "Not enough data",
                    "confidence": 0,
                    "reasons": [
                        "Company was not found in the current IPO dataset",
                        "Live IPO data source is not connected yet"
                    ]
                }
            }

        is_available = matched_ipo["status"] in ["upcoming", "rumored"]

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
            "analysis": {
                "recommendation": "Research further",
                "confidence": 40,
                "reasons": [
                    "Basic IPO profile is available",
                    "Financial statements are not connected yet",
                    "Valuation analysis is not connected yet"
                ]
            }
        }