export type Contract = { id:string; route:string; tour:string; airline:string; departure:string; releaseDate:string; seats:number; booked:number; forecastPax:number; forecastLow:number; forecastHigh:number; unitCost:number; sellPrice:number; releaseFee:number; maxRelease:number; minGroup:number; budgetPax:number; owner:string; region:string; origin:string };
export type Route = {id:string; origin:string; destination:string; country:string; region:string; tour:string; airline:string; cost:number; fare:number; pace:number};
export type Booking = {id:string;contractId:string;bookedAt:string;passengers:number;channel:string;airRevenue:number};
export type Market = {route:string;month:string;inbound:number;outbound:number;total:number};
export type Prediction = {route:string;month:string;forecast:number;lower:number;upper:number};
export type Backtest = {route:string;month:string;actual:number;forecast:number;baseline:number;trendForecast:number;absoluteError:number;split:string};
export type Score = {route:string;selectedModel:string;wape:number;baselineWape:number;trendWape:number;mae:number;testMonths:number;validationMonths:number;holdoutCoverage:number;bandWidth:number};
export type Portfolio = {asOf:string;marketThrough:string;routes:Route[];contracts:Contract[];bookings:Booking[];market:Market[];predictions:Prediction[];backtests:Backtest[];modelScores:Score[];priorYear:{contractId:string;bookedAtComparableLeadTime:number;revenue:number}[];quality:{rawRecords:number;acceptedRecords:number;quarantined:{record:string;rule:string;action:string;severity:string}[];marketRows:number;marketReconciled:boolean;missingMonths:number;duplicateMarketKeys:number;contractReconciled:boolean};provenance:{publisher:string;sourceUrl:string;downloadUrl:string;releaseDate:string;retrievedDate:string;sha256:string;measure:string;simulationSeed:number;rawMarketRows:number}};
export const sum=<T,>(rows:T[],f:(row:T)=>number)=>rows.reduce((a,r)=>a+f(r),0);
export const daysUntil=(value:string,asOf:string)=>Math.round((Date.parse(value+'T00:00:00Z')-Date.parse(asOf+'T00:00:00Z'))/86400000);
export const money=(value:number,compact=false)=>new Intl.NumberFormat('en-AU',{style:'currency',currency:'AUD',maximumFractionDigits:compact?2:0,...(compact?{notation:'compact' as const}: {})}).format(value);
export const number=(value:number)=>new Intl.NumberFormat('en-AU').format(Math.round(value));
export const shortDate=(value:string)=>new Date(value+'T00:00:00Z').toLocaleDateString('en-AU',{day:'numeric',month:'short',timeZone:'UTC'});
export const monthLabel=(value:string)=>new Date(value+'-01T00:00:00Z').toLocaleDateString('en-AU',{month:'short',year:'2-digit',timeZone:'UTC'});
export function recommend(c:Contract,asOf:string,uplift=0,buffer=2,releaseEnabled=true){
 const days=daysUntil(c.releaseDate,asOf);
 const demand=Math.max(c.booked,Math.round(c.forecastPax*(1+uplift/100)));
 const protectedSeats=Math.max(c.booked,c.minGroup,demand+buffer);
 const release=releaseEnabled&&days>=0?Math.max(0,Math.min(c.maxRelease,c.seats-protectedSeats)):0;
 const retained=c.seats-release;
 const served=Math.min(demand,retained);
 const margin=served*c.sellPrice-retained*c.unitCost-release*c.releaseFee;
 const baselineMargin=Math.min(demand,c.seats)*c.sellPrice-c.seats*c.unitCost;
 const status=days<0?'Deadline passed':days<=14&&release>0?'Review release':demand>=c.seats*.9?'Strong demand':release>0?'Monitor pace':'On track';
 return {days,demand,release,retained,served,margin,baselineMargin,benefit:margin-baselineMargin,unbooked:(c.seats-c.booked)*c.unitCost,exposure:Math.max(0,retained-served)*c.unitCost,missed:Math.max(0,demand-retained),status};
}
export function summarize(rows:Contract[],asOf:string){
 const seats=sum(rows,c=>c.seats),booked=sum(rows,c=>c.booked),forecast=sum(rows,c=>c.forecastPax);
 return {seats,booked,forecast,utilisation:seats?booked/seats*100:0,exposure:sum(rows,c=>(c.seats-c.booked)*c.unitCost),due:rows.filter(c=>{const d=daysUntil(c.releaseDate,asOf);return d>=0&&d<=14}).length,overdue:rows.filter(c=>daysUntil(c.releaseDate,asOf)<0).length,revenue:sum(rows,c=>c.booked*c.sellPrice),budget:sum(rows,c=>c.budgetPax*c.sellPrice),forecastRevenue:sum(rows,c=>c.forecastPax*c.sellPrice),benefit:sum(rows,c=>recommend(c,asOf).benefit)};
}
export function exportCsv(rows:Contract[],asOf:string){
 const columns=['Contract ID','Route','Tour','Departure','Release date','Seats','Booked','Forecast passengers','Booked utilisation %','Unbooked commitment AUD','Recommended release','Potential benefit AUD','Status','Owner','Provenance'];
 const values=rows.map(c=>{const r=recommend(c,asOf);return [c.id,c.route,c.tour,c.departure,c.releaseDate,c.seats,c.booked,c.forecastPax,(c.booked/c.seats*100).toFixed(1),r.unbooked,r.release,r.benefit,r.status,c.owner,'Simulated commercial record'];});
 const escape=(v:unknown)=>'"'+String(v).replace(/"/g,'""')+'"';
 return [columns,...values].map(row=>row.map(escape).join(',')).join('\r\n');
}
