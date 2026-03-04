import requests
from typing import Optional


class AbuseIPDBService:
    """
    Service responsible for querying AbuseIPDB IP reputation.
    """

    BASE_URL = "https://api.abuseipdb.com/api/v2/check"

    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout

    def get_abuse_score(self, ip: str) -> Optional[int]:
        """
        Query AbuseIPDB and return abuse confidence score (0-100)
        """

        headers = {
            "Key": self.api_key,
            "Accept": "application/json"
        }

        params = {
            "ipAddress": ip,
            "maxAgeInDays": 90
        }

        try:
            response = requests.get(
                self.BASE_URL,
                headers=headers,
                params=params,
                timeout=self.timeout
            )

            if response.status_code != 200:
                return None

            data = response.json()

            return (
                data
                .get("data", {})
                .get("abuseConfidenceScore")
            )

        except requests.RequestException:
            return None