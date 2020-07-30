from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

import re
import time


class amazonBot(object):
    """Parses relevant information from a text file consisting of
    Amazon links."""

    def __init__(self, item):
        """Setup navigation to Amazon base URL"""

        self.amazon_url = "https://www.amazon.com/"
        self.item = item
        '''
        # Chrome
        chromeDriver = "chromedriver"
        self.driver = webdriver.Chrome(chromeDriver)
        '''
        # Firefox
        self.profile = webdriver.FirefoxProfile()
        self.options = Options()
        # self.options.add_argument("--headless")
        self.driver = webdriver.Firefox(firefox_profile=self.profile,
                                        options=self.options)

        # Navigate to the Amazon URL.
        self.driver.get(self.amazon_url)

        # Obtain the source
        self.html = self.driver.page_source
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.html = self.soup.prettify('utf-8')

    def search_items(self):
        """Searches through the list of items obtained from spreadsheet and
        obtains name, price, and URL information for each item."""

        product_dict = {}

        print(f"Searching for {self.item}...")

        self.driver.get(self.amazon_url)

        # Access search bar in amazon
        search_input = self.driver.find_element_by_id("twotabsearchtextbox")
        search_input.send_keys(self.item)
        time.sleep(2)

        # Access enter button next to search bar
        '''
        search_button = self.driver.find_element_by_xpath(
            "//*[@id='nav-search']/form/div[2]/div/input")
        search_button.click()
        '''
        search_button = self.driver.find_element_by_id(
            "nav-search").find_element_by_class_name("nav-search-submit")
        search_button.click()

        # Access four star and up button to select the best products
        print("Searching 4-star & up products..")
        time.sleep(2)
        fourPlus_star_button = self.driver.find_element_by_id(
            "reviewsRefinements").find_element_by_tag_name("i")
        fourPlus_star_button.click()

        # Check to see up to how many items could be on the page
        print("Retrieving product information")
        time.sleep(2)
        results_section = self.driver.find_element_by_css_selector(
            "div.s-main-slot")
        num_of_results = len(results_section.find_elements_by_xpath("div"))

        # Retrieve first product on the page
        asin = ""
        counter = 0

        # Filter to products that only have data-asin attribute
        while counter < num_of_results:
            product = self.driver.find_element_by_css_selector(
                f"div.s-main-slot > div[data-index='{counter}']")
            asin = product.get_attribute("data-asin")

            if asin is not None and asin is not "":
                url = "https://www.amazon.com/dp/" + asin

                name = self.get_product_name(product)
                price = self.get_product_price(product)
                stars = self.get_product_stars(product)
                num_ratings = self.get_product_num_ratings(product)
                img = self.get_product_image(product)

                product_dict[asin] = {"Name": name, "Price": price,
                                      "Stars": stars, "NumReviews": num_ratings, "Image": img, "URL": url}

            counter = counter + 1

        return product_dict

    def get_product_name(self, product):
        """Returns the product name of the Amazon URL."""

        try:
            product_name = product.find_element_by_tag_name(
                "h2").find_element_by_tag_name("span").text
        except NoSuchElementException:
            product_name = "Not available"

        if product_name is None or product_name is "":
            product_name = "Not available"

        return product_name

    def get_product_price(self, product):
        """Returns the product price of the product."""

        try:
            price = product.find_element_by_css_selector(
                ".a-offscreen").get_attribute("innerHTML")
        except NoSuchElementException:
            price = "Not available"

        if price is None or price is "":
            price = "Not available"

        return price

    def get_product_num_ratings(self, product):
        """Returns the produc ratings"""

        try:
            number_of_ratings = product.find_element_by_css_selector(
                ".a-link-normal span.a-size-base").get_attribute("innerHTML")
        except NoSuchElementException:
            number_of_ratings = "Not available"

        if (number_of_ratings == "Not available"):
            try:
                number_of_ratings = product.find_element_by_xpath(
                    "//div/span/div/div/div/div/div[4]/div/span[2]/a/span").text
            except NoSuchElementException:
                number_of_ratings = "Not available"

        if (number_of_ratings == "Not available"):
            try:
                number_of_ratings = product.find_element_by_xpath(
                    "//div/span/div/div/divdiv[5]//span[2]/a/span").text
            except NoSuchElementException:
                number_of_ratings = "Not available"

        if number_of_ratings is None:
            number_of_ratings = "Not available"

        return number_of_ratings

    def get_product_stars(self, product):
        """Returns the produc ratings"""

        try:
            product_stars = product.find_element_by_css_selector(
                "i.a-icon-star-small span.a-icon-alt").get_attribute("innerHTML")
        except NoSuchElementException:
            product_stars = "Not available"

        if product_stars is None or product_stars is "":
            product_stars = "Not available"

        return product_stars

    def get_product_image(self, product):
        """ Returns the image related to the Amazon item. """

        try:
            imgTag = product.find_element_by_css_selector(
                "span[data-component-type='s-product-image']").find_element_by_tag_name("img")
            img = imgTag.get_attribute("src")
        except NoSuchElementException:
            img = "Not available"

        if img is None or img is "":
            img = "Not available"

        return img

    def close_session(self):
        """Close the browser session."""
        self.driver.close()
