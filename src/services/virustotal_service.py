import requests
from typing import Optional


class VirusTotalService:
    """
    Service responsible for querying VirusTotal IP reputation.
    """

    BASE_URL = "https://www.virustotal.com/api/v3/ip_addresses"

    def __init__(self, api_key: str, timeout: int = 10):
        """
        :param api_key: VirusTotal API key
        :param timeout: request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout

    def get_malicious_count(self, ip: str) -> Optional[int]:
        """
        Query VirusTotal for an IP address and return the number of
        engines that marked it as malicious.

        :param ip: IP address as string
        :return: malicious count or None if unavailable
        """

        url = f"{self.BASE_URL}/{ip}"
        headers = {
            "x-apikey": self.api_key
        }

        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)

            if response.status_code != 200:
                return None

            data = response.json()

            return (
                data
                .get("data", {})
                .get("attributes", {})
                .get("last_analysis_stats", {})
                .get("malicious")
            )

        except requests.RequestException:
            # Network error, timeout, etc.
            return None
