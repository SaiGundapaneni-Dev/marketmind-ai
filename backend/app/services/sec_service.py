import logging

import requests


logger = logging.getLogger("marketmind")


class SECService:

    SEC_TICKERS_URL = (
        "https://www.sec.gov/files/company_tickers.json"
    )

    SEC_SUBMISSIONS_URL = (
        "https://data.sec.gov/submissions"
    )

    HEADERS = {
        "User-Agent": "MarketMindAI contact@example.com",
        "Accept-Encoding": "gzip, deflate",
        "Host": "data.sec.gov",
    }

    SEARCH_HEADERS = {
        "User-Agent": "MarketMindAI contact@example.com",
        "Accept-Encoding": "gzip, deflate",
    }

    @staticmethod
    def search_company(company_name: str):
        try:
            search_term = company_name.strip().lower()

            response = requests.get(
                SECService.SEC_TICKERS_URL,
                headers=SECService.SEARCH_HEADERS,
                timeout=10,
            )

            response.raise_for_status()

            companies = response.json()

            matches = []

            for item in companies.values():
                title = item.get("title", "")
                ticker = item.get("ticker", "")
                cik = item.get("cik_str")

                title_match = search_term in title.lower()
                ticker_match = search_term == ticker.lower()

                if title_match or ticker_match:
                    matches.append(
                        {
                            "company_name": title,
                            "ticker": ticker,
                            "cik": str(cik).zfill(10),
                        }
                    )

            return {
                "query": company_name,
                "count": len(matches),
                "matches": matches[:10],
            }

        except requests.RequestException:
            logger.exception(
                "SEC company search request failed for: %s",
                company_name,
            )

            return {
                "query": company_name,
                "count": 0,
                "matches": [],
                "error": "Unable to connect to SEC company data.",
            }

        except Exception:
            logger.exception(
                "Unexpected SEC company search error for: %s",
                company_name,
            )

            return {
                "query": company_name,
                "count": 0,
                "matches": [],
                "error": "Unable to process SEC company data.",
            }

    @staticmethod
    def get_company_filings(cik: str):
        try:
            clean_cik = str(cik).strip()

            if not clean_cik.isdigit():
                return {
                    "cik": clean_cik,
                    "count": 0,
                    "filings": [],
                    "error": "CIK must contain numbers only.",
                }

            padded_cik = clean_cik.zfill(10)

            url = (
                f"{SECService.SEC_SUBMISSIONS_URL}/"
                f"CIK{padded_cik}.json"
            )

            response = requests.get(
                url,
                headers=SECService.HEADERS,
                timeout=10,
            )

            response.raise_for_status()

            company_data = response.json()

            recent = (
                company_data
                .get("filings", {})
                .get("recent", {})
            )

            forms = recent.get("form", [])
            accession_numbers = recent.get(
                "accessionNumber",
                [],
            )
            filing_dates = recent.get(
                "filingDate",
                [],
            )
            report_dates = recent.get(
                "reportDate",
                [],
            )
            primary_documents = recent.get(
                "primaryDocument",
                [],
            )
            descriptions = recent.get(
                "primaryDocDescription",
                [],
            )

            filings = []

            for index, form in enumerate(forms):

                accession_number = (
                    accession_numbers[index]
                    if index < len(accession_numbers)
                    else None
                )

                filing_date = (
                    filing_dates[index]
                    if index < len(filing_dates)
                    else None
                )

                report_date = (
                    report_dates[index]
                    if index < len(report_dates)
                    else None
                )

                primary_document = (
                    primary_documents[index]
                    if index < len(primary_documents)
                    else None
                )

                description = (
                    descriptions[index]
                    if index < len(descriptions)
                    else None
                )

                filings.append(
                    {
                        "form": form,
                        "accession_number": accession_number,
                        "filing_date": filing_date,
                        "report_date": report_date,
                        "primary_document": primary_document,
                        "description": description,
                    }
                )

            return {
                "company_name": company_data.get("name"),
                "cik": padded_cik,
                "sic": company_data.get("sic"),
                "sic_description": company_data.get(
                    "sicDescription"
                ),
                "state_of_incorporation": company_data.get(
                    "stateOfIncorporation"
                ),
                "fiscal_year_end": company_data.get(
                    "fiscalYearEnd"
                ),
                "count": len(filings),
                "filings": filings[:50],
            }

        except requests.HTTPError as error:
            logger.exception(
                "SEC filings HTTP error for CIK: %s",
                cik,
            )

            status_code = (
                error.response.status_code
                if error.response is not None
                else None
            )

            if status_code == 404:
                return {
                    "cik": str(cik),
                    "count": 0,
                    "filings": [],
                    "error": "No SEC company submission found for this CIK.",
                }

            return {
                "cik": str(cik),
                "count": 0,
                "filings": [],
                "error": "Unable to fetch SEC filings.",
            }

        except requests.RequestException:
            logger.exception(
                "SEC filings request failed for CIK: %s",
                cik,
            )

            return {
                "cik": str(cik),
                "count": 0,
                "filings": [],
                "error": "Unable to connect to SEC filing data.",
            }

        except Exception:
            logger.exception(
                "Unexpected SEC filings error for CIK: %s",
                cik,
            )

            return {
                "cik": str(cik),
                "count": 0,
                "filings": [],
                "error": "Unable to process SEC filing data.",
            }