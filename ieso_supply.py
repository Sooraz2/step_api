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


# run web page and extract supplies
def get_hourly_supply():
    driver.get("https://www.ieso.ca/power-data/this-hours-data")
    supply_driver = driver.find_element(By.CSS_SELECTOR, "a[href='#supply']")
    supply_driver.click()
    supplies_by_type = driver.find_elements(By.CLASS_NAME, "ieso-data-hour")
    supplies_by_type = supplies_by_type[12:20]
    important_supplies_by_type = dict()

    # hourly supplies outputs
    for supply_by_type in supplies_by_type:
        supply_key = supply_by_type.text.split("\n")[0]
        supply_value = int(supply_by_type.text.split("\n")[2].replace(" ", "").replace("MW", "").replace(",", ""))
        important_supplies_by_type[supply_key] = supply_value
    return important_supplies_by_type

print(get_hourly_supply())

# close browser
driver.quit()
