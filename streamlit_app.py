"""Touring Control: a public, interactive commercial inventory portfolio project."""

from html import escape
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from analytics.streamlit_model import ROOT, load_portfolio, filter_contracts, inventory_records, recommend, summarize


st.set_page_config(page_title="Touring Control | Flight Inventory Intelligence", page_icon="✈️", layout="wide")
RED, ROSE, INK, GREEN = "#d71920", "#f0a8ae", "#253746", "#238773"
VIEWS = ["Overview", "Flight inventory", "Demand forecast", "Scenario planner", "Data quality", "Project & methodology"]

st.html("""
<style>
.stApp {background:#f5f7fa}
.block-container,[data-testid="stMainBlockContainer"] {padding:2rem;max-width:1500px}
h1,h2,h3 {letter-spacing:-.04em}
h1 {font-size:2.25rem!important;font-weight:750!important}
h2 {font-size:1.35rem!important}
h3 {font-size:1.25rem!important}
[data-testid="stSidebar"] {background:#bd131a;color:white}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {color:white!important}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color:#ffe2e4!important}
[data-testid="stSidebar"] [data-baseweb="select"] {color:#253746}
[data-testid="stSidebar"] [data-testid="stLinkButton"] p {color:#253746!important}
[data-testid="stSidebar"] [data-testid="stRadio"] label {padding:.45rem .6rem;border-radius:7px;margin:2px 0}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {background:#9e1016}
[data-testid="stMetric"] {background:white;border:1px solid #e3e8ef;border-radius:12px;padding:18px 20px;min-height:132px}
[data-testid="stMetricValue"] {font-size:2rem!important;font-weight:700;letter-spacing:-.04em}
[data-testid="stMetricLabel"] {color:#667b8b;font-size:.9rem}
[data-testid="stMetricLabel"] * {white-space:normal!important;text-overflow:clip!important;overflow:visible!important}
.eyebrow {color:#af1118;font-size:.75rem;letter-spacing:.13em;font-weight:700;margin-bottom:8px}
.subtitle {color:#667b8b;line-height:1.7;margin-bottom:24px}
.callout {background:#fff0f1;border:1px solid #f3d1d5;border-radius:12px;padding:24px;height:100%}
.callout h3 {font-size:1.65rem!important;margin-top:5px;color:#253746}
.callout p {color:#77535a;font-size:.95rem;line-height:1.7}
.callout .value {font-size:2rem;color:#af1118;font-weight:750}
.sidebar-brand {font-size:1.8rem;font-weight:750;line-height:1.05;color:white;margin:12px 0 25px}
.sidebar-brand span {display:block;font-weight:400;color:#ffe2e4}
.sidebar-note {color:white;font-size:1.25rem;line-height:1.6;margin:30px 0 15px}
.evidence {background:#fff0f1;border:1px solid #f3d1d5;padding:14px 18px;border-radius:9px;color:#9f1820;margin-bottom:22px}
.project-brief {display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:16px;margin:6px 0 20px}
.project-brief article {background:white;border:1px solid #e3e8ef;border-top:3px solid #d71920;border-radius:10px;padding:18px 20px}
.project-brief h2 {font-size:1.05rem!important;letter-spacing:-.02em;margin:0 0 8px;color:#253746}
.project-brief p {font-size:.9rem;line-height:1.6;color:#536979;margin:0}
.project-decision {grid-column:1/-1;color:#9f1820;font-size:.9rem;line-height:1.6;background:#fff0f1;border-radius:8px;padding:12px 18px}
@media(max-width:1100px){
[data-testid="stHorizontalBlock"]{flex-wrap:wrap}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{min-width:100%!important;flex:1 1 100%!important}
.st-key-top_metrics [data-testid="stColumn"]{min-width:calc(50% - .75rem)!important;flex:1 1 calc(50% - .75rem)!important}}
@media(max-width:640px){h1{font-size:1.8rem!important}.block-container,[data-testid="stMainBlockContainer"]{padding:1.25rem 1rem}
[data-testid="stHorizontalBlock"]{flex-wrap:wrap}
[data-testid="stHorizontalBlock"]>[data-testid="stColumn"],.st-key-top_metrics [data-testid="stColumn"]{min-width:100%!important;flex:1 1 100%!important}
[data-testid="stMetric"]{min-height:112px}}
</style>
""")


