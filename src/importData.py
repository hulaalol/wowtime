from os import listdir
from os.path import isfile, join
import pandas as pd
import numpy as np
from dateutil import parser
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))



onlyfiles = [f for f in listdir("../data/") if isfile(join("../data/", f))]

s = pd.Period("2016-01",freq="M")
e = pd.Period("2019-12",freq="M")

data = pd.Series(pd.date_range(start=s.start_time, end = e.end_time, freq="H")).to_frame("date")
data['gt'] = np.zeros(len(data))

data.set_index('date', inplace=True)

def parseDate(line):
    line = line.lower().replace("pm","").replace("am","")
    try:
        return parser.parse(line)
    except ValueError:
        return None

def getNextDate(filepointer):
    nextDate = None
    while nextDate is None:
        line = filepointer.readline()
        if ":" in line:
            nextDate = parseDate(line)
        if line == "":
            break
    #print("line was: "+line)
    return nextDate

def insertGametime(start,end):
    # TODO: filter duplicates
    #find row
    #row = data.loc[start]
    if start is None or end is None:
        print("ERROR: start or end is None!")
        return


    index = start.replace(minute=0,second=0)
    indexString = index.strftime('%Y-%m-%d %H:%M:%S')

    duration = (end-start).total_seconds()

    if end < start:
        print("ERROR: end is before start!")

    # check if start and end have the same hour
    # if not, fill start to next hour up and insert
    # recursively call with full hour and end
    if start.hour == end.hour:
        data.loc[indexString]['gt'] += duration
    else:
        fillUp = start.replace(minute=0, second=0) + timedelta(hours=1)
        data.loc[indexString]['gt'] += (fillUp-start).total_seconds()
        insertGametime(fillUp, end)



########## START

gametimes = {}

for f in onlyfiles:

    with open("../data/"+f,'r') as fp:

        start = getNextDate(fp)
        print(start)
        end = getNextDate(fp)
        print(end)
        gametimes[start.strftime('%Y-%m-%d %H:%M:%S')] = end.strftime('%Y-%m-%d %H:%M:%S')

        while start is not None and end is not None:
            gametimes[start.strftime('%Y-%m-%d %H:%M:%S')] = end.strftime('%Y-%m-%d %H:%M:%S')
            start = getNextDate(fp)
            print(start)
            end = getNextDate(fp)
            print(end)
            #insertGametime(start,end)

        fp.close();

#print(gametimes)

for start in gametimes:
    insertGametime(parser.parse(start),parser.parse(gametimes[start]))

print(data)

maxvalue = data['gt'].max()
print("max value of gt: "+str(maxvalue))

minvalue = data['gt'].min()
print("min value of gt: "+str(minvalue))

sum = data['gt'].sum()
print("gametime in hours: "+str(sum/3600))


plt.figure()
data['gt'].plot()
plt.show()

"""
    line = fp.readline()
        while line:
                try:
                    startDate = parser.parse(line)

                    # skip lines with tabs and spaces
                    line = fp.readline()
                    endDate = None

                    while endDate is None:
                        try:
                            endDate = parser.parse(line)
                            line = fp.readline()
                        except ValueError:
                            print("searching for endDate...")

                    gt = float(line)
                    n = nearest(data[0,:] , startDate)
                    data[data[0] == n] += gt

                    print("success")
                except ValueError:
                    print("Skip introduction lines...")
                line = fp.readline()
    
    """