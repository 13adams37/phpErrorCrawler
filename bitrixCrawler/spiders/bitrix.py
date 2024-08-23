from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from w3lib.url import url_query_cleaner
from bs4 import BeautifulSoup


def process_links(links):
    # print('crawler links = ', links)
    for link in links:
        link.url = url_query_cleaner(link.url)  # remove  queries
        yield link

def has_php_error(php_error, error_list) -> bool:
    if php_error not in error_list:
        return True
    else:
        return False
    

def trim_php_error(php_error):
    return php_error.split("#0: ")[0]


def fetch_php_error(html_body):
    soup = BeautifulSoup(html_body, "html.parser")
    
    try:
        return soup.find("pre").contents[0]
    except AttributeError:
        return 'HTTP ERROR 500'


def get_referer(response):
    try:
        return response.request.headers.get("Referer", None).decode("utf-8")
    except AttributeError:  # if no referer
        return "None"


class BitrixCrawler(CrawlSpider):
    name = "bitrix"
    allowed_domains = []
    start_urls = []
    test_url = ""
    rules = (
        Rule(
            LinkExtractor(
                deny=[":443", ":80"],  # remove links with protocols
            ),
            callback="parse_item",
            follow=True,
            process_links=process_links,
        ),
    )
    urls_with_errors = []
    php_error_list = []
    error_count = 0

    def parse_start_url(self, response):  # костыль scrapy какой-то
        self.parse_item(response)  # process first request

    def parse_item(self, response):
        text_error = ""
        
        if(len(response.body) <= 1000 and (response.status >=200 and response.status <= 299)):     
            print('LOW RESPONSE SIZE')
            self.error_count = self.error_count + 1

            self.urls_with_errors.append(
                {
                    "id": self.error_count,
                    "url": response.url,
                    "status_code": response.status,
                    "text_error": f"LOW RESPONSE SIZE = {len(response.body)}",
                    "referer": get_referer(response),
                },
            )

        if response.status >= 500:
            text_error = trim_php_error(fetch_php_error(response.text))

        elif response.status >= 400:
            text_error = response.status

        if response.status != 200:
            if response.status >= 500 and not has_php_error(text_error, self.php_error_list):
                return
            else:
                self.php_error_list.append(text_error)
            
            self.error_count = self.error_count + 1

            self.urls_with_errors.append(
                {
                    "id": self.error_count,
                    "url": response.url,
                    "status_code": response.status,
                    "text_error": text_error,
                    "referer": get_referer(response),
                },
            )

            return {
                "url": response.url,
                "status_code": response.status,
                "text_error": text_error,
                "referer": get_referer(response),
            }  # to log

    def closed(self, reason):
        print("bitrixCrawler was closed by -", reason)
        print("urls with err", self.urls_with_errors)

