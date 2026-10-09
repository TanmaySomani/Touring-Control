import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const root=path.resolve(import.meta.dirname,'..');
const output=path.join(root,'outputs/01a11f16-db0b-7011-89dc-64c020f54e2d');
await fs.mkdir(output,{recursive:true});
const p=JSON.parse(await fs.readFile(path.join(root,'public/data/portfolio.json'),'utf8'));
const wb=Workbook.create();
const sheets=Object.fromEntries(['Summary','Inventory','Market data','Forecast review','Bookings'].map(n=>[n,wb.worksheets.add(n)]));
const summary=sheets.Summary, inventory=sheets.Inventory, market=sheets['Market data'], review=sheets['Forecast review'], bookings=sheets.Bookings;
const money='"$"#,##0;("$"#,##0);"-"';
const body='#233e53',blue='#2463eb',green='#348267';
function setup(s,range){s.showGridLines=false;s.getRange(range).format.font={name:'Arial',size:10,color:body};s.getRange(range).format.rowHeight=22;s.getRange(range).format.verticalAlignment='center';}
function title(s,text,last){s.getRange('A2').values=[[text]];s.getRange('A2:'+last+'2').format.font={name:'Arial',size:16,bold:true,color:body};s.getRange('A2:'+last+'2').format.rowHeight=32;s.getRange('A2:'+last+'2').format.borders={bottom:{style:'thin',color:'#bccbda'}};}
function header(s,range){s.getRange(range).format={fill:'#193f58',font:{name:'Arial',size:10,bold:true,color:'#fff'},rowHeight:30,horizontalAlignment:'center',verticalAlignment:'center',wrapText:true};}
function formula(s,cell,text){s.getRange(cell).formulas=[[text]];}
const serial=d=>Math.round((Date.parse(d+'T00:00:00Z')-Date.UTC(1899,11,30))/86400000);
setup(inventory,'A1:AA56');title(inventory,'Flight inventory and release model','AA');
inventory.getRange('A3:B5').values=[['Reporting date',serial(p.asOf)],['Safety seats',2],['Demand change',0]];
inventory.getRange('B3').setNumberFormat('d-mmm-yyyy');inventory.getRange('B5').setNumberFormat('0.0%');
inventory.getRange('B4:B5').format.fill='#fff3cc';inventory.getRange('B3:B5').format.font={name:'Arial',size:10,color:blue};
inventory.getRange('D3').values=[['Commercial facts are simulated. All amounts are AUD.']];
inventory.getRange('D4').values=[['Yellow cells are editable. Recalculate after changes.']];
inventory.getRange('D5').values=[['Base forecast comes from an illustrative booking curve; it is not market traffic.']];
inventory.dataValidations.add({range:'B4',rule:{type:'whole',operator:'between',formula1:0,formula2:8}});
inventory.dataValidations.add({range:'B5',rule:{type:'decimal',operator:'between',formula1:-.35,formula2:.35}});
const invHeaders=['Contract ID','Route','Departure','Release date','Seats','Booked pax','Base forecast','Budget pax','Air cost AUD','Air price AUD','Release fee AUD','Release cap','Min group','Scenario demand','Days to release','Booked load','Unbooked AUD','Release seats','Retain seats','Served pax','Contribution AUD','Benefit AUD','Budget revenue AUD','Forecast revenue AUD','Variance AUD','Prior-year pax','Departure month'];
inventory.getRange('A8:AA56').values=[invHeaders,...p.contracts.map(c=>[c.id,c.route,serial(c.departure),serial(c.releaseDate),c.seats,null,c.forecastPax,c.budgetPax,c.unitCost,c.sellPrice,c.releaseFee,c.maxRelease,c.minGroup,null,null,null,null,null,null,null,null,null,null,null,null,p.priorYear.find(x=>x.contractId===c.id).bookedAtComparableLeadTime,serial(c.departure.slice(0,7)+'-01')])];
for(let r=9;r<=56;r++){
 const sourceFormulas={F:'=SUMIFS(\'Bookings\'!$D$6:$D$753,\'Bookings\'!$B$6:$B$753,A'+r+')',N:'=MAX(F'+r+',ROUND(G'+r+'*(1+$B$5),0))',O:'=D'+r+'-$B$3',P:'=F'+r+'/E'+r,Q:'=(E'+r+'-F'+r+')*I'+r,R:'=IF(O'+r+'<0,0,MAX(0,MIN(L'+r+',E'+r+'-MAX(F'+r+',M'+r+',N'+r+'+$B$4))))',S:'=E'+r+'-R'+r,T:'=MIN(N'+r+',S'+r+')',U:'=T'+r+'*J'+r+'-S'+r+'*I'+r+'-R'+r+'*K'+r,V:'=U'+r+'-(MIN(N'+r+',E'+r+')*J'+r+'-E'+r+'*I'+r+')',W:'=H'+r+'*J'+r,X:'=MIN(N'+r+',E'+r+')*J'+r,Y:'=X'+r+'-W'+r};
 for(const [col,f] of Object.entries(sourceFormulas))formula(inventory,col+r,f);
}
inventory.getRange('A8:AA56').format.columnWidth=14;inventory.getRange('C9:D56').setNumberFormat('d-mmm-yy');inventory.getRange('AA9:AA56').setNumberFormat('mmm-yy');
inventory.getRange('P9:P56').setNumberFormat('0.0%');
for(const col of ['I','J','K','Q','U','V','W','X','Y'])inventory.getRange(col+'9:'+col+'56').setNumberFormat(money);
inventory.getRange('A8:A56').format.columnWidth=17;inventory.getRange('N8:N56').format.columnWidth=18;inventory.getRange('U8:Y56').format.columnWidth=21;
inventory.getRange('E9:M56').format.font={name:'Arial',size:10,color:blue};
inventory.getRange('F9:F56').format.font={name:'Arial',size:10,color:green};
inventory.tables.add('A8:AA56',true,'InventoryModel');header(inventory,'A8:AA8');
inventory.freezePanes.freezeRows(8);inventory.freezePanes.freezeColumns(2);
inventory.getRange('O9:O56').conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{fill:'#ffebe8',font:{color:'#b65449',bold:true}}});
inventory.getRange('Y9:Y56').conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{font:{color:'#b65449'}}});
inventory.tabColor='#5c88b0';

