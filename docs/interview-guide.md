# Five-minute interview demonstration

1. **Problem, 45 seconds:** Explain the trade-off between committed seat cost and uncertain touring sales. Show how missed release windows can turn unsold seats into avoidable cost.
2. **Overview, 60 seconds:** Explain weighted utilisation, gross unbooked commitment and forecast revenue versus budget. Filter to Brisbane for a Product Manager view.
3. **Inventory review, 60 seconds:** Open the first BNE–TYO departure. Walk through the bookings, deadline, protected passenger demand, proposed release and fee assumptions. State that the decision belongs to Product.
4. **Forecast evidence, 60 seconds:** Show genuine market observations, baseline versus trend, validation versus holdout, WAPE and uncertainty coverage. Explain why market traffic is not company demand.
5. **Scenario and controls, 75 seconds:** Increase demand and watch releases fall. Show a booking exception and the Excel formulas. Explain the company data needed for a pilot.

## Questions to prepare for

**Is this real Flight Centre data?**

No. The passenger movements are official BITRE observations. Contracts, bookings, fares and commercial results are simulated. The project demonstrates a decision process without claiming access to private records.

**Why did you choose a seasonal baseline?**

It beat the trend-adjusted alternative on chronological 2025 validation for all six selected routes. I then reported performance on a separate six-month holdout. A more complex model should earn its place through measured results.

**Is the unbooked commitment the loss?**

No. It is the gross air cost of unsold committed seats at the snapshot. More passengers may book, and actual loss depends on supplier terms. The planner compares contribution under explicit demand and release assumptions.

**How would you validate release recommendations?**

Reconcile real booking loads and supplier contract versions, estimate booking curves from historical snapshots, capture deadlines and timezones, and compare observed results against a retained-seat baseline. Verify multi-leg and land inventory constraints before approval.

**How does the Excel report update?**

Bookings roll into the inventory model through SUMIFS keyed on contract ID. Formulas calculate demand, days to release, protected capacity, releases and contribution. Summary formulas aggregate by route and month. Demand/buffer inputs recalculate the same build. Tables are ready for PivotTables; the file contains a formula route summary, not a native pivot.

**What would you improve next?**

Use real cancellation and promotion histories, learn product-specific booking curves, estimate better uncertainty intervals, add supplier/finance reconciliation, and build durable approval/audit workflows. Measure report preparation time and deadline review completion before commercial ROI.

## Portfolio wording

Designed a commercial flight-inventory analytics prototype combining official Australian route statistics with a reproducible simulated touring portfolio. Built chronological forecast validation, contract-constrained release scenarios, passenger-to-inventory reconciliation, and an interactive responsive dashboard with Excel, CSV and SQL reporting.

Do not describe illustrative scenario benefits as achieved business savings or describe the prototype as a live Flight Centre system.
