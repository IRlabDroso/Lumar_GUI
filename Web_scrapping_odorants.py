from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import pubchempy as pcp
import csv
import re


##### Foundind CIDs for the odours ######

with open("Odorants.csv", "r") as f:
    reader = csv.reader(f, delimiter=";")
    first_line = True
    notfound = []
    CIDs = []
    for i in reader:
        if re.search("Water", i[0]):
            continue
        elif first_line:
            first_line = False
            continue
        else:
            print(i[0])
            CID = pcp.get_cids(str(i[0]), 'name',
                               'substance', list_return='flat')
            if len(CID) == 0:
                notfound.append(i[0])
                print("notfound")
            else:
                print(CID[0])
                CIDs.append(CID[0])

print(notfound)
stillnotfound = []
for i in notfound:
    new_label = re.sub("-", " ", i)
    CID = pcp.get_cids(str(new_label), 'name', 'substance', list_return='flat')
    print(new_label)
    if len(CID) == 0:
        stillnotfound.append(new_label)
        print("notfound")
    else:
        print(CID[0])
        CIDs.append(CID[0])

print(stillnotfound)
##### Web scrapping Part #####
chromedriver_autoinstaller.install()

options = webdriver.ChromeOptions()
options.add_argument("--headless")

driver = webdriver.Chrome()
driver.implicitly_wait(5)
url = "https://pubchem.ncbi.nlm.nih.gov/compound/" + str(CID[0])
driver.get(url)

name = driver.find_element(By.XPATH, "//meta[@property='og:title']")
print(name.get_attribute("content"))

driver.quit()
