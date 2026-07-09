import logging
import requests

logger = logging.getLogger("marketmind")


class SECService:

    SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

    HEADERS = {
        "User-Agent": "MarketMindAI contact@example.com"
    }

    @staticmethod
    def search_company(company_name: str):
        try:
            search_term = company_name.strip().lower()

            response = requests.get(
                SECService.SEC_TICKERS_URL,
                headers=SECService.HEADERS,
                timeout=10
            )

            response.raise_for_status()

            companies = response.json()
            matches = []

            for item in companies.values():
                title = item.get("title", "")
                ticker = item.get("ticker", "")
                cik = item.get("cik_str")

                if search_term in title.lower() or search_term in ticker.lower():
                    matches.append({
                        "company_name": title,
                        "ticker": ticker,
                        "cik": str(cik).zfill(10),
                    })

            return {
                "query": company_name,
                "count": len(matches),
                "matches": matches[:10],
            }

        except Exception:
            logger.exception("SEC company search failed for: %s", company_name)

            return {
                "query": company_name,
                "count": 0,
                "matches": [],
                "error": "Unable to search SEC company data.",
            }