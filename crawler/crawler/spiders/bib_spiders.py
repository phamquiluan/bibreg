import os
import scrapy
import json


class BibsSpider(scrapy.Spider):
    name = "bibs"

    def start_requests(self):
        urls = [
            "https://activstore.vn/dlut-2022-album-7-45-amp-70km-a10253.html",
            "https://activstore.vn/dlut-2022-album-6-45-amp-70km-a10252.html",
            "https://activstore.vn/dlut-2022-album-5-45-amp-70km-a10251.html",
            "https://activstore.vn/dlut-2022-album-4-45-amp-70km-a10231.html",
            "https://activstore.vn/dlut-2022-album-3-21km-a10220.html",
            "https://activstore.vn/dlut-2022-album-2-21km-a10203.html",
            "https://activstore.vn/dlut-2022-album-1-21km-a10202.html",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        file_name = os.path.splitext(os.path.basename(response.url))[0]
        image_urls = [i.split("\"")[1] for i in response.css("img").getall()]
        dlut_image_urls = [url for url in image_urls if "album" in url and "dlu" in url]

        with open(f"{file_name}.json", "w") as ref:
            json.dump(dlut_image_urls, ref, indent=2, sort_keys=True)
