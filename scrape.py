from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd

class AgentScraper:
    """
    A class to scrape commercial real estate agent data from the KW Commercial website.

    Attributes:
        driver_path (str): Path to the ChromeDriver executable.
        url (str): URL of the website to be scraped.
        service (Service): WebDriver service for Chrome.
        driver (webdriver.Chrome): WebDriver instance for Chrome.
        agent_data (list): List to store scraped agent data.

    Methods:
        start(): Starts the scraping process.
        _switch_to_iframe(): Switches the WebDriver context to the appropriate iframe.
        _scrape_data(): Scrapes the agent data from the webpage.
        _create_dataframe(): Creates a DataFrame from the scraped data and saves it to a CSV file.
    """
    
    def __init__(self, driver_path, url):
        """
        Initializes the AgentScraper with the path to the ChromeDriver and the target URL.

        Args:
            driver_path (str): Path to the ChromeDriver executable.
            url (str): URL of the website to be scraped.
        """
        self.service = Service(driver_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.url = url
        self.agent_data = []

    def start(self):
        """
        Starts the scraping process by navigating to the target URL, switching to the iframe,
        scraping the data, quitting the WebDriver, and saving the data to a CSV file.
        """
        self.driver.get(self.url)  # Navigate to the target URL
        self._switch_to_iframe()   # Switch to the iframe containing the agent data
        self._scrape_data()        # Start scraping the agent data
        self.driver.quit()         # Close the WebDriver after scraping is complete
        self._create_dataframe()   # Save the scraped data to a CSV file

    def _switch_to_iframe(self):
        """
        Switches the WebDriver context to the iframe that contains the agent listings.

        Raises:
            Exception: If the iframe is not found within the specified timeout.
        """
        try:
            # Wait for the iframe to be present and switch to it
            iframe = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'realnex.com')]"))
            )
            self.driver.switch_to.frame(iframe)
        except Exception as e:
            print("Failed to locate iframe.")
            self.driver.quit()
            raise e

    def _scrape_data(self):
        """
        Scrapes the agent data from the webpage by iterating through the listings,
        extracting the relevant information, and handling pagination.

        Raises:
            Exception: If there is an error during data extraction or if the "Load More" button is not found.
        """
        base_url = "https://mpdirect.realnex.com/AgentProfile/?agentID={}"
        
        while True:
            time.sleep(5)  # Wait for the page to fully load
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find the main listings section that contains the agents
            main_listings_section = soup.find('section', class_='main-listings')
            if main_listings_section:
                list_container_div = main_listings_section.find('div', class_='list-container')
                if list_container_div:
                    # Find all agent entries on the page
                    agents = list_container_div.find_all('div', class_='agent_list_div list-item agent-item')
                    for agent in agents:
                        data_id = agent.get('data-id')  # Extract the agent's data ID
                        if data_id:
                            try:
                                # Extract the agent's name and URL
                                name_tag = (agent.find('div', class_='flex-row agent-item--info-name mb-3')
                                            .find('div', class_='flex-col agent-item--info-name--name-title')
                                            .find('h3', class_='m-0').find('a'))
                                if name_tag:
                                    name_text = name_tag.get_text(strip=True)
                                    url = base_url.format(data_id)
                                    self.agent_data.append({"Name": name_text, "URL": url})  # Append the data to the list
                                else:
                                    print(f"Name tag not found for data-id: {data_id}")
                            except Exception as e:
                                print(f"Error extracting name and URL for data-id: {data_id}. Exception: {e}")

            try:
                # Attempt to click the "Load More" button to load more agent entries
                load_more_button = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "load-more-agents"))
                )
                load_more_button.click()
                time.sleep(5)  # Wait for the new data to load
            except Exception as e:
                print("No more Load More button found or all data is loaded.")
                break  # Exit the loop if there are no more pages to load

    def _create_dataframe(self):
        """
        Creates a pandas DataFrame from the scraped agent data and saves it as a CSV file.

        The resulting file is named 'agent_data.csv'.
        """
        df = pd.DataFrame(self.agent_data)  # Create DataFrame from the list of agent data
        df.to_csv('agent_data.csv', index=False)  # Save DataFrame to a CSV file
        print("Data saved to 'agent_data.csv'")

if __name__ == "__main__":
    driver_path = 'path/to/your/chromedriver'  # Path to the ChromeDriver executable
    url = "https://kwcommercial.com/agents/"  # URL of the KW Commercial agents page
    scraper = AgentScraper(driver_path, url)  # Create an instance of the AgentScraper
    scraper.start()  # Start the scraping process
