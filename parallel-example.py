# import IPython.parallel as ipp   # Python 2
import ipyparallel as ipp     # Python 3
rc = ipp.Client(profile='default', cluster_id='')
rc.ids

dview = rc[:]
dview.block = True
dview.apply(lambda : "Hello, World")

lview = rc.load_balanced_view()
lview.block = True

import pandas 
dat = pandas.read_csv('/global/scratch/paciorek/bayArea.csv', header = None, encoding = 'latin1')
dat.columns = ('Year','Month','DayofMonth','DayOfWeek','DepTime','CRSDepTime',
'ArrTime','CRSArrTime','UniqueCarrier','FlightNum','TailNum',
'ActualElapsedTime','CRSElapsedTime','AirTime','ArrDelay','DepDelay',
'Origin','Dest','Distance','TaxiIn','TaxiOut','Cancelled','CancellationCode',
'Diverted','CarrierDelay','WeatherDelay','NASDelay','SecurityDelay','LateAircraftDelay')

dview.execute('import statsmodels.api as sm')

dat2 = dat.loc[:, ('DepDelay','Year','Dest','Origin')]
dests = dat2.Dest.unique()

mydict = dict(dat2 = dat2, dests = dests)
dview.push(mydict)

def f(id):
    sub = dat2.loc[dat2.Dest == dests[id],:]
    sub = sm.add_constant(sub)
    model = sm.OLS(sub.DepDelay, sub.loc[:,('const','Year')])
    results = model.fit()
    return results.params

import time
time.time()
parallel_result = lview.map(f, range(len(dests)))
#result = map(f, range(len(dests)))
time.time()
