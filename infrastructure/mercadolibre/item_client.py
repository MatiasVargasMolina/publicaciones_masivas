import requests

class ItemClient:

    BASE_URL = "https://api.mercadolibre.com"

    def get_listing_exposures(self, site_id: str, access_token: str):
        url = f"{self.BASE_URL}/sites/{site_id}/listing_exposures"

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Error getting exposures: {response.text}")

        return response.json()

    def get_listing_exposure_detail(self, site_id: str, exposure: str, access_token: str):
        url = f"{self.BASE_URL}/sites/{site_id}/listing_exposures/{exposure}"

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Error getting exposure detail: {response.text}")

        return response.json()