@st.cache_data
def get_data():
    return load_portfolio()


def cash(value, compact=False):
    if compact and abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    if compact and abs(value) >= 1000:
        return f"${value / 1000:,.1f}K"
    return f"${value:,.0f}"


def metric_columns():
    with st.container(key="top_metrics"):
        return st.columns(4)


def chart(fig, key):
    fig.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Arial, sans-serif", color="#667b8b", size=12),
                      margin=dict(l=10, r=15, t=15, b=15), height=320,
                      legend=dict(orientation="h", y=-.15, x=0), hovermode="x unified")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#edf1f5", zeroline=False)
    st.plotly_chart(fig, width="stretch", key=key, config={"displaylogo": False})


def table(frame, key=None):
    st.dataframe(frame, width="stretch", hide_index=True, key=key,
                 column_config={"Booked utilisation %": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.1f%%")})


def display_inventory(frame):
    columns = {"id": "Contract", "route": "Route", "tour": "Tour", "departure": "Departure", "releaseDate": "Release deadline",
               "seats": "Seats", "booked": "Booked", "forecastPax": "Forecast passengers", "days": "Days to release",
               "release": "Recommended release", "benefit": "Potential benefit AUD", "status": "Status", "owner": "Product owner"}
    result = frame[list(columns)].rename(columns=columns).copy()
    result["Booked utilisation %"] = frame["booked"].values / frame["seats"].values * 100
    return result


def csv_download(frame, label, filename, key):
    st.download_button(label, frame.to_csv(index=False).encode("utf-8"), filename, "text/csv", key=key, width="stretch")


def project_brief():
    st.html("""
    <section class="project-brief" aria-label="Project problem and solution">
      <article>
        <h2>Problem statement</h2>
        <p>Flight-inclusive tours commit airline seats before customer demand is certain.
        Unsold seats can become a cost if supplier release deadlines are missed;
        releasing too early can leave a successful tour short of capacity.</p>
      </article>
      <article>
        <h2>What this dashboard solves</h2>
        <p>Touring Control brings bookings, contracted seats, deadlines and forecasts into one view.
        Identify departures at risk, test demand scenarios and compare the commercial trade-off
        before a Product Manager decides what to retain, release or escalate.</p>
      </article>
      <div class="project-decision"><strong>The decision:</strong> Which seats should we keep,
      release or escalate before the supplier deadline?</div>
    </section>
    """)


data = get_data()
as_of = data["asOf"]
with st.sidebar:
    st.html('<div class="sidebar-brand">✈ touring<span>control</span></div>')
    st.caption("COMMERCIAL WORKSPACE")
    view = st.radio("Workspace", VIEWS, label_visibility="collapsed", key="view")
    st.divider()
    region = st.selectbox("Region", ["All regions", "Asia", "Oceania"], key="region")
    origin = st.selectbox("Departure city", ["All origins", "Brisbane", "Sydney", "Melbourne"], key="origin")
    horizon = st.selectbox("Departure horizon", ["All departures", "Next 60 days", "Next 120 days"], key="horizon")
    st.html('<div class="sidebar-note">The right seats.<br>The right time.<br>Less exposure.</div>')
    st.caption("Independent portfolio project\n\nSnapshot: 9 October 2026 · AUD")
    st.link_button("View source on GitHub", "https://github.com/TanmaySomani/Touring-Control", width="stretch")

contracts = filter_contracts(data["contracts"], as_of, region, origin, horizon)
totals = summarize(contracts, as_of)
records = inventory_records(contracts, as_of)
frame = pd.DataFrame(records)
route_ids = sorted({c["route"] for c in contracts})
st.html('<div class="eyebrow">MY TOURING CASE STUDY · COMMERCIAL INTELLIGENCE</div>')
st.title("Every seat. A smarter decision." if view == "Overview" else view)
st.html('<p class="subtitle">Stay ahead of demand, supplier release deadlines and commercial exposure.</p>')
st.caption("Real BITRE market statistics · Simulated contracts and commercial results · AUD · Fixed October 2026 snapshot")
if view in ["Overview", "Project & methodology"]:
    project_brief()
if not contracts:
    st.info("No departures match these filters. Choose another region, departure city or horizon in the sidebar.")
    st.stop()


if view == "Overview":
    metrics = metric_columns()
    metrics[0].metric("Contracted seats", f"{totals['seats']:,}", help=f"{len(contracts)} simulated upcoming departures")
    metrics[1].metric("Booked utilisation", f"{totals['utilisation']:.1f}%", help="Total booked passengers ÷ total contracted seats")
    metrics[2].metric("Unbooked commitment", cash(totals["exposure"], True), help="Gross cost of unsold seats; not a realised loss")
    metrics[3].metric("Upcoming release windows", totals["due"], help=f"Due within 14 days; {totals['overdue']} deadlines have passed")
    st.write("")
    left, right = st.columns([1.7, 1])
    with left, st.container(border=True):
        st.subheader("Bookings meet commitments")
        st.caption("Passenger position by departure month · simulated portfolio")
        monthly = frame.assign(month=pd.to_datetime(frame["departure"]).dt.to_period("M").astype(str)).groupby("month")[["booked", "forecastPax", "seats"]].sum()
        labels = pd.to_datetime(monthly.index).strftime("%b %y")
        fig = go.Figure()
        fig.add_bar(x=labels, y=monthly["booked"], name="Booked", marker_color=RED)
        fig.add_bar(x=labels, y=monthly["forecastPax"], name="Forecast", marker_color=ROSE)
        fig.add_scatter(x=labels, y=monthly["seats"], name="Committed", line=dict(color=INK, dash="dash"))
        chart(fig, "overview_chart")
        st.caption("Touring forecasts use an illustrative booking curve. The public market forecast is a separate model.")
    with right:
        candidates = [r for r in records if r["release"] > 0]
        if candidates:
            best = max(candidates, key=lambda r: r["benefit"])
            st.html(f'<div class="callout"><div class="eyebrow">NEXT COMMERCIAL REVIEW</div><h3>Make room for a better outcome.</h3><p>Review <b>{escape(best["route"])}</b>, departing {best["departure"]}. The base case suggests releasing <b>{best["release"]} seats</b> while preserving a two-seat safety buffer.</p><div class="value">{cash(best["benefit"])}</div><p>Illustrative contribution improvement. Product Manager approval and actual supplier terms are required before execution.</p></div>')
        else:
            st.info("No release recommendation is available for this filtered portfolio.")
    left, right = st.columns([1.4, 1])
    with left, st.container(border=True):
        st.subheader("Attention before the deadline")
        attention = frame[(frame["days"] < 0) | ((frame["days"] <= 14) & (frame["release"] > 0))].sort_values("days")
        st.caption(f"{len(attention)} commitments need a closer look")
        table(attention[["id", "route", "releaseDate", "days", "booked", "seats", "status"]])
    with right, st.container(border=True):
        st.subheader("Commercial position")
        st.metric("Forecast air revenue", cash(totals["forecastRevenue"], True))
        st.caption(f"Budget {cash(totals['budget'])} · Variance {cash(totals['forecastRevenue'] - totals['budget'])}")
        st.progress(min(1.0, totals["forecastRevenue"] / totals["budget"]))
        st.write(f"Potential release benefit: **{cash(totals['benefit'])}**")
        comparable = sum(p["bookedAtComparableLeadTime"] for p in data["priorYear"] if p["contractId"] in frame["id"].values)
        st.caption(f"{(totals['booked'] / comparable - 1) * 100:+.1f}% booked passengers vs simulated prior year at the same lead time. Air component only; excludes land costs and overheads.")
    with st.container(border=True):
        st.subheader("Route performance at a glance")
        routes = frame.groupby("route")[["seats", "booked", "forecastPax", "unbooked"]].sum().reset_index()
        routes["Booked utilisation %"] = routes["booked"] / routes["seats"] * 100
        table(routes.rename(columns={"route": "Route", "seats": "Seats", "booked": "Booked", "forecastPax": "Forecast passengers", "unbooked": "Unbooked commitment AUD"}))
    csv_download(display_inventory(frame), "Download filtered inventory CSV", "touring-control-inventory.csv", "overview_csv")

elif view == "Flight inventory":
    search = st.text_input("Search contract, route, tour or airline", placeholder="Try BNE-TYO or Tokyo", key="inventory_search")
    risk = st.selectbox("Inventory status", ["All commitments", "Release due in 14 days", "Deadline passed", "Release recommended"], key="risk")
    filtered = frame.copy()
    if search:
        matching = filtered[["id", "route", "tour", "airline"]].astype(str).agg(" ".join, axis=1).str.contains(search, case=False, regex=False)
        filtered = filtered[matching]
    if risk == "Release due in 14 days":
        filtered = filtered[filtered["days"].between(0, 14)]
    elif risk == "Deadline passed":
        filtered = filtered[filtered["days"] < 0]
    elif risk == "Release recommended":
        filtered = filtered[filtered["release"] > 0]
    filtered = filtered.sort_values("releaseDate")
    st.caption(f"{len(filtered)} of {len(frame)} filtered commitments · Review flags last only for this session")
    table(display_inventory(filtered), "inventory_table")
    csv_download(display_inventory(filtered), "Download this inventory view", "touring-control-inventory.csv", "inventory_csv")
    if not filtered.empty:
        selected_id = st.selectbox("Inspect a commitment", filtered["id"].tolist(), key="selected_contract")
        selected = next(c for c in contracts if c["id"] == selected_id)
        decision = recommend(selected, as_of)
        with st.container(border=True):
            st.subheader(f"{selected['route']} · {selected['tour']}")
            st.caption(f"{selected['airline']} · Departure {selected['departure']} · Supplier deadline {selected['releaseDate']}")
            columns = st.columns(3)
            columns[0].metric("Booked / contracted", f"{selected['booked']} / {selected['seats']}")
            columns[1].metric("Recommended release", decision["release"])
            columns[2].metric("Potential benefit", cash(decision["benefit"]))
            st.write(f"Forecast **{selected['forecastPax']}** passengers; indicative booking-curve range **{selected['forecastLow']}–{selected['forecastHigh']}**. Retain **{decision['retained']}** seats. Minimum group **{selected['minGroup']}**; maximum release **{selected['maxRelease']}**.")
            st.caption(f"Return air cost {cash(selected['unitCost'])}/seat · Selling price {cash(selected['sellPrice'])}/passenger · Assumed release fee {cash(selected['releaseFee'])}/seat · Product owner {selected['owner']}")
            if decision["days"] < 0:
                st.warning("The release deadline has passed. Escalate to the Product Manager; the model blocks seat releases.")
            st.checkbox("Reviewed in this browser session", key=f"reviewed_{selected_id}")
            st.caption("This flag is a local review aid and never changes airline inventory or creates a shared audit record.")

elif view == "Demand forecast":
    st.html('<div class="evidence"><b>Official BITRE actuals through June 2026.</b> Downloaded release: 18 September 2026. Later months are model estimates at this snapshot.</div>')
    selected_route = st.selectbox("Market route", ["All filtered routes"] + route_ids, key="market_route")
    active = route_ids if selected_route == "All filtered routes" else [selected_route]
    market = pd.DataFrame(data["market"]).query("route in @active")
    predictions = pd.DataFrame(data["predictions"]).query("route in @active")
    backtests = pd.DataFrame(data["backtests"]).query("route in @active")
    holdout = backtests[backtests["split"] == "holdout"]
    wape = holdout["absoluteError"].sum() / holdout["actual"].sum() * 100
    metrics = metric_columns()
    for col, label, value in zip(metrics, ["Holdout forecast error", "Real route observations", "Forecast horizon", "Selected model"], [f"{wape:.1f}% WAPE", str(len(market)), "12 months", "Seasonal"]):
        col.metric(label, value)
    with st.container(border=True):
        st.subheader("Where demand is heading")
        actual = market[market["month"] >= "2025-01"].groupby("month")["outbound"].sum()
        future = predictions.groupby("month")[["forecast", "lower", "upper"]].sum()
        fig = go.Figure()
        fig.add_scatter(x=future.index, y=future["upper"], line=dict(width=0), showlegend=False, hoverinfo="skip")
        fig.add_scatter(x=future.index, y=future["lower"], fill="tonexty", fillcolor="rgba(215,25,32,.12)", line=dict(width=0), name="Indicative error envelope")
        fig.add_scatter(x=actual.index, y=actual, name="Actual", line=dict(color=RED, width=2.5))
        fig.add_scatter(x=[actual.index[-1]] + future.index.tolist(), y=[actual.iloc[-1]] + future["forecast"].tolist(), name="Forecast", line=dict(color=GREEN, width=2.5, dash="dash"))
        chart(fig, "market_chart")
        st.caption("Outbound passenger movements across all carriers. Not tourism-only demand, airline seat availability or My Touring sales. Aggregate envelopes sum route limits without modelling correlation.")
    with st.container(border=True):
        st.subheader("Accuracy you can inspect")
        scores = pd.DataFrame(data["modelScores"]).query("route in @active")
        table(scores[["route", "selectedModel", "wape", "trendWape", "holdoutCoverage"]].rename(columns={"route": "Route", "selectedModel": "Selected model", "wape": "Selected holdout WAPE %", "trendWape": "Trend holdout WAPE %", "holdoutCoverage": "Envelope coverage %"}))
        st.info("Models were selected using 12 rolling 2025 validation months, then tested on six unseen Jan–Jun 2026 months. The seasonal baseline won validation for all six routes. Low envelope coverage means some ranges are too narrow; this is not a guaranteed confidence interval.")
    with st.container(border=True):
        st.subheader("The seasonality signal")
        observed = market[market["month"].str.startswith("2025")].copy()
        observed["ratio"] = observed["outbound"] / observed.groupby("route")["outbound"].transform("mean")
        observed["month_number"] = observed["month"].str[-2:].astype(int)
        heat = observed.pivot(index="route", columns="month_number", values="ratio")
        fig = go.Figure(go.Heatmap(z=heat.values, x=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], y=heat.index,
                                  colorscale=[[0, "#fff5f5"], [1, "#d71920"]], text=heat.round(1).astype(str).values, texttemplate="%{text}", hovertemplate="%{y} · %{x}: %{z:.2f}× route mean<extra></extra>", colorbar=dict(title="× mean")))
        chart(fig, "seasonality_chart")
        st.caption("1.2 means demand was 20% above that route's 2025 monthly mean. This does not establish a touring conversion rate.")
    col1, col2 = st.columns(2)
    with col1:
        csv_download(market, "Download actual market data", "market_actuals.csv", "actuals_csv")
    with col2:
        csv_download(backtests, "Download forecast validation", "forecast_backtest.csv", "backtests_csv")
    st.link_button("Official BITRE source", data["provenance"]["sourceUrl"])

elif view == "Scenario planner":
    left, right = st.columns([1, 1.7])
    with left, st.container(border=True):
        st.subheader("Challenge the base case")
        st.write("Change expected demand and the safety buffer to see the effect on capacity and contribution.")
        uplift = st.slider("Demand change (%)", -35, 35, 0, key="demand_change")
        buffer = st.slider("Safety buffer per departure", 0, 8, 2, key="safety_buffer")
        strategy = st.selectbox("Inventory strategy", ["Release eligible seats", "Retain all seats"], key="strategy")
        st.caption("Protect confirmed passengers and the minimum group. Respect release caps. Block releases after the deadline. Assumes unchanged fares, unit costs and release fees.")
    scenario = pd.DataFrame(inventory_records(contracts, as_of, uplift, buffer, strategy == "Release eligible seats"))
    margin, baseline = scenario["margin"].sum(), scenario["baselineMargin"].sum()
    with right, st.container(border=True):
        st.subheader("What changes commercially")
        st.metric("Illustrative contribution improvement", cash(margin - baseline))
        a, b = st.columns(2)
        a.metric("Seats released", int(scenario["release"].sum()))
        b.metric("Seats retained", int(scenario["retained"].sum()))
        a.metric("Expected passengers served", int(scenario["served"].sum()))
        b.metric("Demand beyond retained capacity", int(scenario["missed"].sum()))
        st.write(f"Retain-all contribution: **{cash(baseline)}** · Scenario contribution: **{cash(margin)}**")
        st.caption("Air revenue minus retained-seat cost and release fees. Excludes tour land components and overheads. Not achieved company savings.")
    st.subheader("Decisions by commitment")
    table(display_inventory(scenario.sort_values(["days", "benefit"], ascending=[True, False])))
    csv_download(scenario[["id", "route", "departure", "releaseDate", "days", "demand", "release", "retained", "served", "missed", "margin", "baselineMargin", "benefit", "status"]], "Download this scenario CSV", "touring-control-scenario.csv", "scenario_csv")

elif view == "Data quality":
    quality = data["quality"]
    metrics = metric_columns()
    for col, label, value in zip(metrics, ["Raw booking records", "Accepted booking records", "Quarantined exceptions", "Real market observations"], [quality["rawRecords"], quality["acceptedRecords"], len(quality["quarantined"]), quality["marketRows"]]):
        col.metric(label, value)
    st.caption("Pipeline controls apply to the complete source dataset; portfolio filters apply to commercial views.")
    with st.container(border=True):
        st.subheader("Exception register")
        table(pd.DataFrame(quality["quarantined"]))
        st.write("Duplicate booking IDs, unknown contract references and future-dated bookings are quarantined before reporting.")
    with st.container(border=True):
        st.subheader("Reconciliation controls")
        checks = ["Accepted booking passengers reconcile to contract bookings", "Market inbound + outbound equals total traffic", "Route/month keys are unique", "All expected route months are present"]
        table(pd.DataFrame({"Control": checks, "Result": ["Passed" if quality["contractReconciled"] else "Failed", "Passed" if quality["marketReconciled"] else "Failed", "Passed" if quality["duplicateMarketKeys"] == 0 else "Failed", "Passed" if quality["missingMonths"] == 0 else "Failed"]}))
    st.subheader("Source lineage")
    st.write(f"**Publisher:** {data['provenance']['publisher']}\n\n**Retrieved:** {data['provenance']['retrievedDate']} · **Release:** {data['provenance']['releaseDate']}\n\n**Raw market rows:** {data['provenance']['rawMarketRows']:,} · **Simulation seed:** {data['provenance']['simulationSeed']}")
    st.caption(data["provenance"]["measure"])
    st.code(data["provenance"]["sha256"], language=None)
    st.caption("SHA-256 of the pinned original XLSX. No personal customer data is included.")

elif view == "Project & methodology":
    solution, methodology, report = st.tabs(["Solution & workflow", "Calculations & assumptions", "Full report"])
    with solution:
        st.subheader("From business problem to practical solution")
        st.write("When supplier contracts, booking records and sales reports sit in separate systems, teams can struggle to see exposure in time. This case study models a shared review workflow for an Inventory Coordinator working with Product, Commercial, Sales, Finance and Operations.")
        table(pd.DataFrame([
            {"Business problem": "Fragmented inventory and booking records", "Dashboard solution": "Reconciled contract register, filters and data-quality controls", "Intended outcome": "A consistent passenger and seat position"},
            {"Business problem": "Weak bookings near a supplier release deadline", "Dashboard solution": "Utilisation, gross unbooked commitment and deadline alerts", "Intended outcome": "Earlier review of avoidable cost exposure"},
            {"Business problem": "Uncertain demand and seasonal booking patterns", "Dashboard solution": "Market forecast validation and illustrative tour booking curves", "Intended outcome": "Better-informed capacity planning"},
            {"Business problem": "Releasing too many or too few seats", "Dashboard solution": "Demand scenarios with booking protection, buffers and contract limits", "Intended outcome": "Compare capacity needs with contribution trade-offs"},
            {"Business problem": "Inconsistent reporting across stakeholder teams", "Dashboard solution": "Budget and prior-year comparisons, CSV exports and an Excel pack", "Intended outcome": "A shared, reviewable basis for commercial decisions"},
        ]))
        st.caption("These are the project's intended benefits. It uses simulated commercial records and does not demonstrate realised savings or diagnose Flight Centre's internal operations.")
        st.subheader("How a coordinator uses it")
        st.markdown("1. Reconcile contracted inventory and bookings.\n2. Monitor utilisation, release deadlines, budget and comparable prior-year performance.\n3. Inspect real market seasonality and forecast validation.\n4. Test demand and capacity scenarios within contract constraints.\n5. Export decisions for Product, Commercial, Sales, Finance and Operations review.")
        st.write("**Scope:** Six city pairs, 252 official market observations, 48 simulated commitments, 1,632 seats and 748 accepted bookings.")
        st.info("A production pilot would require actual supplier terms, historical booking snapshots, cancellations, capacity bottlenecks, refresh monitoring, role-based approvals and a durable audit trail.")
    with methodology:
        st.markdown("**Booked utilisation** = booked passengers ÷ contracted seats.\n\n**Unbooked commitment** = unsold seats × return-air unit cost; this is not an expected loss.\n\n**Release quantity** = eligible seats above max(confirmed bookings, minimum group, forecast demand + buffer), capped by the contract release allowance.\n\n**Contribution** = passengers served × selling price − retained seats × unit cost − released seats × release fee.")
        st.write("Market models use chronological validation: 2023–24 initial history, 12 rolling 2025 validation months, six separate Jan–Jun 2026 holdout months. The selected model is the seasonal baseline. Error envelopes use historical validation errors, with observed coverage disclosed.")
        st.warning("Tour booking curves, costs, fares, release fees, airline assignments, budgets and prior-year figures are simulated. Public city-pair statistics do not represent My Touring bookings or live seat availability.")
    with report:
        st.markdown((ROOT / "docs/case-study.md").read_text())
    st.subheader("Download the project evidence")
    downloads = st.columns(3)
    for col, label, path, mime in [(downloads[0], "Excel reporting pack", "public/reports/touring-control.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                                  (downloads[1], "Business case report", "docs/case-study.md", "text/markdown"),
                                  (downloads[2], "Interview walkthrough", "docs/interview-guide.md", "text/markdown")]:
        with col:
            st.download_button(label, (ROOT / path).read_bytes(), path.split("/")[-1], mime=mime, width="stretch")
    st.caption("The Excel pack contains formulas, tables and a chart. It is PivotTable-ready and does not contain a native PivotTable.")
    st.link_button("Explore the original React dashboard", "https://touring-control-commercial-lab.rainyhinny4.chatgpt.site/")

st.divider()
st.caption("Independent portfolio project. Not affiliated with or endorsed by Flight Centre or My Touring. Commercial records and financial outcomes are simulated. No airline inventory is changed by this app.")
