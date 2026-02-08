import requests
from typing import Optional, Tuple


class IPQSASNScoreService:
    """
    Minimal IPQualityScore service.
    Returns only ASN and fraud score for a given IP.
    """

    BASE_URL = "https://ipqualityscore.com/api/json/ip"

    def __init__(self, api_key: str, timeout: int = 10):
        """
        :param api_key: IPQualityScore API key
        :param timeout: request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout

    def lookup(self, ip: str) -> Optional[Tuple[int, int]]:
        """
        Query IPQualityScore and return (asn, fraud_score).

        :param ip: IP address as string
        :return: (asn, fraud_score) or None if unavailable
        """

        url = f"{self.BASE_URL}/{self.api_key}/{ip}"

        try:
            response = requests.get(url, timeout=self.timeout)

            if response.status_code != 200:
                return None

            data = response.json()

            if not data.get("success", False):
                return None

            asn = data.get("ASN")
            fraud_score = data.get("fraud_score")

            if asn is None or fraud_score is None:
                return None

            return asn, fraud_score

        except requests.RequestException:
            return None
