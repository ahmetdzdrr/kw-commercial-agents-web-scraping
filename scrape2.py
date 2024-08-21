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
    """
    A class to scrape detailed agent information from URLs provided in a CSV file.

    Attributes:
        driver_path (str): Path to the ChromeDriver executable.
        csv_file (str): Path to the CSV file containing agent URLs.
        service (Service): WebDriver service for Chrome.
        options (Options): Options for the Chrome WebDriver.
        driver (webdriver.Chrome): WebDriver instance for Chrome.
        agent_details (list): List to store scraped agent details.

    Methods:
        start(): Starts the scraping process by iterating over URLs in the CSV file.
        _process_url(url): Scrapes the details from a single agent's profile page.
        _save_to_csv(): Saves the scraped agent details to a CSV file.
    """
    
    def __init__(self, driver_path, csv_file):
        """
        Initializes the AgentScraper with the path to the ChromeDriver and the CSV file containing URLs.

        Args:
            driver_path (str): Path to the ChromeDriver executable.
            csv_file (str): Path to the CSV file containing agent URLs.
        """
        self.service = Service(driver_path)
        self.options = Options()
        self.options.add_argument("--start-maximized")  # Start Chrome maximized
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.csv_file = csv_file
        self.agent_details = []

    def start(self):
        """
        Starts the scraping process by reading URLs from the CSV file and processing each one.

        Iterates over the URLs, processes each, and then quits the WebDriver.
        """
        df = pd.read_csv(self.csv_file)  # Read the CSV file containing agent URLs
        for index, row in df.iterrows():
            url = row['URL']
            self._process_url(url)  # Process each URL to scrape agent details
            time.sleep(15)  # Sleep to avoid overwhelming the server

        self.driver.quit()  # Close the WebDriver after processing all URLs
        self._save_to_csv()  # Save the scraped data to a CSV file

    def _process_url(self, url):
        """
        Opens the agent profile URL in a new tab, scrapes the details, and closes the tab.

        Args:
            url (str): The URL of the agent's profile page to be scraped.
        """
        # Open the URL in a new tab
        self.driver.execute_script("window.open(arguments[0], '_blank');", url)
        self.driver.switch_to.window(self.driver.window_handles[-1])

        try:
            # Wait for the agent contact details to be present on the page
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.agent-contact'))
            )
            time.sleep(10)  # Extra wait to ensure the page is fully loaded

            # Parse the page source with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Extract the position, contact, and other details
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

                # Get text or default to 'N/A' if not found
                title_text = title.get_text(strip=True) if title else 'N/A'
                street_text = street.get_text(strip=True) if street else 'N/A'
                address_text = address.get_text(strip=True) if address else 'N/A'
                phone_text = phone.get_text(strip=True) if phone else 'N/A'
                licence_text = licence.get_text(strip=True) if licence else 'N/A'

                # Store the scraped data in a dictionary
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

                self.agent_details.append(agent_detail)  # Add the details to the list

                # Print the scraped details for verification
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
            # Close the current tab and switch back to the first tab
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def _save_to_csv(self):
        """
        Saves the scraped agent details to a CSV file named 'agent_details.csv'.
        """
        details_df = pd.DataFrame(self.agent_details)  # Create DataFrame from the list of agent details
        details_df.to_csv('agent_details.csv', index=False)  # Save DataFrame to a CSV file
        print("Agent details saved to 'agent_details.csv'")

if __name__ == "__main__":
    driver_path = 'path/to/your/chromedriver'  # Update with your ChromeDriver path
    csv_file = 'agent_data.csv'  # CSV file containing agent URLs
    scraper = AgentScraper(driver_path, csv_file)  # Create an instance of the scraper
    scraper.start()  # Start the scraping process
