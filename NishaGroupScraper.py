from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from Utils import calc_distance

base_url = "https://www.nisha.co.il/"
search_url = "Search?NicheID=1&catID=2,23&GeoAreas=2,4,9"

class NishaGroupScraper:
    def __init__(self):
        # Specifying incognito mode as you launch your browser[OPTIONAL]
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option('excludeSwitches', ["enable-automation", "load-extension"])
        chrome_options.add_argument("--incognito")

        # Create new Instance of Chrome in incognito mode using webdriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(f'{base_url}{search_url}')

    def __del__(self):
        self.driver.close()

    def get_jobs_in_page(self, page_num, jobs_collection):
        page_addr = f'{base_url}{search_url}&PageNum={page_num}'
        # self.driver.get(page_addr)
        jobs_collection.append(page_addr)

    def get_jobs(self):
        pagination_nav = self.driver.find_element(By.CSS_SELECTOR, 'nav.pagination')
        last_page = pagination_nav.find_elements(By.CSS_SELECTOR, 'a')[-1]
        last_page_href = last_page.get_attribute("href")
        last_page_number = int(last_page_href[(last_page_href.rfind('=') + 1):len(last_page_href)])

        jobs_collection = list()

        for i in range(1, last_page_number + 1):
            self.get_jobs_in_page(i, jobs_collection)

        print(jobs_collection)


n = NishaGroupScraper()
n.get_jobs()

