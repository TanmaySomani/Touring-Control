"""Reproducible BITRE demand analysis + explicitly simulated commercial portfolio.
Run with Python 3.11+ and openpyxl. No live airline or Flight Centre integration.
"""
from __future__ import annotations
import csv, hashlib, json, math, random, sqlite3, statistics
from datetime import date, timedelta
from pathlib import Path
from collections import defaultdict
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 10, 9)
SOURCE = 'https://www.bitre.gov.au/resource/aviation/international-airline-activity-time-series-data'
DOWNLOAD = 'https://www.bitre.gov.au/sites/default/files/documents/international_airline_activity_citypairs_2009tocurrent_0626.xlsx'
ROUTES = [
 {'id':'BNE-AKL','origin':'Brisbane','destination':'Auckland','country':'New Zealand','region':'Oceania','tour':'Northern New Zealand Explorer','airline':'Air New Zealand','cost':690,'fare':990,'pace':.94},
 {'id':'SYD-TYO','origin':'Sydney','destination':'Tokyo','country':'Japan','region':'Asia','tour':'Japan Discovery','airline':'Japan Airlines','cost':1420,'fare':1870,'pace':1.04},
 {'id':'BNE-TYO','origin':'Brisbane','destination':'Tokyo','country':'Japan','region':'Asia','tour':'Japan Autumn Trails','airline':'Qantas','cost':1490,'fare':1990,'pace':.63},
 {'id':'MEL-SGN','origin':'Melbourne','destination':'Ho Chi Minh City','country':'Vietnam','region':'Asia','tour':'Vietnam Heritage Journey','airline':'Vietnam Airlines','cost':920,'fare':1290,'pace':.72},
 {'id':'SYD-SEL','origin':'Sydney','destination':'Seoul','country':'South Korea','region':'Asia','tour':'Colours of South Korea','airline':'Korean Air','cost':1280,'fare':1690,'pace':.98},
 {'id':'MEL-SIN','origin':'Melbourne','destination':'Singapore','country':'Singapore','region':'Asia','tour':'Singapore & Beyond','airline':'Singapore Airlines','cost':1050,'fare':1420,'pace':.82},
]

def month_add(m: str, count: int) -> str:
 y, mo = map(int,m.split('-')); ix=y*12+mo-1+count
 return f'{ix//12:04d}-{ix%12+1:02d}'

def forecast(series: dict, target: str, trend=True) -> float:
 """Seasonal reference times trailing six observed months' YoY growth. No target leakage."""
 previous=month_add(target,-12)
 if previous not in series: raise ValueError(f'Missing seasonal reference: {previous}')
 observed=sorted(k for k in series if k < target)
 ratios=[series[k]/series[month_add(k,-12)] for k in observed[-6:] if month_add(k,-12) in series and series[month_add(k,-12)]>0]
 multiplier=max(.8,min(1.2,statistics.mean(ratios))) if ratios and trend else 1
 return series[previous]*multiplier

def quantile(values, q):
 values=sorted(values); idx=(len(values)-1)*q; lo=int(idx)
 return values[lo]+(values[min(lo+1,len(values)-1)]-values[lo])*(idx-lo)

def completion(days):
 """Illustrative booking-curve knots; linear interpolation. Not fitted to market traffic."""
 knots=[(0,1),(30,.94),(60,.79),(90,.64),(120,.48),(180,.26),(240,.14)]
 for (a,x),(b,y) in zip(knots,knots[1:]):
  if days <= b: return x+(y-x)*max(0,days-a)/(b-a)
 return .14

