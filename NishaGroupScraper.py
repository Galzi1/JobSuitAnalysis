from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import pandas as pd

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

        self.pages_collection = list()
        self.jobs_collection = list()

    def __del__(self):
        self.driver.close()

    def get_jobs_pages(self, page_num):
        page_addr = f'{base_url}{search_url}&PageNum={page_num}'
        # self.driver.get(page_addr)
        self.pages_collection.append(page_addr)

    def get_jobs_in_page(self, page_url):
        self.driver.get(page_url)
        # jobs_table = self.driver.find_element(By.CSS_SELECTOR, 'table')
        jobs_table = WebDriverWait(self.driver, 10).until(ec.visibility_of_element_located(
            (By.CSS_SELECTOR, 'table')))
        jobs_titles = jobs_table.find_elements(By.CSS_SELECTOR, 'tr.jobtr')
        jobs_titles = [item for item in jobs_titles if item.find_elements(By.CSS_SELECTOR, 'td.jobtds')]
        jobs_elements = jobs_table.find_elements(By.CSS_SELECTOR, 'tr.trdetails')

        assert len(jobs_titles) == len(jobs_elements)

        for i in range(0, len(jobs_titles)):
            job = {}
            job_title = jobs_titles[i]
            job_element = jobs_elements[i]
            job["area"] = job_title.find_elements(By.CSS_SELECTOR, 'td.jobtds')[1].text
            box_top_element = job_element.find_element(By.CSS_SELECTOR, 'section.box-top')
            job["title"] = box_top_element.find_element(By.CSS_SELECTOR, 'p.right > a').get_attribute("text")
            job["id"] = box_top_element.find_element(By.CSS_SELECTOR, 'p.left > a').get_attribute("text").strip(' \t\n\r')
            job_cols = job_element.find_elements(By.CSS_SELECTOR, 'section.cols > section.col')
            job_fields = job_cols[0].find_elements(By.XPATH, './h5 | ./p | ./div')

            for j in range(0, len(job_fields)):
                if job_fields[j].tag_name == 'h5':
                    if 'תיאור' in job_fields[j].get_attribute('textContent'):
                        k = j + 1
                        desc = []
                        while k < len(job_fields) and job_fields[k].tag_name != 'h5':
                            job_description_element = job_fields[k]
                            if job_description_element.tag_name == 'p':
                                desc.append(job_description_element.get_attribute("textContent"))
                            elif job_description_element.tag_name == 'div':
                                desc.append(job_description_element.text)
                                # if not job_description_element.find_elements(By.CSS_SELECTOR, 'p'):
                                #     print("hi")
                                # desc.append(job_description_element.find_element(By.CSS_SELECTOR, 'p')
                                #             .get_attribute("textContent"))
                            k += 1

                        job["description"] = "" if len(desc) == 0 else ' '.join(desc)
                    elif 'דרישות' in job_fields[j].get_attribute('textContent'):
                        k = j + 1
                        req = []
                        while k < len(job_fields) and job_fields[k].tag_name != 'h5':
                            job_requirements_element = job_fields[k]
                            if job_requirements_element.tag_name == 'p':
                                req.append(job_requirements_element.get_attribute("textContent"))
                            elif job_requirements_element.tag_name == 'div':
                                req.append(job_requirements_element.text)
                            k += 1

                        job["requirements"] = "" if len(req) == 0 else ' '.join(req)

            self.jobs_collection.append(job)

    def get_jobs(self):
        pagination_nav = self.driver.find_element(By.CSS_SELECTOR, 'nav.pagination')
        last_page = pagination_nav.find_elements(By.CSS_SELECTOR, 'a')[-1]
        last_page_href = last_page.get_attribute("href")
        last_page_number = int(last_page_href[(last_page_href.rfind('=') + 1):len(last_page_href)])

        for i in range(1, last_page_number + 1):
            self.get_jobs_pages(i)

        for page in self.pages_collection:
            self.get_jobs_in_page(page)

        jobs_df = pd.DataFrame(self.jobs_collection)
        jobs_df.to_csv("jobs.csv")


n = NishaGroupScraper()
n.get_jobs()

