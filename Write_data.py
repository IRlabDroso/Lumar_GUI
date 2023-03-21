import csv
from itertools import zip_longest
import pandas as pd

with open ("Data.csv","w", encoding='UTF8', newline='') as f:
    writer = csv.writer(f,delimiter=",")
    
    writer.writerow(["OR","Promoter","Driver","Transgene","Reporter"])
    OR = ["Endogenous","Empty"] + ["DmOR%d" % id for id in range(1, 30)]
    promotor = ["OR42b", "OR47b", "OR59b", "OR22ab", "ORCO"]
    replaced = ["Gal4","Boosted Gal4"]
    KIKO = ["Knockin", "Transgene", "other"]
    reporter = ["GCaMP7f"]
    d = [OR,promotor,replaced,KIKO,reporter]
    rows = zip_longest(*d, fillvalue = pd.NA)
    writer.writerows(rows)

def load_csv(filename):
        odour = dict()
        # Open file in read mode
        file = open(filename,"r")
        # Reading file
        csv_reader = csv.reader(file)
        OR = []
        Promoter = []
        Driver = []
        Transgene = []
        Reporter = []

        for row in csv_reader:
            for i in range(len(row)):
                if (i == 0) & (row[i] != ''): #ORs
                    OR.append(row[i])
                elif (i == 1) & (row[i] != ''): #Promoter
                     Promoter.append(row[i])
                elif (i == 2) & (row[i] != ''): #Driver
                     Driver.append(row[i])
                elif (i == 3) & (row[i] != ''): #Transgene
                     Transgene.append(row[i])
                elif (i == 4) & (row[i] != ''): #Reporter
                     Reporter.append(row[i])    

        return (OR,Promoter,Driver,Transgene,Reporter)


print(load_csv("Data.csv"))