def write_csv(path, rows):
 with path.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def run():
 raw=ROOT/'data/raw/bitre-citypairs-jun2026.xlsx'
 book=openpyxl.load_workbook(raw,read_only=True,data_only=True)
 source_rows=list(book['Data'].iter_rows(min_row=2,values_only=True))
 markets=[]; errors=[]; seen=set(); series_by=defaultdict(dict)
 lookup={(r['origin'],r['destination']):r['id'] for r in ROUTES}
 for row in source_rows:
  dt,origin,dest=row[:3]
  if not isinstance(dt,date) or dt.year<2023 or (origin,dest) not in lookup: continue
  key=(lookup[(origin,dest)],dt.strftime('%Y-%m'))
  if key in seen: errors.append(f'Duplicate market key: {key}'); continue
  seen.add(key)
  pin,pout,total=map(lambda x:float(x or 0),(row[4],row[7],row[10]))
  if min(pin,pout,total)<0 or abs(pin+pout-total)>.01: errors.append(f'Invalid passenger reconciliation: {key}')
  record={'route':key[0],'month':key[1],'inbound':int(pin),'outbound':int(pout),'total':int(total),'source':'BITRE actual'}
  markets.append(record); series_by[key[0]][key[1]]=pout
 if errors: raise ValueError(errors)
 if len(series_by)!=len(ROUTES): raise ValueError('Expected six routes')
 last=max(x['month'] for x in markets)
 predictions=[]; backtests=[]; model_scores=[]
 for route in ROUTES:
  s=series_by[route['id']]
  required=[month_add('2023-01',i) for i in range(42)]
  missing=[m for m in required if m not in s]
  if missing: raise ValueError(f'{route["id"]}: missing months {missing}')
  tests=[]
  for target in sorted(k for k in s if k>='2025-01'):
   train={k:v for k,v in s.items() if k<target}
   p=forecast(train,target); naive=forecast(train,target,False)
   tests.append({'route':route['id'],'month':target,'actual':int(s[target]),'forecast':round(p),'baseline':round(naive),'absoluteError':round(abs(p-s[target]))})
  # First 12 rolling-origin errors calibrate band; last six evaluate it out of sample.
  use_trend=sum(t['absoluteError'] for t in tests[:12]) < sum(abs(t['actual']-t['baseline']) for t in tests[:12])
  for t in tests:
   t['trendForecast']=t['forecast']
   t['forecast']=t['forecast'] if use_trend else t['baseline']
   t['absoluteError']=abs(t['forecast']-t['actual'])
   t['split']='validation' if t['month']<'2026-01' else 'holdout'
  width=quantile([abs(t['forecast']-t['actual'])/max(t['forecast'],1) for t in tests[:12]],.8)
  holdout=tests[12:]
  coverage=sum(t['forecast']*(1-width)<=t['actual']<=t['forecast']*(1+width) for t in holdout)/len(holdout)
  denominator=sum(t['actual'] for t in holdout)
  score={'route':route['id'],'selectedModel':'Seasonal + trend' if use_trend else 'Seasonal baseline','wape':round(sum(t['absoluteError'] for t in holdout)/denominator*100,2),'baselineWape':round(sum(abs(t['actual']-t['baseline']) for t in holdout)/denominator*100,2),'trendWape':round(sum(abs(t['actual']-t['trendForecast']) for t in holdout)/denominator*100,2),'mae':round(statistics.mean(t['absoluteError'] for t in holdout)),'testMonths':len(holdout),'validationMonths':12,'holdoutCoverage':round(coverage*100,1),'bandWidth':round(width,4)}
  model_scores.append(score); backtests.extend(tests)
  extended=s.copy()
  for i in range(1,13):
   m=month_add(last,i)
   # Growth is fixed using only observed data; seasonal prior stays observed for this 12-month horizon.
   reference=s[month_add(m,-12)]
   ratios=[s[k]/s[month_add(k,-12)] for k in sorted(s)[-6:] if s.get(month_add(k,-12),0)>0]
   p=reference*(max(.8,min(1.2,statistics.mean(ratios))) if use_trend else 1)
   predictions.append({'route':route['id'],'month':m,'forecast':round(p),'lower':max(0,round(p*(1-width))),'upper':round(p*(1+width)),'source':'Model estimate'})

 rng=random.Random(417); contracts=[]; bookings=[]; prior=[]
 for ri,route in enumerate(ROUTES):
  for i in range(8):
   departure=date(2026,11,18)+timedelta(days=i*18+ri*3)
   days=(departure-AS_OF).days
   seats=[28,32,36,40][(i+ri)%4]
   demand=seats*route['pace']*rng.uniform(.89,1.09)
   booked=max(1,min(seats,round(demand*completion(days))))
   expected=max(booked,min(seats,round(booked/completion(days))))
   release=departure-timedelta(days=45)
   cid=f'TC-{ri+1:02d}{i+1:03d}'
   budget_pax=round(seats*.85)
   contracts.append({'id':cid,'route':route['id'],'tour':route['tour'],'airline':route['airline'],'departure':departure.isoformat(),'releaseDate':release.isoformat(),'seats':seats,'booked':booked,'forecastPax':expected,'forecastLow':max(booked,round(expected*.8)),'forecastHigh':min(seats,round(expected*1.2)),'unitCost':route['cost'],'sellPrice':route['fare'],'releaseFee':round(route['cost']*.12),'maxRelease':math.floor(seats*.5),'minGroup':10,'budgetPax':budget_pax,'owner':['S. Chen','J. Patel','A. Wilson'][ri%3],'region':route['region'],'origin':route['origin'],'status':'Simulated contract'})
   for j in range(booked):
    # Passenger-level synthetic booking transactions, no personal data.
    booked_date=min(AS_OF,departure-timedelta(days=rng.randint(max(days,30),240)))
    bookings.append({'id':f'BK-{cid}-{j+1:03d}','contractId':cid,'bookedAt':booked_date.isoformat(),'passengers':1,'channel':rng.choice(['Retail','Online','Trade']),'status':'Confirmed','airRevenue':route['fare'],'source':'Simulated booking'})
   ly_pax=max(0,min(seats,round(booked*rng.uniform(.82,1.06))))
   prior.append({'contractId':cid,'departure':departure.replace(year=2025).isoformat(),'seats':seats,'bookedAtComparableLeadTime':ly_pax,'revenue':ly_pax*route['fare'],'source':'Simulated prior-year comparator'})
 # Seed realistic, repairable problems into a separate raw booking feed.
 raw_bookings=[dict(b) for b in bookings]
 raw_bookings.append(dict(bookings[0]))
 orphan=dict(bookings[1]); orphan.update(id='BK-ORPHAN-001',contractId='TC-MISSING'); raw_bookings.append(orphan)
 future=dict(bookings[2]); future.update(id='BK-FUTURE-001',bookedAt='2026-10-12'); raw_bookings.append(future)
 clean=[]; ids=set(); issues=[]; contract_keys={c['id'] for c in contracts}
 for b in raw_bookings:
  reason='Duplicate booking ID' if b['id'] in ids else 'Unknown contract ID' if b['contractId'] not in contract_keys else 'Booking after snapshot' if b['bookedAt']>AS_OF.isoformat() else None
  if reason: issues.append({'record':b['id'],'rule':reason,'action':'Quarantined','severity':'Warning'}); continue
  ids.add(b['id']); clean.append(b)
 assert len(clean)==len(bookings)
 for c in contracts: assert sum(b['passengers'] for b in clean if b['contractId']==c['id'])==c['booked']
 data={'asOf':AS_OF.isoformat(),'marketThrough':last,'routes':ROUTES,'market':markets,'predictions':predictions,'backtests':backtests,'modelScores':model_scores,'contracts':contracts,'bookings':clean,'priorYear':prior,'quality':{'rawRecords':len(raw_bookings),'acceptedRecords':len(clean),'quarantined':issues,'marketRows':len(markets),'marketReconciled':True,'missingMonths':0,'duplicateMarketKeys':0,'contractReconciled':True},'provenance':{'publisher':'Bureau of Infrastructure and Transport Research Economics','sourceUrl':SOURCE,'downloadUrl':DOWNLOAD,'releaseDate':'2026-09-18','retrievedDate':'2026-10-09','sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'measure':'Outbound revenue passenger movements on scheduled international services. City-pair uplift/discharge data; includes all carriers and may include through traffic. Not tourism-only demand, airline availability or My Touring sales.','simulationSeed':417,'rawMarketRows':len(source_rows)}}
 (ROOT/'public/data/portfolio.json').write_text(json.dumps(data,separators=(',',':')))
 (ROOT/'data/processed/portfolio.json').write_text(json.dumps(data,indent=2))
 for name,rows in [('market_actuals',markets),('market_forecasts',predictions),('forecast_backtest',backtests),('contracts',contracts),('bookings_raw',raw_bookings),('bookings_clean',clean),('prior_year',prior)]:
  write_csv(ROOT/f'data/processed/{name}.csv',rows)
  if name!='bookings_raw': write_csv(ROOT/f'public/reports/{name}.csv',rows)
 db=sqlite3.connect(ROOT/'data/processed/inventory.sqlite')
 for name,rows in [('market_actuals',markets),('contracts',contracts),('bookings',clean),('prior_year',prior)]:
  db.execute(f'DROP TABLE IF EXISTS {name}')
  cols=list(rows[0]); types=['INTEGER' if isinstance(rows[0][k],int) else 'REAL' if isinstance(rows[0][k],float) else 'TEXT' for k in cols]
  db.execute(f'CREATE TABLE {name} ({", ".join(k+" "+t for k,t in zip(cols,types))})')
  db.executemany(f'INSERT INTO {name} VALUES ({",".join("?" for _ in cols)})',[[r[k] for k in cols] for r in rows])
 db.execute('CREATE UNIQUE INDEX IF NOT EXISTS market_grain ON market_actuals(route,month)')
 db.execute('CREATE UNIQUE INDEX IF NOT EXISTS contract_key ON contracts(id)')
 db.execute('CREATE UNIQUE INDEX IF NOT EXISTS booking_key ON bookings(id)')
 db.commit(); db.close()
 print(json.dumps({'routes':len(ROUTES),'marketRows':len(markets),'contracts':len(contracts),'bookings':len(clean),'quarantined':len(issues),'forecastWape':model_scores}))

if __name__=='__main__': run()
