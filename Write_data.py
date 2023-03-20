import csv
from itertools import zip_longest

with open ("Data.csv","w", encoding='UTF8', newline='') as f:
    writer = csv.writer(f,delimiter=",")
    
    OR = ["Endogenous","Empty"] + ["DmOR%d" % id for id in range(1, 30)]
    promotor = ["OR42b", "OR47b", "OR59b", "OR22ab", "ORCO"]
    replaced = ["Gal4","Boosted Gal4"]
    KIKO = ["Knockin", "Transgene", "other"]
    reporter = ["GCaMP7f"]
    d = [OR,promotor,replaced,KIKO,reporter]
    rows = zip_longest(*d, fillvalue = '')
    writer.writerows(rows)

def load_csv(filename):
        odour = dict()
        # Open file in read mode
        file = open(filename,"r")
        # Reading file
        csv_reader = csv.reader(file)
        first_line = True
        for row in csv_reader:
            if first_line:
                first_line=False
                continue
            odour[row[0]] = row[1]
        
        return odour

print(load_csv("Data.csv"))