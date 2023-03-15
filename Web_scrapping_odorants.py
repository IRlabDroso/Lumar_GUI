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
            print(i)
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
    if len(CID) == 0:
        stillnotfound.append(new_label)
        print("notfound")
    else:
        CIDs.append(CID[0])

print(stillnotfound)
print(CIDs)


##### Web scrapping Part #####
chromedriver_autoinstaller.install()

options = webdriver.ChromeOptions()
options.add_argument("--headless")

driver = webdriver.Chrome()
driver.implicitly_wait(5)

compound_list = {}
for CID in CIDs:

    url = "https://pubchem.ncbi.nlm.nih.gov/compound/" + str(CID)
    driver.get(url)
    name_content = driver.find_element(
        By.XPATH, "//meta[@property='og:title']")
    name_compound = name_content.get_attribute("content")
    compound_list[CID] = name_compound

driver.quit()
print(compound_list)

##### Web scrapping Part #####

compound_list = {7439: 'Carvone', 14525: 'Fenchone', 8129: '1-Heptanol', 8103: '1-Hexanol', 8914: 'Nonan-1-ol', 18827: '1-Octen-3-OL', 6276: '1-Pentanol', 650: '2,3-Butanedione', 8461: '2,4-Dinitrotoluene', 6569: 'Methyl Ethyl Ketone', 10976: '2-Heptanol', 8051: '2-Heptanone', 18522: '2-Methyltetrahydrofuran-3-one', 7895: '2-Pentanone', 3776: 'Isopropyl Alcohol', 11509: '3-Hexanone', 246728: '3-Octanone', 9862: '6-Methyl-5-hepten-2-one', 175: 'Acetate', 179: 'Acetoin', 7410: 'Acetophenone', 6654: 'alpha-PINENE',
                 6713932: '(4R,5R)-5-(1,2-dihydroxyethyl)-3,4-dihydroxy-2-oxolanone', 240: 'Benzaldehyde', 11529: 'Butyl propionate', 264: 'Butyric Acid', 273: 'Cadaverine', 7794: 'Citronellal', 62378: 'Dihydrojasmone', 402: 'Hydrogen Sulfide', 22311: 'Limonene', 174: 'Ethylene Glycol', 62572: 'Ethyl 3-hydroxybutyrate', 8857: 'Ethyl Acetate', 7749: 'Ethyl propionate', 12191: '2-Butenoic acid, ethyl ester', 7344: 'Ethyl lactate', 6184: 'Hexanal', 798: 'Indole', 6590: 'Isobutyric acid', 91604: 'Lyral', 1254: 'Menthol', 7128: 'Methyl isoeugenol', 6584: 'Methyl acetate', 4133: 'Methyl Salicylate', 335: 'o-Cresol', 454: 'Octanal', 998: 'Phenylacetaldehyde', 6054: '2-Phenylethanol', 1032: 'Propionic Acid', 7997: 'Propyl acetate', 1049: 'Pyridine', 31268: 'Pyrrolidine', 19801: 'Dec-2-enal', 10460: 'Hexenal', 9251: 'Thietane', 288227: '4a,5-Dimethyl-3-(prop-1-en-2-yl)-1,2,3,4,4a,5,6,7-octahydronaphthalene', 8468: 'Vanillic Acid', 31272: 'Butyl acetate', 7165: 'Ethyl benzoate', 7342: 'Ethyl isobutyrate', 7780: '3,7-Dimethylocta-2,6-dienyl acetate', 12180: 'Methyl butyrate', 7824: 'Methyl hexanoate', 11124: 'Methyl propionate', 12348: 'Pentyl acetate'}

with open("Corrected_odors.csv", "r") as filetoread, open("Corrected_odors.csv", "w") as filetowrite:
    reader = csv.reader(filetoread, delimiter=",")
    writer = csv.writer(filetowrite, dialect='excel', delimiter=',')
    writer.writerow(["Odor_id", "Odor_name"])
    already_in = []
    for i in reader:
        already_in.append(i[0])
    for id, name in compound_list.items(), reader:
        if id not in already_in:
            writer.writerow([id, name])
