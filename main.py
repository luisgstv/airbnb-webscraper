from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time

class Scraper:
    def __init__(self):
        # Creating the ChromeOptions
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('window-size=800,600')
        self.options.add_argument('--lang=en-US')
        self.options.add_argument('--headless')
        self.options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"')
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
    def run(self):
        # Asking information about the search
        self.place = input('Place to search: ')

        start = time.perf_counter()
        self.go_to_scrape_page()

        # Scraping the pages until it reaches the end
        self.page = 1
        self.data = []
        print(f'Number of pages to scrape: {self.pages}')

        while True:
            print(f'Scraping page: {self.page}')
            self.scrape_stays()
            if self.page < self.pages:
                self.next_page()
            else:
                break
        
        self.save_data_frame()
        stop = time.perf_counter()
        print(f'Took {stop - start} seconds to scrape.')

    def go_to_scrape_page(self):
        # Creating the webdriver
        self.driver = webdriver.Chrome(options=self.options)

        # Going to the page and waiting for it to load
        self.driver.get('https://www.airbnb.com')

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div#seo-link-section-tabbed-dense-grid'))
        )

        search_input = self.driver.find_element(By.CSS_SELECTOR, 'input#bigsearch-query-location-input')
        search_input.send_keys(self.place)
        time.sleep(0.5)
        
        # Searching and waiting for the page to load
        search_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-testid="structured-search-input-search-button"]')
        search_button.click()

        total_pages_nav = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div#site-content nav'))
        )

        # Checking if the cookies banner appeared
        if self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="main-cookies-banner-container"]'):
            self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="main-cookies-banner-container"] section button')[-1].click()

        # Getting the number of pages to scrape
        self.pages = int(total_pages_nav.find_elements(By.TAG_NAME, 'a')[-2].text)

    def wait_element(self, n_elements, locator):
        if n_elements == 'one':
            element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(locator)
            )

        elif n_elements == 'all':
            element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located(locator)
            )

        return element

    def get_amenity(self, xpath_selector):
        try:
            amenity = self.driver.find_element(By.XPATH, xpath_selector)
            if 'unavailable' in amenity.get_attribute('id'):
                amenity = False
            else:
                amenity = True
        except Exception:
            amenity = False
        
        return amenity

    def scrape_stays(self):
        stays = self.driver.find_elements(By.CSS_SELECTOR, 'div[itemprop="itemListElement"]')

        for i, stay in enumerate(stays):
            stay.click()
            self.driver.switch_to.window(self.driver.window_handles[-1])

            try:
                WebDriverWait(self.driver, 2.5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="dialog"] button'))
                ).click()
            except TimeoutException:
                pass

            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-section-id="POLICIES_DEFAULT"]'))
                )
                time.sleep(1)
            except Exception:
                print('ERROR')
                with open('html.txt', 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)

            # Stay name
            stay_name = self.wait_element('one', (By.CSS_SELECTOR, 'div[data-section-id="TITLE_DEFAULT"] h1')).text

            # Stay type
            stay_type = self.wait_element('one', (By.CSS_SELECTOR, 'div[data-section-id="OVERVIEW_DEFAULT_V2"] h2')).text
            
            # Number of bedrooms
            try:
                stay_bedrooms = self.wait_element('one', (By.XPATH, '//div[@data-section-id="OVERVIEW_DEFAULT_V2"]//li[contains(text(), "bedroom")]')).text
                stay_bedrooms = stay_bedrooms.replace('·', '').strip().split(' ')[0]
            except Exception:
                stay_bedrooms = None

            # Number of beds
            try:
                stay_beds = self.wait_element('all', (By.XPATH, '//div[@data-section-id="OVERVIEW_DEFAULT_V2"]//li[contains(text(), "bed")]'))[-1].text
                stay_beds = stay_beds.replace('·', '').strip().split(' ')[0]
            except Exception:
                stay_beds = None
            
            # Number of bathrooms
            try:
                stay_bathrooms = self.wait_element('one', (By.XPATH, '//div[@data-section-id="OVERVIEW_DEFAULT_V2"]//li[contains(text(), "bath")]')).text
                stay_bathrooms = stay_bathrooms.replace('·', '').strip().split(' ')[0]
                if not stay_bathrooms.isnumeric():
                    stay_bathrooms = '1'
            except Exception:
                stay_bathrooms = None

            # Stars and comment counts
            try:
                stay_rating = self.wait_element('one', (By.CSS_SELECTOR, 'div[data-section-id="OVERVIEW_DEFAULT_V2"] div[aria-hidden="true"]')).text
                
                stay_reviews_number = None    
            except Exception:
                try:
                    stay_rating = self.wait_element('one', (By.XPATH, '//div[@data-section-id="GUEST_FAVORITE_BANNER"]//span[contains(text(), "Rated")]')).text
                    stay_rating = stay_rating.split(' ')[1]

                    stay_reviews_number = self.wait_element('one', (By.XPATH, '//div[@data-section-id="GUEST_FAVORITE_BANNER"]//span[contains(text(), "review")]')).text
                    stay_reviews_number = stay_reviews_number.split(' ')[0]
                except Exception:
                    stay_rating = 'New'
                    stay_reviews_number = '0'
            
            if not stay_reviews_number:
                try:
                    stay_reviews_number = self.wait_element('one', (By.CSS_SELECTOR, 'div[data-section-id="OVERVIEW_DEFAULT_V2"] a')).text
                    stay_reviews_number = stay_reviews_number.split(' ')[0]
                except Exception:
                    stay_reviews_number = '0'

            # Host information
            host_name = self.wait_element('one', (By.CSS_SELECTOR, 'div[data-section-id="MEET_YOUR_HOST"] h3 span')).text

            try:
                is_superhost = self.wait_element('one', (By.XPATH, '//div[@data-section-id="MEET_YOUR_HOST"]//span[contains(text(), "host")]')).text
                if 'Superhost' in is_superhost:
                    is_superhost = True
                else:
                    is_superhost = False
            except Exception:
                print(self.driver.current_url)
                is_superhost = False

            try:
                host_rating = self.wait_element('one', (By.XPATH, '//div[@data-section-id="MEET_YOUR_HOST"]//span[contains(text(), "rating")]')).text
                host_rating = host_rating.split(' ')[0]

                total_host_reviews = self.wait_element('one', (By.XPATH, '//div[@data-section-id="MEET_YOUR_HOST"]//span[contains(text(), "review")]')).text
                total_host_reviews = total_host_reviews.split(' ')[0]
            except Exception:
                host_rating = 'New'
                total_host_reviews = '0'

            try:
                time_hosting = self.wait_element('one', (By.XPATH, '//div[@data-section-id="MEET_YOUR_HOST"]//span[contains(text(), "hosting")]')).text
            except Exception:
                time_hosting = 'New Host'

            # Price information
            stay_price = self.wait_element('one', (By.XPATH, '//div[@data-section-id="BOOK_IT_SIDEBAR"]//div[@data-testid="book-it-default"]//span[contains(text(), "per")]')).text
            if 'originally' in stay_price:
                stay_price = stay_price.split(' ')[-1]
            else:
                stay_price = stay_price.split(' ')[0]

            # URL
            stay_url = self.driver.current_url

            # Latitude and Longitude
            actions = webdriver.ActionChains(self.driver)
            actions.scroll_to_element(self.driver.find_element(By.XPATH, '//div[@data-section-id="MEET_YOUR_HOST"]')).perform()
            self.driver.execute_script('window.scrollBy(0,-1000);')
            lat, long = self.wait_element('one', (By.CSS_SELECTOR, 'div[data-testid="map/GoogleMap"] a')).get_attribute('href').split('ll=')[-1].split('&')[0].split(',')

            # Amenities
            actions.click(self.driver.find_element(By.CSS_SELECTOR, 'div[data-section-id="AMENITIES_DEFAULT"] button')).perform()
            time.sleep(0.5)

            essentials = self.get_amenity('//div[contains(@id, "_40_")]')
            wifi = self.get_amenity('//div[contains(@id, "_4_")]')
            tv = self.get_amenity('//div[contains(@id, "_1_")]')
            ac = self.get_amenity('//div[contains(@id, "_5_")]')
            heating = self.get_amenity('//div[contains(@id, "_30_")]')
            hot_water = self.get_amenity('//div[contains(@id, "_77_")]')
            washer = self.get_amenity('//div[contains(@id, "_33_")]')
            dryer = self.get_amenity('//div[contains(@id, "_34_")]')
            kitchen = self.get_amenity('//div[contains(@id, "_8_")]')
            paid_parking = self.get_amenity('//div[contains(@id, "_10_")]')
            free_street_parking = self.get_amenity('//div[contains(@id, "_23_")]')
            first_aid_kit = self.get_amenity('//div[contains(@id, "_37_")]')
            fire_extinguisher = self.get_amenity('//div[contains(@id, "_39_")]')
            smoke_alarm = self.get_amenity('//div[contains(@id, "_35_")]')
            carbon_monoxide_alarm = self.get_amenity('//div[contains(@id, "_36_")]')
            security_camera = self.get_amenity('//div[contains(@id, "_9999_")]')
            patio_or_balcony = self.get_amenity('//div[contains(@id, "_100_")]')
            bbq_grill = self.get_amenity('//div[contains(@id, "_99_")]')
            shared_pool = self.get_amenity('//div[contains(@id, "_7_")]')
            beach_access = self.get_amenity('//div[contains(@id, "_674_")]')
            pets_allowed = self.get_amenity('//div[contains(@id, "_12_")]')

            # Appending data
            self.data.append([
                stay_name,
                stay_type,
                stay_bedrooms, 
                stay_beds, 
                stay_bathrooms,
                stay_rating,
                stay_reviews_number,
                host_name,
                is_superhost,
                host_rating,
                total_host_reviews,
                time_hosting,
                essentials,
                wifi,
                tv,
                ac,
                heating,
                hot_water,
                washer,
                dryer,
                kitchen,
                paid_parking,
                free_street_parking,
                first_aid_kit,
                fire_extinguisher,
                smoke_alarm,
                carbon_monoxide_alarm,
                security_camera,
                patio_or_balcony,
                bbq_grill,
                shared_pool,
                beach_access,
                pets_allowed,
                stay_price,
                stay_url,
                lat,
                long
            ])

            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            print(f'Scraped stay {i + 1} from page {self.page}')
            time.sleep(1.5)

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
        data_frame = pd.DataFrame(self.data, columns=[
            'Stay Name',
            'Stay Type',
            'Num Bedrooms',
            'Num Beds',
            'Num Bathrooms',
            'Stay Rating',
            'Num Stay Reviews',
            'Host Name',
            'Superhost',
            'Host Rating',
            'Num Host Reviews',
            'Time Hosting',
            'Essentials',
            'Wifi',
            'TV',
            'AC',
            'Heating',
            'Hot Water',
            'Washer',
            'Dryer',
            'Kitchen',
            'Paid Parking',
            'Free Street Parking',
            'First Aid Kit',
            'Fire Extinguisher',
            'Smoke Alarm',
            'Carbon Monoxide Alarm',
            'Security Camera',
            'Patio or Balcony',
            'BBQ Grill',
            'Shared Pool',
            'Beach Access',
            'Pets Allowed',
            'Stay Price',
            'Stay URL',
            'Latitude',
            'Longitude'
        ])
        data_frame.to_csv(f'{self.place}.csv', index=False)

# Running the application
if __name__ == '__main__':  
    webscraper = Scraper()
    webscraper.run()