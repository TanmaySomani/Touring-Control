# Touring Control

A commercial flight-inventory decision-support project built for an Inventory Coordinator application. It combines official Australian aviation statistics with an explicitly simulated touring operation.

**Business question:** Which contracted seats should a touring operator retain, release or escalate before supplier deadlines, and what is the commercial effect?

## What you can demonstrate

- A responsive six-view dashboard: overview, inventory, demand forecasting, scenario planning, data quality and methodology.
- 252 real route-month observations from BITRE, January 2023–June 2026, across six Australian international city pairs.
- 48 reproducible simulated return-air seat commitments, 1,632 seats and 748 passenger bookings.
- Release recommendations constrained by booked passengers, minimum group size, contract release allowance and deadline.
- Real model comparison, chronological validation and a separate holdout. Seasonal models win the validation comparison; their weaknesses remain visible.
- Formula-driven Excel reporting, filterable tables, CSV exports and SQLite commercial queries.
- Data-quality exceptions, grain checks, transaction-to-contract reconciliation and source provenance.

## Run the Streamlit dashboard

Python 3.12 is used for Streamlit Community Cloud. The public app runs from `streamlit_app.py` on the `main` branch.

```sh
python3 -m venv .streamlit-venv
.streamlit-venv/bin/python -m pip install -r requirements.txt
.streamlit-venv/bin/python -m streamlit run streamlit_app.py
```

The Streamlit version includes the same six analytical views, red theme, portfolio filters, inventory search, contract detail, market forecasts, scenario sliders, data controls and evidence downloads. Each visitor gets independent session controls; the app never changes airline inventory. Its Python commercial model is checked against the original TypeScript calculations across 864 contract/scenario combinations. Six tests also cover supplier deadline protection, retained capacity, weighted metrics, all six views and interactive demand/strategy changes.

```sh
.streamlit-venv/bin/python -m unittest tests/test_streamlit.py -v
```

This test command needs Node.js and the existing npm dependencies for the TypeScript parity check. Running the Streamlit app itself needs only the Python packages in `requirements.txt`.

[GitHub source](https://github.com/TanmaySomani/Touring-Control) · [Resume project wording](docs/resume-project.md)

## Run the React dashboard

Requirements: Node.js 22.13 or later and npm.

```sh
npm ci
npm run dev
```

Open the Local URL printed by the server. The dashboard uses a bundled snapshot, so browsing does not call airline APIs or need external data credentials.

```sh
npm run build
```

The included project starter builds a Cloudflare-compatible application. Hosting identity is managed in `.openai/hosting.json`; no source credentials are stored in the repository.

## Reproduce the data and forecasts

Requirements: Python 3.11 or later.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r analytics/requirements.txt
.venv/bin/python analytics/pipeline.py
.venv/bin/python analytics/test_pipeline.py
node --test tests/analytics.test.mjs
npx tsc --noEmit
```

The pinned original XLSX is in `data/raw/bitre-citypairs-jun2026.xlsx`. The pipeline reads the `Data` sheet, retains the six selected city pairs, checks uniqueness and passenger reconciliation, builds forecasts, simulates commercial sources with seed 417, quarantines invalid booking records and produces JSON, CSV and SQLite outputs.

To update the publication, replace the pinned source intentionally and update the source URL, reporting date, completeness range and documentation together. Re-running the existing script reproduces the October 2026 case study. There is no scheduled refresh or live connection.

## Evidence pack

- `docs/case-study.md`: business context, calculations, evidence and a pilot proposal.
- `docs/data-dictionary.md`: grains, units, definitions and limitations.
- `docs/interview-guide.md`: a five-minute demo and likely questions.
- `analytics/commercial.sql`: reusable route reporting and deadline queries.
- `public/reports/touring-control.xlsx`: Excel workbook with formulas, a chart, filterable tables and a SUMIFS route summary.
- `data/processed/inventory.sqlite`: reconciled commercial and market records.
- `data/processed/*`: source-like tables, cleaned records and forecast evidence.

The Excel workbook has live release formulas and editable demand/buffer inputs. Its tables support building PivotTables in Excel. It does not contain a native PivotTable. The workbook was calculated and rendered using the Codex spreadsheet engine; native Excel recalculation has not been tested.

## Data and affiliation

BITRE is the source of the public passenger data. Its city-pair statistics measure uplift/discharge traffic, which may include connecting traffic. They do not identify leisure travellers, tour purchasers, current seat availability or airline-specific contracted inventory. TYO and SEL represent city aggregates, not specific airports.

All contracts, departure schedules, carrier assignments, return air costs, selling prices, release terms, tour names, booking curves, budgets and prior-year commercial figures are simulated. Commercial results are illustrative and are not verified Flight Centre or My Touring savings. The project is independent and is not affiliated with or endorsed by either business.

## Technical structure

React and TypeScript handle the dashboard, Recharts renders data visualisations, and installed accessible UI primitives provide filters, tabs, sliders and the commitment drawer. Business logic lives in `lib/analytics.ts`. A Python ETL script creates the analytical snapshot and SQLite database. The Excel builder uses the Codex artifact library and is included in `.artifact-build/build-report.mjs` for the supported Codex runtime.

Optional browser WebMCP tools expose the same portfolio filters and scenario controls. They do not operate airline bookings. Local review annotations are saved to this browser only. The published dashboard is a snapshot prototype, not a production inventory system.

## Public research

1. [BITRE international airline activity time series](https://www.bitre.gov.au/resource/aviation/international-airline-activity-time-series-data), downloaded 9 October 2026; release 18 September 2026.
2. [My Touring](https://mytouring.com.au/), flight-inclusive touring products, reviewed 9 October 2026.
3. [Qantas group travel](https://www.qantas.com/en-au/book/flights/group-travel), group booking and deposit context, reviewed 9 October 2026. Dashboard rules do not reproduce these terms.

## Boundaries for a real implementation

Obtain real contract versions and fare rules, historical departure booking snapshots, cancellations and customer channel data. Add supplier reconciliation, separate outbound/inbound legs and tour bottleneck capacity, role-based approvals, durable audit records, refresh monitoring and finance reconciliation. Validate the booking curve and monetary assumptions against company data before recommending operational changes.