setup(bookings,'A1:G753');title(bookings,'Accepted passenger booking records','G');
bookings.getRange('A3').values=[['Simulated passenger-level feed, accepted after ID, contract and snapshot-date validation.']];
bookings.getRange('A5:G753').values=[['Booking ID','Contract ID','Booking date','Passengers','Channel','Air revenue AUD','Provenance'],...p.bookings.map(b=>[b.id,b.contractId,serial(b.bookedAt),b.passengers,b.channel,b.airRevenue,'Simulated'])];
bookings.tables.add('A5:G753',true,'AcceptedBookings');header(bookings,'A5:G5');
bookings.getRange('A5:A753').format.columnWidth=27;bookings.getRange('B5:G753').format.columnWidth=19;bookings.getRange('C6:C753').setNumberFormat('d-mmm-yy');bookings.getRange('F6:F753').setNumberFormat(money);
bookings.freezePanes.freezeRows(5);bookings.freezePanes.freezeColumns(2);

setup(market,'A1:F257');title(market,'Real route passenger observations','F');
market.getRange('A3').values=[['Source: BITRE international airline activity, release 18 Sep 2026. '+p.provenance.sourceUrl]];
market.getRange('A4').values=[['Revenue passenger movements; uplift/discharge city pairs, all carriers. Outbound is not tourism-only demand.']];
market.getRange('A5:F257').values=[['Route','Month','Inbound pax','Outbound pax','Total pax','Provenance'],...p.market.map(m=>[m.route,serial(m.month+'-01'),m.inbound,m.outbound,m.total,'BITRE actual'])];
market.tables.add('A5:F257',true,'MarketActuals');header(market,'A5:F5');market.getRange('A5:F257').format.columnWidth=22;market.getRange('B6:B257').setNumberFormat('mmm-yy');market.getRange('C6:E257').setNumberFormat('#,##0');
market.freezePanes.freezeRows(5);market.freezePanes.freezeColumns(2);

