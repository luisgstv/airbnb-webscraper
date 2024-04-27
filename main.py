from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
from math import floor

class Scraper:
    def __init__(self):
        # Creating the ChromeOptions
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('window-size=800,600')
        self.options.add_argument('--lang=en-US')
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
    def run(self):
        self.ask_info()

        start = time.perf_counter()
        self.go_to_scrape_page(self.place, self.page_number)

        # Scraping the pages until it reaches the end
        self.page = 1
        self.data = []
        print(f'Number of pages to scrape = {self.pages}')
        while True:
            print(f'Moving to the page: {self.page}')
            self.scrape()
            if self.page < self.pages:
                self.next_page()
            else:
                break
        
        self.save_data_frame()
        stop = time.perf_counter()
        print(f'Took {stop - start} seconds to scrape.')

    def ask_info(self):
        # Asking information about the search and how many pages will be scraped
        self.place = input('Where do you wanna go? ')
        self.page_number = input('How many pages you wanna scrape? \n(1) The first page\n(2) 50% of the pages\n(3) 100% of the pages\n')
        if self.page_number not in ('1', '2', '3'):
            print('Wrong option. Try again.')
            self.ask_info()

    def go_to_scrape_page(self, place, page_number):
        # Creating the webdriver
        self.driver = webdriver.Chrome(options=self.options)

        # Going to the page and waiting for it to load
        self.driver.get('https://www.airbnb.com')

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="site-content"]//img'))
        )

        # Writing the place in the search field
        self.driver.find_element(By.ID, 'bigsearch-query-location-input').send_keys(place)
        
        # Searching and waiting for the page to load
        self.driver.find_element(By.XPATH, '//button[@data-testid="structured-search-input-search-button"]').click()

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="site-content"]//nav'))
        )

        # Checking if the cookies banner appeared
        if len(self.driver.find_elements(By.XPATH, '//div[@data-testid="main-cookies-banner-container"]')) == 1:
            self.driver.find_elements(By.XPATH, '//div[@data-testid="main-cookies-banner-container"]/section//button')[-1].click()

        # Setting the number of pages to scrape
        if page_number == '1':
            self.pages = 1
        elif page_number == '2':
            self.pages = floor(int(self.driver.find_elements(By.XPATH, '//*[@id="site-content"]//nav//a')[-2].text) * 0.5)
            print(self.pages)
        elif page_number == '3':
            self.pages = int(self.driver.find_elements(By.XPATH, '//*[@id="site-content"]//nav//a')[-2].text)

    def scrape(self):
        # Parsing the page's HTML
        self.soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # Getting the divs with the stays
        self.stays = self.soup.find_all('div', attrs={'itemprop': 'itemListElement'})
        for stay in self.stays:
            # Getting the data
            title = stay.find('div', attrs={'data-testid': 'listing-card-title'})
            *house_type, description, _ = stay.find_all('div', attrs={'data-testid': 'listing-card-subtitle'})
            price = stay.find('div', attrs={'data-testid': 'price-availability-row'})
            rating = price.parent.contents[-1].find('span', attrs={'aria-hidden': 'true'})
            url = stay.find('meta', attrs={'itemprop': 'url'})

            # Cleaning the data
            title = title.text

            house_type = house_type[0].find_all('span')
            if len(house_type) > 1:
                house_type = f'{house_type[0].text.replace('\n', '')} · {house_type[-1].text.replace('\n', '')}'
            else:
                house_type = house_type[0].text.replace('\n', '')

            try: 
                description = description.find('span').text.replace('\n', '')
            except AttributeError:
                description = None

            price = price.find('div', attrs={'aria-hidden': 'true'}).find_all('span')[-2].text

            try:
                rating = rating.text
            except AttributeError:
                rating = 'No ratings'

            url = url['content']

            # Appending the data
            self.data.append([title, house_type, description, price, rating, url])

    def next_page(self):
        # Going to the next page
        self.driver.find_elements(By.XPATH, '//*[@id="site-content"]//nav//a')[-1].click()

        # Waiting for elements to appear two times to avoid errors
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@itemprop="itemListElement"]//img'))
            
        )
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="site-content"]//*[@data-testid="listing-card-title"]'))
        )

        self.page += 1

    def save_data_frame(self):
        # Generating the data frame and saving it in CSV and Excel formats
        data_frame = pd.DataFrame(self.data, columns=['Title', 'Type', 'Description', 'Price', 'Ratings', 'URL'])
        data_frame.to_csv(f'{self.place}.csv', index=False)
        data_frame.to_excel(f'{self.place}.xlsx', index=False)

# Running the application
if __name__ == '__main__':  
    webscraper = Scraper()
    webscraper.run()