from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import timeit
import pandas as pd
from time import sleep
import os

symbols = []
gpas = []
remarks = []

def init_scraper():
    print("🕸\tInitializing scraper...")
    url = "https://www.see.gov.np/exam/results"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)

    return driver

def scrape_iframe(driver, symbol):
    # print("🧹\tScraping symbol: ", symbol)

    iframe = driver.find_elements(by=By.TAG_NAME, value='iframe')[0]
    driver.switch_to.frame(iframe)

    font_tag = driver.find_element(by=By.TAG_NAME, value="font")
    if font_tag.text.strip() == ":: Symbol Not Found !!!":
        print("❕️\tSymbol not found: ", symbol)
        print("Skipping...\nn")
        driver.switch_to.default_content()
        return driver

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
    df = pd.DataFrame({"symbol": symbols, "gpa": gpas, "remarks": remarks})
    return df

def padder(symbol):
    as_str = str(symbol)
    if len(as_str) < 8:
        padded = (8 - len(as_str)) * "0" + as_str
        return padded
    else:
        return as_str

def main_scraper():
    print("🕷\tRunning main scraper...")
    if not os.path.exists("results"):
        os.makedirs("results")

    driver = init_scraper()
    initial_symbol = 302_467
    to_add = 0
    symbol = initial_symbol
    start = timeit.default_timer()
    errors = 0
    file_storage_increment = 1000
    """
    00304119W,3.95,COMPLETED
    00402467M,2.55,COMPLETED

    The current method started at 302_467 and then restarted at 402_467, so missed otu on 400_001 until 402_466
    """
    for _ in range(10_000):
        try:
            driver = scrape_iframe(driver, padder(symbol))
            symbol = symbol + 1
            if len(symbols) % 100 == 0:
                print(f"🎉\t{len(symbols)} rows completed.")
            
            if len(symbols) % file_storage_increment == 0:
                df = create_df()
                # os.remove(f"results/first_{len(symbols) - file_storage_increment}.csv") if len(symbols) > file_storage_increment else None
                df.to_csv(f"results/{len(symbols)}.csv", index=False)
        except Exception as e:
            print(e)

            print("❌\tError occurred while scraping symbol: ", symbol)
            print("😵‍💫\tRestarting driver...")
            errors += 1
            driver = init_scraper()
            to_add = to_add + 100_000
            symbol = initial_symbol + to_add

    df = create_df()
    df.to_csv('results/final_results.csv')
    end = timeit.default_timer()
    print(f"⏲\tTotal time taken: {end - start} seconds.")
    print(f"💥\tTotal errors: {errors}.")
    print(df)

    driver.close()

main_scraper()
