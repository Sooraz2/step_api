# selenium library
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pymysql

# datetime library
from datetime import datetime, timedelta

# add attributes for visual output
options = Options()
options.add_argument("--headless")
#options.add_argument("--window-size=1920,1200")

# install chrome driver with attributes
driver = webdriver.Chrome(executable_path='chromedriver', options=options)


# run web page and extract demands
def get_hourly_demand():
    driver.get("https://www.ieso.ca/power-data/this-hours-data")
    demand_with_info = driver.find_element(By.ID, "demand")
    demands = demand_with_info.find_elements(By.CLASS_NAME, "ieso-data-group")

    # hourly demands outputs
    ontario_demand = int(demands[0].text.split("\n")[2].replace(" MW", "").replace(",", ""))
    market_demand = int(demands[1].text.split("\n")[2].replace(" MW", "").replace(",", ""))
    return {'Ontario Demand': ontario_demand, 'Market Demand': market_demand}


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


# run web page and extract prices
def get_hourly_price():
    driver.get("https://www.ieso.ca/power-data/this-hours-data")
    price_driver = driver.find_element(By.CSS_SELECTOR, "a[href='#price']")
    price_driver.click()
    prices_by_type = driver.find_elements(By.CLASS_NAME, "ieso-data-hour")
    price_by_type = prices_by_type[20:21][0]

    # hourly price output
    price_value = float(price_by_type.text.split("\n")[2].replace(" ", "").replace("MWh", "").replace("/", "").replace("$", ""))
    return {'HOEP': price_value}


# extract all three features at once
def get_hourly_data():

    # join three data hourly
    data = get_hourly_demand() | get_hourly_supply() | get_hourly_price()

    # get important features data only
    important_features = ['Market Demand', 'Ontario Demand', 'Nuclear', 'Hydro', 'Wind', 'Gas', 'Solar', 'Biofuel', 'HOEP']
    data = {key: data[key] for key in important_features}

    # calculate total supply
    data['Total Supply'] = 0
    if data['Nuclear'] is not None:
        data['Total Supply'] += data['Nuclear']
    if data['Hydro'] is not None:
        data['Total Supply'] += data['Hydro']
    if data['Wind'] is not None:
        data['Total Supply'] += data['Wind']
    if data['Gas'] is not None:
        data['Total Supply'] += data['Gas']
    if data['Solar'] is not None:
        data['Total Supply'] += data['Solar']
    if data['Biofuel'] is not None:
        data['Total Supply'] += data['Biofuel']

    # renaming features with units
    renamed_features = {
        'Market Demand': 'Market Demand (MW)',
        'Ontario Demand': 'Ontario Demand (MW)',
        'Nuclear': 'Nuclear Supply (MW)',
        'Hydro': 'Hydro Supply (MW)',
        'Wind': 'Wind Supply (MW)',
        'Gas': 'Gas Supply (MW)',
        'Solar': 'Solar Supply (MW)',
        'Biofuel': 'Biofuel Supply (MW)',
        'Total Supply': 'Total Supply (MW)',
        'HOEP': 'HOEP ($/MWh)'
    }
    data = {value: data[key] for key, value in renamed_features.items()}

    # record time of data
    current_datetime = datetime.now()
    recorded_datetime = current_datetime - timedelta(hours=2)
    recorded_datetime = recorded_datetime.replace(minute=0, second=0, microsecond=0)
    data['Datetime'] = recorded_datetime

    return data

def dbconnect():
    #db = pymysql.connect(host="127.0.0.1", user="root", password="", database="step")
    return  pymysql.connect(host="database-1.c2iykoijq5qp.us-east-2.rds.amazonaws.com", user="admin", password="CP2A7.m+cc?3k!$", database="mydatabase")
  
    
def collectDataHourly():
    
    db = dbconnect()
    cursor = db.cursor()
    data  = get_hourly_data()
    query = """
    INSERT INTO `energy` (`Date`, `Hour`, `Market_Demand`, `Ontario_Demand`, `Nuclear`, `Gas`, `Hydro`, `Wind`, `Solar`, `Biofuel`, `Total_Output`, `HOEP`, `Hour_1_Predispatch`, `Hour_2_Predispatch`, `Hour_3_Predispatch`, `OR_10_Min_Sync`, `OR_10_Min_non-sync`, `OR_30_Min`)
    VALUES (%(date)s, %(hour)s, %(market_demand)s, %(ontario_demand)s, %(nuclear)s, %(gas)s, %(hydro)s, %(wind)s, %(solar)s, %(biofuel)s, %(total_output)s, %(hoep)s, NULL, NULL, NULL, NULL, NULL, NULL)
    """
   
    cursor.execute(query, {
        'date': data['Datetime'].date(),
        'hour': data['Datetime'].hour,
        'market_demand': data['Market Demand (MW)'],
        'ontario_demand': data['Ontario Demand (MW)'],
        'nuclear': data['Nuclear Supply (MW)'],
        'gas': data['Gas Supply (MW)'],
        'hydro': data['Hydro Supply (MW)'],
        'wind': data['Wind Supply (MW)'],
        'solar': data['Solar Supply (MW)'],
        'biofuel': data['Biofuel Supply (MW)'],
        'total_output': data['Total Supply (MW)'],
        'hoep': data['HOEP ($/MWh)']
    })
    db.commit()
    #cursor.execute("INSERT INTO energy (Date, Hour, Market_Demand,Ontario_Demand, Nuclear, Gas, Hydro, Wind, Solar, Biofuel, Total_Output, HOEP) VALUES ('2023-06-19', 13, 18679, 17159, 8939, 4457, 3867, 698, 391, 24, 18376, 30.94)")
    return 1


print(collectDataHourly())


# close browser
driver.quit()
