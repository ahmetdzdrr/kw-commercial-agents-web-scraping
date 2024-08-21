import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

class AgentScraper:
    def __init__(self, driver_path, csv_file):
        self.service = Service(driver_path)
        self.options = Options()
        self.options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.csv_file = csv_file
        self.agent_details = []

    def start(self):
        df = pd.read_csv(self.csv_file)
        for index, row in df.iterrows():
            url = row['URL']
            self._process_url(url)
            time.sleep(15)

        self.driver.quit()
        self._save_to_csv()

    def _process_url(self, url):
        self.driver.execute_script("window.open(arguments[0], '_blank');", url)
        self.driver.switch_to.window(self.driver.window_handles[-1])

        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.agent-contact'))
            )
            time.sleep(10)

            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            position_div = soup.find('div', class_='col-xs-5').find('div', class_='agent-title')
            if position_div:
                position_text = position_div.text

            contact_div = soup.find('div', class_='agent-contact col-sm-3 col-xs-12')
            if contact_div:
                title = contact_div.find('h5', class_='company-name mb-0 font-bold')
                street = contact_div.find('div', class_='agent-address-street')
                address = contact_div.find('div', class_='agent-address-city-state mb-5')
                phone = contact_div.find('div', class_='contact_phone')
                licence = contact_div.find('div', class_='agent-license')

                email_tag = soup.find('div').find('a', class_='email fill-text')
                email_text = email_tag.text

                title_text = title.get_text(strip=True) if title else 'N/A'
                street_text = street.get_text(strip=True) if street else 'N/A'
                address_text = address.get_text(strip=True) if address else 'N/A'
                phone_text = phone.get_text(strip=True) if phone else 'N/A'
                licence_text = licence.get_text(strip=True)

                agent_detail = {
                    'URL': url,
                    'Title': title_text,
                    'Position': position_text,
                    'Street': street_text,
                    'Address': address_text,
                    'Phone': phone_text,
                    'Email': email_text,
                    'License': licence_text
                }

                self.agent_details.append(agent_detail)

                print(f"URL: {url}")
                print(f"Title: {title_text}")
                print(f"Position: {position_text}")
                print(f"Street: {street_text}")
                print(f"Address: {address_text}")
                print(f"Phone: {phone_text}")
                print(f"Email: {email_text}")
                print(f"Licence: {licence_text}")
                print("="*40)

            else:
                print(f"No contact div found for URL: {url}")

        except Exception as e:
            print(f"Failed to process URL: {url}. Error: {e}")

        finally:
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def _save_to_csv(self):
        details_df = pd.DataFrame(self.agent_details)
        details_df.to_csv('agent_details.csv', index=False)
        print("Agent details saved to 'agent_details.csv'")

if __name__ == "__main__":
    driver_path = 'path/to/your/chromedriver'
    csv_file = 'agent_data.csv'
    scraper = AgentScraper(driver_path, csv_file)
    scraper.start()








