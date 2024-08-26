# Airbnb Web Scraper

This project is an Airbnb web scraper that allows you to search any location and scrape essential data from each result, exporting it to a CSV file. This creates a comprehensive dataset, which can be used for further analysis and predictions. The scraped data includes information such as:

- Number of bedrooms, beds and bathrooms of the stay;
- The rating of the stay;
- Information about the host of the stay;
- The availability of 21 amenities;
- The price of the stay;
- The URL of the stay;
- Latitude and Longitude of the stay.

## Tools and Modules

- This project uses **Selenium** to scrape each page in the Airbnb website.
- The **Pandas** module is used to create the DataFrame for exporting the data to CSV and Excel files.
- The **Time** module is used to measure the time spent scraping all the pages.

## How it works

When you run the program, you'll need to specify the location you want to scrape in the terminal. The Selenium WebDriver will then open the [Airbnb](https://www.airbnb.com) website and initiate the search once the page is fully loaded. Upon reaching the results page, it will wait for the navigation bar to appear to determine the total number of available pages. The scraper will then navigate through each page, opening individual results and waiting for all relevant data to be retrieved, while handling potential exceptions for missing information. After the scraping process is complete, the data will be compiled into a Pandas DataFrame and exported as a CSV file.

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

3. Once you run the script, enter the place you want to search and wait the data to be scraped (Something between 40 to 50 minutes).
