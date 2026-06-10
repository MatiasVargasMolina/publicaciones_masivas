from infrastructure.mercadolibre.item_client import ItemClient

class ExposureService:

    def __init__(self):
        self.client = ItemClient()

    def get_all(self, site_id: str, token: str):
        return self.client.get_listing_exposures(site_id, token)

    def get_one(self, site_id: str, exposure: str, token: str):
        return self.client.get_listing_exposure_detail(site_id, exposure, token)