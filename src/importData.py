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
e = pd.Period("2021-06",freq="M")

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

#read files
for f in onlyfiles:

    with open("../data/"+f,'r') as fp:
        start = getNextDate(fp)
        end = getNextDate(fp)
        gametimes[start.strftime('%Y-%m-%d %H:%M:%S')] = end.strftime('%Y-%m-%d %H:%M:%S')

        while start is not None and end is not None:
            gametimes[start.strftime('%Y-%m-%d %H:%M:%S')] = end.strftime('%Y-%m-%d %H:%M:%S')
            start = getNextDate(fp)
            end = getNextDate(fp)
        fp.close();

#insert into dataframe
for start in gametimes:
    insertGametime(parser.parse(start),parser.parse(gametimes[start]))


#remove zero rows
#data = data[data['gt'] != 0]

maxvalue = data['gt'].max()
print("max value of gt: "+str(maxvalue))

minvalue = data['gt'].min()
print("min value of gt: "+str(minvalue))

sum = data['gt'].sum()
print("gametime in hours: "+str(sum/3600))

# plot
#plt.figure()
#data['gt'].plot()
#plt.show()

def getWeekday(datestring):
    return parser.parse(datestring).weekday()

def removeClock(datestring):
    return datestring[0:10]

def assignWeek(weekdays):
    weeks = []
    weekIndex = 0
    block = False
    for w in weekdays:
        if(w == 0 and not block):
            weekIndex += 1
            block = True
        if(w == 6 and block):
            block = False

        weeks.append(weekIndex)
    return weeks

def getMonth(datestring):
    return datestring[0:7]


data['day'] = list(map(removeClock,data.index.format()))
data['weekday'] = list(map(getWeekday, data.index.format()))
data['month'] = list(map(getMonth, data.index.format()))

weeks = assignWeek(data['weekday'])
data['week'] = weeks

print(data)

collapseByDay = data.groupby('day').agg({'gt':'sum', 'weekday':'first'})
#print(collapseByDay)
plt.figure()
collapseByDay['gt'].plot()
plt.show()

collapseByWeekDay = data.groupby('weekday').agg({'gt':'mean'})
plt.figure()
collapseByWeekDay['gt'].plot()
plt.show()

collapseByWeek = data.groupby('week').agg({'gt':'sum'})
collapseByWeek['gt'].plot.bar(x='week', y='gt', rot=0)
plt.show()

collapseByMonth = data.groupby('month').agg({'gt':'sum'})
collapseByMonth['gt'].plot.bar(x='month', y='gt', rot=90)
plt.show()
