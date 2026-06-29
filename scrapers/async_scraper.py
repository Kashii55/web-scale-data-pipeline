import asyncio
import aiohttp
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from utils.logger import get_logger
import re
import json
import csv
import os
import time

logger = get_logger("AsyncScraper")

RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}

class AsyncScraper(BaseScraper):
    def __init__(self, config_path="config/config.yaml"):
        super().__init__(config_path)
        self.concurrency = self.scraper_config["concurrency"]
        self.semaphore = None
        self.session = None

    async def start(self):
        self.semaphore = asyncio.Semaphore(self.concurrency)
        connector = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(
            connector=connector,
            headers={
                "User-Agent": self.scraper_config["user_agent"],
                "Accept-Encoding": "gzip, deflate",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )
        logger.info(f"Async session started with concurrency={self.concurrency}")

    async def fetch(self, url: str) -> BeautifulSoup:
        async with self.semaphore:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                response.raise_for_status()
                html = await response.text(encoding="utf-8")
                return BeautifulSoup(html, "lxml")

    def clean_price(self, price: str) -> float:
        try:
            return float(re.sub(r'[^\d.]', '', price.strip()))
        except:
            return 0.0

    async def get_book_urls(self, page_url: str) -> list:
        soup = await self.fetch(page_url)
        anchors = soup.select("div.image_container a")
        urls = []
        for a in anchors:
            href = a.get("href", "").replace("../", "")
            full_url = f"https://books.toscrape.com/catalogue/{href.split('catalogue/')[-1]}"
            urls.append(full_url)
        return urls

    async def get_all_book_urls(self) -> list:
        all_urls = []
        page = 1
        while True:
            page_url = self.base_url if page == 1 else f"https://books.toscrape.com/catalogue/page-{page}.html"
            logger.info(f"Scraping page {page}: {page_url}")
            try:
                urls = await self.get_book_urls(page_url)
                if not urls:
                    break
                all_urls.extend(urls)
                logger.info(f"Found {len(urls)} books on page {page}")
                page += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Stopped at page {page}: {e}")
                break
        logger.info(f"Total URLs collected: {len(all_urls)}")
        return all_urls

    async def scrape_book(self, url: str, index: int, total: int) -> dict:
        try:
            soup = await self.fetch(url)

            title = soup.select_one("div.product_main h1")
            title = title.text.strip() if title else "N/A"

            price = soup.select_one('p.price_color')
            price = self.clean_price(price.text) if price else 0.0

            availability = soup.select_one('p.instock.availability')
            availability = " ".join(availability.text.split()) if availability else "N/A"

            image = soup.select_one('#product_gallery .active img')
            image_url = "N/A"
            if image:
                src = image.get("src", "").replace("../../", "")
                image_url = f"https://books.toscrape.com/{src}"

            description = soup.select_one('div#product_description + p')
            description = description.text.strip() if description else "N/A"

            rating_tag = soup.select_one('p.star-rating')
            rating_num = 0
            if rating_tag:
                for cls in rating_tag.get("class", []):
                    if cls in RATING_MAP:
                        rating_num = RATING_MAP[cls]

            product_info = {}
            for row in soup.select("table.table-striped tr"):
                th = row.select_one("th")
                td = row.select_one("td")
                if th and td:
                    key = th.text.strip()
                    val = td.text.strip()
                    if "Price" in key or "Tax" in key:
                        val = self.clean_price(val)
                    product_info[key] = val

            logger.info(f"[{index}/{total}] Scraped: {title}")

            return {
                "title": title,
                "price": price,
                "availability": availability,
                "rating": rating_num,
                "description": description,
                "upc": product_info.get("UPC", "N/A"),
                "product_type": product_info.get("Product Type", "N/A"),
                "price_excl_tax": product_info.get("Price (excl. tax)", 0.0),
                "price_incl_tax": product_info.get("Price (incl. tax)", 0.0),
                "tax": product_info.get("Tax", 0.0),
                "num_reviews": product_info.get("Number of reviews", "0"),
                "image_url": image_url,
                "url": url
            }
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return None

    async def scrape_all(self) -> list:
        await self.start()
        start_time = time.time()

        all_urls = await self.get_all_book_urls()
        total = len(all_urls)

        tasks = [
            self.scrape_book(url, i+1, total)
            for i, url in enumerate(all_urls)
        ]

        results = await asyncio.gather(*tasks)
        books = [r for r in results if r is not None]

        elapsed = time.time() - start_time
        logger.info(f"Scraped {len(books)} books in {elapsed:.2f} seconds")
        return books

    def save_json(self, data: list, filename: str):
        os.makedirs("output", exist_ok=True)
        filepath = f"output/{filename}"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"JSON saved to {filepath}")

    def save_csv(self, data: list, filename: str):
        os.makedirs("output", exist_ok=True)
        filepath = f"output/{filename}"
        if not data:
            return
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"CSV saved to {filepath}")

    async def close(self):
        if self.session:
            await self.session.close()
        logger.info("Async session closed")
