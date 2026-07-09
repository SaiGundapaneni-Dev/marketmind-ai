class IPOService:

    @staticmethod
    def search_ipo(company_name: str):
        clean_name = company_name.strip().title()

        return {
            "company_name": clean_name,
            "status": "research_required",
            "ipo_available": False,
            "message": (
                f"IPO research workflow initialized for {clean_name}. "
                "Real IPO data integration will be added next."
            ),
            "analysis": {
                "recommendation": "Not enough data",
                "confidence": 0,
                "reasons": [
                    "IPO data source not connected yet",
                    "Financials not available yet",
                    "Valuation not analyzed yet"
                ]
            }
        }