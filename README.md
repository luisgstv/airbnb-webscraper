# Airbnb Web Scraper

This project consists of an Airbnb web scraper that allows you to search any location and scrape a custom number of results, which can then be exported to CSV and Excel files.

## Tools and Modules

- This project uses **Selenium** and **BeautifulSoup4** to scrape each page in the Airbnb website.
- The **Pandas** module is used to create the DataFrame for exporting the data to CSV and Excel files.
- The **Time** module is used to measure the time spent scraping all the pages.
- The **Math** module is used to calculate the floor value of half the total number of pages to scrape.

## How it works

When you run the program, you'll need to specify the location and the number of pages you want to scrape in the terminal. The Selenium WebDriver will then open the [Airbnb](https://www.airbnb.com) website and initiate the search once the page is fully loaded. Once it reaches the results page, it will wait for the navigation bar to appear to determine the total number of pages available to search. Based on the number of pages you have chosen to search, it will navigate through each page, ensuring full loading before using BeautifulSoup4 to extract the title, house type, description, price, rating, and URL of each listing. When the scraping process is complete, the data retrieved will be compiled into a Pandas DataFrame and then exported to both CSV and Excel files.

## How to use

To use this project, you will need to follow these steps:

1. Clone this repository using the following command:

```
    git clone https://github.com/luisgstv/airbnb-webscraper.git
```

2. Install the required modules using the following command:

```
    pip install -r requirements.txt
```

3. Once you run the script, enter the place you want to search and specify the number of pages you want to scrape.
