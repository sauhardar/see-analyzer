from re import I
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
from time import sleep

symbols = []
gpas = []
remarks = []

def init_scraper():
  print("Initializing scraper...")
  url = "https://www.see.gov.np/exam/results"
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
  driver.get(url)

  return driver

def scrape_iframe(driver, symbol):
  print("Scraping symbol: ", symbol)
  
  iframe = driver.find_elements(by=By.TAG_NAME, value='iframe')[0]
  driver.switch_to.frame(iframe)

  font_tag = driver.find_element(by=By.TAG_NAME, value="font")
  if font_tag.text.strip() == ":: Symbol Not Found !!!":
    return

  submission_input_elem = driver.find_element(by=By.NAME, value="symbol")
  submission_input_elem.clear()
  submission_input_elem.send_keys(symbol)

  submission_button_elem = driver.find_element(by=By.NAME, value="submit")
  submission_button_elem.click()

  table = driver.find_element(by=By.TAG_NAME, value="tbody")
  data = table.find_elements(by=By.TAG_NAME, value="b")
  
  symbols.append(data[1].text)
  gpas.append(data[2].text)
  remarks.append(data[3].text)
  
  driver.switch_to.default_content()
  return driver

def create_df():
  df = pd.DataFrame({"GPA": gpas, "Remarks": remarks}, index=symbols)
  return df

def padder(symbol):
  as_str = str(symbol)
  if len(as_str) < 8:
    padded = (8 - len(as_str)) * "0" + as_str
    return padded
  else:
    return as_str

def main_scraper():
  print("Running main scraper...")
  driver = init_scraper()
  symbol = 100001

  for i in range(1000):
    print("Running with symbol: ", symbol)
    driver = scrape_iframe(driver, padder(symbol))
    symbol = symbol + 1

  df = create_df()
  df.to_csv('results.csv')
  print(df)

  driver.close()


main_scraper()
