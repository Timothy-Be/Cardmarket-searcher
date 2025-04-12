from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import dill


def parseCost(costText):
    toParse = costText[:len(costText) - 2]
    nbr = ""
    for j in range(len(toParse)):
        if toParse[j] == ',':
            nbr += '.'
        elif toParse[j] != '.':
            nbr += toParse[j]
    return float(nbr)


merchants = {}
prices = {}
cards = {}

f = open("cards.txt", "r")
lines = f.readlines()
line_nbr = 0


def main(line_nbr):
    service = ChromeService(executable_path=ChromeDriverManager().install())

    options = ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options, service=service)
    driver.get("https://www.cardmarket.com/en/Magic")

    while line_nbr < len(lines):
        """Parse data"""
        line = lines[line_nbr]
        item = ""
        for c in line:
            if c == '(':
                break
            if c.isalpha() or c == ' ':
                item += c
        item = item.strip()
        if item == "deck" or item == "Deck" or item == "" or item == "\n" or item == "Sideboard":
            line_nbr += 1
            continue

        print(item)
        cards[item] = {}

        sleep(3)  # to avoid error 429 (too many requests in a short time)

        """Find item"""
        searchBox = driver.find_element(by=By.ID, value="ProductSearchInput")
        searchButton = driver.find_element(by=By.ID, value="search-btn")

        searchBox.send_keys(item)
        searchButton.click()

        try:
            WebDriverWait(driver, timeout=3).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".col-12.col-md-8.px-2.flex-column a")))  # wait for page to load
            article = driver.find_element(by=By.CSS_SELECTOR, value=".col-12.col-md-8.px-2.flex-column a")
            article.click()
        except:
            print("error 429 ? (1)")

        sleep(3)  # to avoid error 429 (too many requests in a short time)

        """Setup filter for search"""
        try:
            WebDriverWait(driver, timeout=3).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "fonticon-filter.cursor-pointer")))  # wait for page to load
            filterToggle = driver.find_element(by=By.CLASS_NAME, value="fonticon-filter.cursor-pointer")
            driver.execute_script("arguments[0].click();", filterToggle)
        except:
            print("error 429 ? (2)")
            pass

        sleep(3)  # to avoid error 429 (too many requests in a short time)

        WebDriverWait(driver, timeout=10).until(
            EC.element_to_be_clickable((By.ID, "FilterForm")))  # wait for page to load

        # click() doesn't work  for wathever reason
        try:
            proSellerFilter = driver.find_element(by=By.NAME, value="sellerType[1]")
            if not proSellerFilter.is_selected():
                driver.execute_script("arguments[0].click();", proSellerFilter)
        except:
            print(f"Pro Seller not available for {line}")

        sleep(3)  # to avoid error 429 (too many requests in a short time)

        try:
            powerSellerFilter = driver.find_element(by=By.NAME, value="sellerType[2]")
            if not powerSellerFilter.is_selected():
                driver.execute_script("arguments[0].click();", powerSellerFilter)
        except:
            print(f"Power Seller not available for {line}")

        sleep(3)  # to avoid error 429 (too many requests in a short time)

        # english is always available
        englishFilter = driver.find_element(by=By.NAME, value="language[1]")
        if not englishFilter.is_selected():
            driver.execute_script("arguments[0].click();", englishFilter)
        try:
            frenchFilter = driver.find_element(by=By.NAME, value="language[2]")
            if not frenchFilter.is_selected():
                driver.execute_script("arguments[0].click();", frenchFilter)
        except:
            print(f"French not available for {line}")

        sleep(3)  # to avoid error 429 (too many requests in a short time)

        minCondFilter = driver.find_element(by=By.XPATH, value='//span[text()="Min. Condition"]')
        if not minCondFilter.is_selected():
            driver.execute_script("arguments[0].click();", minCondFilter)

        sleep(3)  # to avoid error 429 (too many requests in a short time)

        conditionFilter = driver.find_element(by=By.NAME, value="minCondition")
        selectCondition = Select(conditionFilter)
        selectCondition.select_by_visible_text("Excellent")

        applyButton = driver.find_element(by=By.NAME, value="apply")
        driver.execute_script("arguments[0].click();", applyButton)
        # applyButton.click()

        """Get all corresponding items"""
        for i in range(5):
            try:
                WebDriverWait(driver, timeout=3).until(
                    EC.element_to_be_clickable((By.ID, "loadMore")))  # wait for page to load
                more = driver.find_element(by=By.ID, value="loadMore")
                driver.execute_script("arguments[0].click();", more)
                sleep(1)  # wait for page to load
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);")  # force load new items by scrolling down the page
            except:
                print("Skipped show more results")
                break

        names = driver.find_elements(by=By.CLASS_NAME, value="d-flex.has-content-centered.me-1")
        costs = driver.find_elements(by=By.CLASS_NAME, value="color-primary.small.text-end.text-nowrap.fw-bold")

        """Get rid of all '' values"""
        namesText = []
        costsText = []
        for i in range(len(names)):
            if names[i].text != '':
                namesText.append(names[i].text)
        for i in range(len(costs)):
            if costs[i].text != '':
                costsText.append(costs[i].text)

        """Add elements to dictionaries"""
        for i in range(len(namesText)):
            cards[item][namesText[i]] = parseCost(costsText[i])
            if namesText[i] not in merchants:
                merchants[namesText[i]] = [item]

            elif item not in merchants[namesText[i]]:
                merchants[namesText[i]].append(item)

            prices[namesText[i]] = parseCost(costsText[i])

        with open("save_names.pkl", "wb") as file:
            dill.dump(merchants, file)
        with open("save_prices.pkl", "wb") as file:
            dill.dump(prices, file)
        with open("save_cards.pkl", "wb") as file:
            dill.dump(cards, file)

        line_nbr += 1
        """except Exception as e:
            print(f"An error as occured on {line}")
            pass"""
    driver.quit()


while line_nbr < len(lines):
    try:
        main(line_nbr)
    except:
        print("restart")
        continue
    break

f.close()

l1 = sorted(merchants.items(), key=lambda k: len(k[1]), reverse=True)[:10]
if len(l1) > 0:
    print(len(l1[0][1]))
print(l1)
l2 = []
for t in l1:
    l2.append((t[0], prices[t[0]]))
print(l2)

print(cards)
