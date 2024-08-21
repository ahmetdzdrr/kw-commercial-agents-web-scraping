from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd

class AgentScraper:
    def __init__(self, driver_path, url):
        self.service = Service(driver_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.url = url
        self.agent_data = []

    def start(self):
        self.driver.get(self.url)
        self._switch_to_iframe()
        self._scrape_data()
        self.driver.quit()
        self._create_dataframe()

    def _switch_to_iframe(self):
        try:
            iframe = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'realnex.com')]"))
            )
            self.driver.switch_to.frame(iframe)
        except Exception as e:
            print("Failed to locate iframe.")
            self.driver.quit()
            raise e

    def _scrape_data(self):
        base_url = "https://mpdirect.realnex.com/AgentProfile/?agentID={}"
        while True:
            time.sleep(5)
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            main_listings_section = soup.find('section', class_='main-listings')
            if main_listings_section:
                list_container_div = main_listings_section.find('div', class_='list-container')
                if list_container_div:
                    agents = list_container_div.find_all('div', class_='agent_list_div list-item agent-item')
                    for agent in agents:
                        data_id = agent.get('data-id')
                        if data_id:
                            try:
                                name_tag = (agent.find('div', class_='flex-row agent-item--info-name mb-3')
                                            .find('div', class_='flex-col agent-item--info-name--name-title')
                                            .find('h3', class_='m-0').find('a'))
                                if name_tag:
                                    name_text = name_tag.get_text(strip=True)
                                    url = base_url.format(data_id)
                                    self.agent_data.append({"Name": name_text, "URL": url})
                                else:
                                    print(f"Name tag not found for data-id: {data_id}")
                            except Exception as e:
                                print(f"Error extracting name and URL for data-id: {data_id}. Exception: {e}")

            try:
                load_more_button = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "load-more-agents"))
                )
                load_more_button.click()
                time.sleep(5)
            except Exception as e:
                print("No more Load More button found or all data is loaded.")
                break

    def _create_dataframe(self):
        df = pd.DataFrame(self.agent_data)
        df.to_csv('agent_data.csv', index=False)
        print("Data saved to 'agent_data.csv'")

if __name__ == "__main__":
    driver_path = 'chromedriver'
    url = "https://kwcommercial.com/agents/"
    scraper = AgentScraper(driver_path, url)
    scraper.start()