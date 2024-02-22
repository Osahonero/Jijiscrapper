import scrapy
import json

class CarpriceSpider(scrapy.Spider):
    name = "jijispider"
    allowed_domains = ["jiji.ng"]
    start_urls = ["https://jiji.ng/cars?filter_attr_100_condition=Nigerian%20Used"]
    api_url_template = "https://jiji.ng/api_web/v1/listing?filter_attr_100_condition=Nigerian+Used&slug=cars&webp=true&lsmid=1708566396989&page={page}"
    page_number = 1

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "method": "GET",
        "Referer": "https://jiji.ng/cars?filter_attr_100_condition=Nigerian%20Used",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    }

    def start_requests(self):
        yield scrapy.Request(url=self.api_url_template.format(page=self.page_number), headers=self.headers)

    def parse(self, response):
        data = json.loads(response.text)
        adverts = data.get('adverts_list', {}).get('adverts', [])
        
        for advert in adverts:
            attrs = {attr['name']: attr['value'] for attr in advert.get('attrs', [])}
            yield {
                'title': advert.get('title'),
                'price': advert.get('price_obj', {}).get('view'),
                'condition': attrs.get('Condition'),
                'transmission': attrs.get('Transmission'),
                'details': advert.get('details'),
                'region': advert.get('region'),
            }

        # Check if adverts are empty to stop pagination
        if not adverts:
            self.logger.info(f"No more adverts found at page {self.page_number}. Stopping...")
            return

        # Continue to the next page if adverts are present
        self.page_number += 1
        next_page = self.api_url_template.format(page=self.page_number)
        yield scrapy.Request(url=next_page, callback=self.parse, headers=self.headers)


