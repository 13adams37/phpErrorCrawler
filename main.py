import argparse
import bitrixCrawler.settings as CrawlerSettings
from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess
from bitrixCrawler.spiders.bitrix import BitrixCrawler
from scrapy.settings import Settings
from src.after_crawler import AfterCrawlerMethods


def get_allowed_domain(url):
    return [urlparse(url).netloc]


def main(
    allowed_domains=["citrus-test.ru", "citrus-web.ru"],
    start_urls=["https://citrus-soft.ru/"],
):
    print(allowed_domains, start_urls)
    settings = Settings()
    settings.setmodule(CrawlerSettings, priority="default")

    process = CrawlerProcess(settings=settings)
    process.crawl(
        BitrixCrawler,
        allowed_domains=allowed_domains,
        start_urls=start_urls,
    )

    process.start()  # the script will block here until the crawling is finished

    # run -> python -m scrapy crawl bitrix --logfile bitrix.log -o bitrix.json:json

    if len(BitrixCrawler.urls_with_errors) > 0:
        after_crawler = AfterCrawlerMethods()
        after_crawler.run(BitrixCrawler.urls_with_errors, allowed_domains[0])
    else:
        print("Ошибок не обнаружено (но это не точно)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Автотест ошибок PHP")
    parser.add_argument("url", help="Адрес ресурса формата https://citrus-soft.ru/")
    args = parser.parse_args()
    url_scheme = urlparse(args.url).scheme
    if url_scheme == "http" or url_scheme == "https":
        main(get_allowed_domain(args.url), [args.url])
    else:
        print("Введите правильный URL")
