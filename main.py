from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

service = ChromeService(executable_path=ChromeDriverManager().install())

options = ChromeOptions()
driver = webdriver.Chrome(options=options, service=service)
driver.get("https://www.cardmarket.com/en/Magic")

cards = {}
prices = {}

f = open("cards.txt", "r")
for line in f:
    #try:
    """Parse data"""
    item = ""
    for c in line:
        if c == '(':
            break
        if c.isalpha() or c == ' ':
            item += c
    item = item.strip()
    if item == "deck" or item == "Deck" or item == "" or item == "\n" or item == "Sideboard":
        continue

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
        pass

    """Setup filter for search"""
    try:
        WebDriverWait(driver, timeout=3).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "fonticon-filter")))  # wait for page to load
        filterToggle = driver.find_element(by=By.CLASS_NAME, value="fonticon-filter")
        filterToggle.click()
    except:
        print("error 429 ?")
        pass

    WebDriverWait(driver, timeout=3).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".custom-control.custom-checkbox")))  # wait for page to load

    #click() doesn't work  for wathever reason
    try:
        proSellerFilter = driver.find_element(by=By.NAME, value="sellerType[1]")
        if not proSellerFilter.is_selected():
            driver.execute_script("arguments[0].click();", proSellerFilter)
    except:
        print(f"Pro Seller not available for {line}")
    try:
        powerSellerFilter = driver.find_element(by=By.NAME, value="sellerType[2]")
        if not powerSellerFilter.is_selected():
            driver.execute_script("arguments[0].click();", powerSellerFilter)
    except:
        print(f"Power Seller not available for {line}")

    #english is always available
    englishFilter = driver.find_element(by=By.NAME, value="language[1]")
    if not englishFilter.is_selected():
        driver.execute_script("arguments[0].click();", englishFilter)
    try:
        frenchFilter = driver.find_element(by=By.NAME, value="language[2]")
        if not frenchFilter.is_selected():
            driver.execute_script("arguments[0].click();", frenchFilter)
    except:
        print(f"French not available for {line}")

    conditionFilter = driver.find_element(by=By.NAME, value="minCondition")
    selectCondition = Select(conditionFilter)
    selectCondition.select_by_visible_text("Excellent")

    applyButton = driver.find_element(by=By.NAME, value="apply")
    applyButton.click()

    """Get all corresponding items"""
    for i in range(5):
        try:
            WebDriverWait(driver, timeout=3).until(
                EC.element_to_be_clickable((By.ID, "loadMore")))  # wait for page to load
            more = driver.find_element(by=By.ID, value="loadMore")
            more.click()
            sleep(0.5)  # wait for page to load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # force load new items by scrolling down the page
        except:
            break

    names = driver.find_elements(by=By.CLASS_NAME, value="d-flex.has-content-centered.mr-1")
    costs = driver.find_elements(by=By.CLASS_NAME, value="font-weight-bold.color-primary.small.text-right.text-nowrap")

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
        if namesText[i] not in cards:
            cards[namesText[i]] = [item]

            toParse = costsText[i][:len(costsText[i]) - 2]
            nbr = ""
            for j in range(len(toParse)):
                if toParse[j] == ',':
                    nbr += '.'
                elif toParse[j] != '.':
                    nbr += toParse[j]
            prices[namesText[i]] = float(nbr)

        elif item not in cards[namesText[i]]:
            cards[namesText[i]].append(item)

            toParse = costsText[i][:len(costsText[i]) - 2]
            nbr = ""
            for j in range(len(toParse)):
                if toParse[j] == ',':
                    nbr += '.'
                elif toParse[j] != '.':
                    nbr += toParse[j]
            prices[namesText[i]] += float(nbr)

    """except Exception as e:
        print(f"An error as occured on {line}")
        pass"""

l1 = sorted(cards.items(), key=lambda k: len(k[1]), reverse=True)[:10]
if len(l1) > 0:
    print(len(l1[0][1]))
print(l1)
l2 = []
for t in l1:
    l2.append((t[0], prices[t[0]]))
print(l2)

driver.quit()
