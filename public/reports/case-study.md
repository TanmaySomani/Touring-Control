# Touring Control: contracted flight inventory for a touring operator

## The problem and why it matters

My Touring sells touring holidays that can include flights, accommodation and guided travel. An inventory coordinator needs to reconcile commitments and sales across these components. The flight component is a useful project boundary because a seat is tied to a departure date and supplier terms, while sales develop over a booking window. [My Touring product context](https://mytouring.com.au/).

Group airline arrangements can involve deposits and conditions when group size changes. The precise commercial consequence depends on the fare and supplier agreement. This supports monitoring commitments and deadlines; it does not establish that the simulated rules in this project apply to Flight Centre or any particular carrier. [Qantas group travel](https://www.qantas.com/en-au/book/flights/group-travel).

The operational failure this project addresses is delayed visibility: contract commitments, booking loads and release dates can be difficult to reconcile across spreadsheets and sales systems. A weak-selling departure may retain unnecessary seat cost after a deadline. Releasing too many seats can constrain a strong-selling tour. The decision needs both passenger demand and commercial terms.

**Decision:** Which seat commitments should be retained, released or escalated, and what contribution difference follows under explicit assumptions?

## Project scope and evidence

The reporting snapshot is 9 October 2026. Official BITRE observations cover January 2023–June 2026 for Brisbane–Auckland, Sydney–Tokyo, Brisbane–Tokyo, Melbourne–Ho Chi Minh City, Sydney–Seoul and Melbourne–Singapore. The source is the June 2026 city-pair XLSX released on 18 September 2026. [BITRE publication](https://www.bitre.gov.au/resource/aviation/international-airline-activity-time-series-data).

These 252 observations are genuine monthly revenue passenger movements. The outbound measure reflects uplift/discharge traffic across all carriers, may include connecting traffic, and is not tourism-only demand or tour sales. The data is several months behind the project snapshot. July–September estimates must not be presented as observed actuals.

Private commercial facts are unavailable. A fixed seed creates 48 illustrative return-air commitments, 1,632 seats and 748 passenger bookings. Budgets, comparable prior-year loads, carriers, prices, group minima, release caps and fees are simulated. The tour names and departure schedules are fictional. All commercial dashboard results are labelled accordingly.

## The solution

The dashboard starts with a commercial operating view: weighted booked utilisation, gross unbooked commitment, upcoming deadlines, forecast revenue against budget, urgent commitments and route-level booking pace. Filters provide a region, origin and departure-horizon view without changing metric definitions.

An inventory table connects contract IDs, tour names, departure dates, release dates, booked and forecast loads, unsold seat cost and a review status. The commitment drawer explains a recommendation and exposes its cost assumptions, owner and channel mix. Local review flags support demonstration; they are not durable enterprise approvals.

The demand view shows official market actuals, a forecast and accuracy evidence. The scenario planner tests demand changes from −35% to +35%, a zero-to-eight-seat buffer, and retaining versus releasing eligible seats. Each scenario recomputes commercial contribution and displays demand exceeding retained capacity.

The quality view shows source lineage and deliberately seeded defects: a duplicate booking, an orphaned contract reference and a booking after the snapshot. The ETL quarantines them instead of letting them distort reported passenger loads. CSV, SQLite and Excel reports make the logic inspectable outside the UI.

## Analytical definitions

| Measure | Calculation | Interpretation |
|---|---|---|
| Booked utilisation | Confirmed passengers / contracted seats | Weighted across the same filtered departures |
| Gross unbooked commitment | (Seats − booked passengers) × air cost | Exposure to committed unsold seat cost, not a realised loss |
| Base departure forecast | Booked passengers / lead-time booking fraction, rounded and capped | Uses an illustrative curve, not a validated company model |
| Revenue variance | Forecast air revenue − budget air revenue | Same departure portfolio and assumed air selling price |
| Prior-year booking comparison | Current booked pax / comparable lead-time prior pax − 1 | Both commercial series are simulated |
| Eligible release | Seats less protected demand, capped by allowance | Only when release date has not passed |
| Air contribution | Served pax × price − retained seats × cost − releases × fee | Excludes land costs, marketing and overheads |
| Scenario benefit | Scenario contribution − contribution retaining all seats | Same demand assumption on both sides |

Booking-curve knots are 100% at departure, 94% at 30 days, 79% at 60 days, 64% at 90 days, 48% at 120 days, 26% at 180 days and 14% at 240 days. Intermediate lead times use linear interpolation. A real pilot must estimate these curves from historical snapshots and account for cancellations and promotions.

The simulated contracts permit release of at most 50% of committed seats, keep a minimum group of ten, close the release window 45 days before departure and charge a release fee of approximately 12% of air cost, rounded to a whole AUD amount. These are case-study assumptions, not published rules for the named airlines.

Protected seats are the maximum of confirmed passengers, group minimum and adjusted expected demand plus the safety buffer. Release seats are the nonnegative difference between commitment and protected seats, capped by the release allowance. Once the deadline passes, the model permits no release and recommends escalation instead.

## Forecast design and what the evidence says

The public market model compares a seasonal baseline with a trend-adjusted seasonal baseline. The seasonal reference is the same month in the previous year. The trend multiplier is the mean year-on-year ratio from the last six observed months, clipped to 0.8–1.2.

January 2023–December 2024 supplies initial history. Each 2025 validation prediction uses only preceding observations. The lower validation absolute error selects the model per route. January–June 2026 is a separate holdout; it does not choose the model. Final July 2026–June 2027 forecasts use only observations through June 2026.

All six routes select the seasonal baseline. Holdout WAPE ranges from 4.8% to 8.9%. The trend model sometimes performs better on the later holdout, but that information is not used retroactively to change the validation choice. This demonstrates why model selection must be chronological and why a useful baseline should be retained.

An indicative envelope uses the 80th percentile of validation absolute relative errors. Its six-month holdout coverage ranges from 50% to 100% by route. It is not a proven 80% confidence interval. Aggregate chart bands sum route bounds without modelling correlations. Low coverage is a signal to widen operational buffers and improve uncertainty modelling.

The public model and contract booking model answer different questions. Market passenger volumes are not converted into tour bookings. The project avoids pretending that all international passengers are customers of one travel brand.

## Example decision

The first Brisbane–Tokyo commitment departs 24 November 2026 and has a release deadline of 10 October. It has 36 contracted seats and 17 confirmed passengers. The illustrative base forecast is 20 passengers. Protecting 20 passengers plus two safety seats produces a recommendation to review releasing 14 seats.

At an assumed return air cost of AUD 1,490 and a release fee of AUD 179 per seat, the contribution difference from retaining all seats is 14 × (1,490 − 179) = AUD 18,354. The scenario preserves forecast demand. This is an arithmetic estimate under simulated terms, not verified savings. The actual supplier contract and Product Manager approval are prerequisites for action.

## Stakeholder workflow

| Team | What the project provides | Decision or input |
|---|---|---|
| Product | Departure-level capacity, booking pace and release suggestions | Validate supplier terms and approve inventory changes |
| Commercial | Contribution and sensitivity comparisons | Assess margin/capacity trade-offs |
| Sales | Low-load departures and channel mix | Consider targeted promotion; promotion uplift requires evidence |
| Finance | Air revenue/budget reporting and cost reconciliation | Verify cost basis, revenue allocation and liability treatment |
| Operations | Expected passenger load and group limits | Confirm tour-operating feasibility and multi-leg constraints |
| Inventory coordinator | Shared reporting, deadlines and exceptions | Maintain records, communicate recommendations and track review |

## What would make this production-ready

Start with a six-week pilot using historical company data. Map unique tour departures to actual outbound/inbound supplier segments and contract versions. Match confirmed, cancelled and provisional bookings. Reconcile supplier balances and finance reports independently.

Train lead-time booking curves by product, route, season and channel. Include cancellations, promotional changes, demand censoring and tour minimum viability. Backtest forecasts chronologically and evaluate both point error and interval coverage. Account for the weakest leg and the availability of accommodation or land components.

Introduce role-based access, durable review/approval logs, automated refresh jobs, exception ownership and stale-data alerts. The current snapshot is independent of these enterprise services and does not operate airline bookings.

Measure on-time release reviews, avoidable expired seat cost, missed sales due to capacity shortage, forecast error and report preparation time against a pre-pilot baseline. Do not claim commercial savings until the baseline, contract terms and observed post-decision outcomes are verified.

## Validation

The project includes tests for booking reconciliation, route-month uniqueness/completeness, passenger arithmetic, forecast split integrity, deadline boundaries, release caps, sold-passenger protection, group minima, demand/buffer monotonicity, contribution formulas and CSV exports. The Excel pack is recalculated and checked after an input change. The browser controls, detail drawer and responsive views are tested during build.
