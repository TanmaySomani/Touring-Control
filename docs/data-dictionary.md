# Data dictionary

| Dataset | Grain and key | Measure / provenance |
|---|---|---|
| BITRE source XLSX, Data sheet | AustralianPort × ForeignPort × Month | Reported inbound, outbound and total revenue passenger movements |
| market_actuals | route × YYYY-MM | Six selected city pairs, 42 months each, Jan 2023–Jun 2026 |
| market_forecasts | route × YYYY-MM | Jul 2026–Jun 2027 seasonal forecasts and indicative limits |
| forecast_backtest | route × month | Actual, selected forecast, trend forecast, baseline, absolute error and split |
| contracts | contract ID | One illustrative return-air block for one tour departure; not airline schedule data |
| bookings_raw | booking ID, before validation | Simulated passenger transaction feed with three seeded defects |
| bookings_clean | unique booking ID | Accepted confirmed passenger record, contract key, date, channel and air revenue |
| prior_year | current contract ID | Simulated equivalent departure and passenger count at comparable booking lead time |

All monetary amounts are Australian dollars, stored as numeric values. Unit air cost and air selling price are for one passenger's return-air component. Selling prices are allocations to the air component, not full tour package prices. Contract seats count return-air passenger capacity, avoiding double-counting outbound and return legs.

`releaseDate` is a simulated supplier deadline in calendar dates. `asOf` fixes the analytical snapshot. Browser timezones do not move these dates. A release is eligible on the deadline date under the model assumption; real cut-off times and supplier timezones would need to be captured.

`forecastPax` is derived from an assumed booking-completion curve. `forecastLow` and `forecastHigh` use an illustrative ±20% range capped to booked/contracted limits. These are separate from the empirically calibrated public-market error envelope.

`unbooked` is gross unsold seat commitment. `exposure` in the scenario result is the residual unused retained-seat cost at expected demand. Neither is a booked financial loss. `benefit` is an incremental air-contribution estimate compared with retaining all seats at the same scenario demand.

TYO and SEL are city-level labels; Tokyo/Seoul observations are not attributable to a specific airport. Singapore traffic may include onward travellers. Public monthly route totals have no customer, tour, sales-channel or contracted-allotment attribution.

The public source is linked and its original bytes are SHA-256 hashed in the JSON manifest. Commercial provenance is recorded as simulated. The snapshot and reproducibility seed are explicit. The database stores no personal information.