setup(review,'A1:I118');title(review,'Market forecast validation and holdout','I');
review.getRange('A3').values=[['2025 validation selects the model; Jan–Jun 2026 holdout measures final accuracy. No future observations enter training.']];
review.getRange('A5:I113').values=[['Route','Month','Actual pax','Selected forecast','Trend forecast','Seasonal baseline','Absolute error','Split','Selected model'],...p.backtests.map(b=>[b.route,serial(b.month+'-01'),b.actual,b.forecast,b.trendForecast,b.baseline,null,b.split,p.modelScores.find(s=>s.route===b.route).selectedModel])];
for(let r=6;r<=113;r++)formula(review,'G'+r,'=ABS(C'+r+'-D'+r+')');
review.tables.add('A5:I113',true,'ForecastBacktest');header(review,'A5:I5');review.getRange('A5:I113').format.columnWidth=20;review.getRange('I5:I113').format.columnWidth=23;review.getRange('B6:B113').setNumberFormat('mmm-yy');review.getRange('C6:G113').setNumberFormat('#,##0');review.freezePanes.freezeRows(5);
review.getRange('K5:N11').values=[['Route','Holdout WAPE','Trend WAPE','Band coverage'],...p.modelScores.map(s=>[s.route,null,s.trendWape/100,s.holdoutCoverage/100])];
for(let r=6;r<=11;r++)formula(review,'L'+r,'=SUMIFS($G$6:$G$113,$A$6:$A$113,K'+r+',$H$6:$H$113,"holdout")/SUMIFS($C$6:$C$113,$A$6:$A$113,K'+r+',$H$6:$H$113,"holdout")');
review.getRange('K5:N11').format.columnWidth=19;review.getRange('L6:N11').setNumberFormat('0.0%');header(review,'K5:N5');

