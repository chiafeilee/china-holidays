from bs4 import BeautifulSoup
from selenium import webdriver

HOLIDAY_URL = "https://sousuo.www.gov.cn/sousuo/search.shtml?code=17da70961a7&searchWord={year}节假日&dataTypeId=14"


class WebDriver:
    def __init__(self, options=None):
        self.options = options

    def __enter__(self):
        self.driver = webdriver.Chrome(options=self.options)
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()


class Crawler:
    year: int
    url: str

    def __init__(self, year: int) -> None:
        self.year = year
        self.url = HOLIDAY_URL.format(year=year)

        _options = webdriver.ChromeOptions()
        _options.add_argument("headless")
        self.options = _options

    def get_holiday_link(self, driver: WebDriver):
        driver.get(self.url)
        response = driver.page_source

        soup = BeautifulSoup(response, "html.parser")
        content = soup.find(class_="js_result")

        return content.a["href"]

    def get_holiday_content(self):
        with WebDriver(self.options) as driver:
            link = self.get_holiday_link(driver)
            driver.get(link)
            response = driver.page_source

            soup = BeautifulSoup(response, "html.parser")
            return soup.find_all("p")

    def parse(self):
        return self.get_holiday_content()
