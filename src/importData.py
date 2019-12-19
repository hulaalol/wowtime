from os import listdir
from os.path import isfile, join
import pandas as pd
import numpy as np
from dateutil import parser


def nearest(items, pivot):
    return min(items, key=lambda x: abs(x - pivot))



onlyfiles = [f for f in listdir("../data/") if isfile(join("../data/", f))]

s = pd.Period("2016-01",freq="M")
e = pd.Period("2019-12",freq="M")

data = pd.Series(pd.DatetimeIndex(start=s.start_time, end = e.end_time, freq="D")).to_frame("date")
data['gt'] = np.zeros(len(data))


print(data)

for f in onlyfiles:

    with open("../data/"+f,'r') as fp:
        line = fp.readline()
        while line:
                try:
                    startDate = parser.parse(line)

                    # skip lines with tabs and spaces
                    line = fp.readline()

                    endDate = parser.parse(line)
                    line = fp.readline()
                    gt = float(line)
                    n = nearest(data[0,:] , startDate)
                    data[data[0] == n] += gt

                    print("success")
                except ValueError:
                    print("Skip introduction lines...")
                line = fp.readline()

        fp.close();


    #"16 January 2016 02:04:29 AM"