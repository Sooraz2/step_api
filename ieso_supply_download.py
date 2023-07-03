# pandas library
import pandas as pd

# selenium library
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# add attributes for visual output
options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1200")

# install chrome driver with attributes
driver = webdriver.Chrome(executable_path='chromedriver', options=options)


# run web page and download table as csv
def download_supply_by_year(year):
    url = "http://reports.ieso.ca/public/GenOutputbyFuelHourly/PUB_GenOutputbyFuelHourly_{}.xml".format(year)
    driver.get(url)

    # create csv file using table element
    div_element = driver.find_element(By.CLASS_NAME, 'report')
    table_element = div_element.find_element(By.TAG_NAME, 'table')
    df = pd.read_html(table_element.get_attribute('outerHTML'))[0]
    df.to_csv('ieso_supply_{}.csv'.format(year), index=False, header=False)


# download supply datasets one by one
download_supply_by_year(2015)

# close browser
driver.quit()