setup(summary,'A1:R36');title(summary,'Touring Control commercial report','H');summary.tabColor='#193f58';
summary.getRange('A3').values=[['Snapshot']];formula(summary,'B3',"='Inventory'!B3");summary.getRange('B3').setNumberFormat('d-mmm-yyyy');
summary.getRange('D3').values=[['All commercial records are simulated. Air component only. AUD.']];
summary.getRange('A5:B14').values=[['Metric','Portfolio value'],['Contracted seats',null],['Confirmed passengers',null],['Booked utilisation',null],['Forecast air revenue',null],['Budget air revenue',null],['Revenue variance',null],['Unbooked commitment',null],['Release seats',null],['Contribution improvement',null]];
const formulas={B6:"=SUM('Inventory'!E9:E56)",B7:"=SUM('Inventory'!F9:F56)",B8:'=B7/B6',B9:"=SUM('Inventory'!X9:X56)",B10:"=SUM('Inventory'!W9:W56)",B11:'=B9-B10',B12:"=SUM('Inventory'!Q9:Q56)",B13:"=SUM('Inventory'!R9:R56)",B14:"=SUM('Inventory'!V9:V56)"};
for(const [cell,f] of Object.entries(formulas))formula(summary,cell,f);
header(summary,'A5:B5');summary.getRange('B8').setNumberFormat('0.0%');summary.getRange('B9:B12').setNumberFormat(money);summary.getRange('B14').setNumberFormat(money);
summary.getRange('A18:H24').values=[['Route','Seat commitment','Booked pax','Booked load','Forecast pax','Forecast revenue','Budget revenue','Release benefit'],...p.routes.map(r=>[r.id,null,null,null,null,null,null,null])];
for(let r=19;r<=24;r++){
 for(const [out,col] of [['B','E'],['C','F'],['E','N'],['F','X'],['G','W'],['H','V']])formula(summary,out+r,"=SUMIFS('Inventory'!$"+col+"$9:$"+col+"$56,'Inventory'!$B$9:$B$56,$A"+r+')');
 formula(summary,'D'+r,'=C'+r+'/B'+r);
}
header(summary,'A18:H18');summary.getRange('D19:D24').setNumberFormat('0.0%');summary.getRange('F19:H24').setNumberFormat(money);
summary.getRange('A28:H34').values=[['Departure month','Seat commitment','Booked pax','Scenario demand','Forecast revenue','Budget revenue','Revenue variance','Release benefit'],...['2026-11','2026-12','2027-01','2027-02','2027-03','2027-04'].map(m=>[serial(m+'-01'),null,null,null,null,null,null,null])];
for(let r=29;r<=34;r++){
 for(const [out,col] of [['B','E'],['C','F'],['D','N'],['E','X'],['F','W'],['G','Y'],['H','V']])formula(summary,out+r,"=SUMIFS('Inventory'!$"+col+"$9:$"+col+"$56,'Inventory'!$AA$9:$AA$56,$A"+r+')');
}
header(summary,'A28:H28');summary.getRange('A29:A34').setNumberFormat('mmm-yy');summary.getRange('E29:H34').setNumberFormat(money);
summary.getRange('A5:A14').format.columnWidth=31;summary.getRange('B5:B14').format.columnWidth=21;summary.getRange('C5:H34').format.columnWidth=20;
summary.getRange('D5:H14').format.columnWidth=18;
summary.getRange('A16').values=[['Route summary uses SUMIFS. Inventory and source sheets are filterable and ready for PivotTables.']];
summary.getRange('A36').values=[['Unbooked commitment is gross seat cost, not a realised loss. Scenario benefit requires verified contract terms.']];
const chart=summary.charts.add('bar',summary.getRange('A18:C24'));
chart.title='Seat commitment and bookings by route';chart.titleTextStyle.typeface='Arial';chart.titleTextStyle.fontSize=13;
chart.legend={position:'top',textStyle:{typeface:'Arial',fontSize:11}};
chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};
chart.yAxis={numberFormatCode:'#,##0',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};
chart.series.items[0].fill='#b6ccec';chart.series.items[1].fill='#2463eb';chart.setPosition('D5','I15');
wb.recalculate();
const base=summary.getRange('B6:B14').values.map(r=>r[0]);
if(base[0]!==1632||base[1]!==748)throw new Error('Source reconciliation failed: '+JSON.stringify(base));
const previousBenefit=summary.getRange('B14').values[0][0];
inventory.getRange('B5').values=[[.35]];wb.recalculate();
const higherDemandBenefit=summary.getRange('B14').values[0][0];
if(!(higherDemandBenefit<previousBenefit))throw new Error('Demand change did not reduce release benefit');
inventory.getRange('B5').values=[[0]];wb.recalculate();
console.log(JSON.stringify({base,benefit:previousBenefit,higherDemandBenefit}));
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},summary:'Formula error scan'});
console.log(errors.ndjson);
for(const [name,range] of [['Summary','A1:I36'],['Inventory','A1:S14'],['Market data','A1:F14'],['Forecast review','A1:N14'],['Bookings','A1:G14']]){
 const image=await wb.render({sheetName:name,range,scale:1,format:'png'});
 await fs.writeFile(path.join(output,name.replaceAll(' ','-')+'.png'),new Uint8Array(await image.arrayBuffer()));
}
console.log((await wb.inspect({kind:'table',range:'Summary!A5:B14',include:'values,formulas',tableMaxRows:10,tableMaxCols:2,maxChars:1800})).ndjson);
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(path.join(output,'touring-control.xlsx'));
await fs.copyFile(path.join(output,'touring-control.xlsx'),path.join(root,'public/reports/touring-control.xlsx'));
console.log('Saved reporting pack');
