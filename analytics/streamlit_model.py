"""Python equivalent of lib/analytics.ts, shared by the Streamlit UI and tests."""

from datetime import date
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_portfolio():
    return json.loads((ROOT / "public/data/portfolio.json").read_text())


def days_until(value, as_of):
    return (date.fromisoformat(value) - date.fromisoformat(as_of)).days


def recommend(contract, as_of, demand_change=0, buffer=2, release_enabled=True):
    """Protect bookings, minimum group size, forecast demand and a safety buffer."""
    days = days_until(contract["releaseDate"], as_of)
    # JS Math.round for the nonnegative forecasts used in the original model.
    demand = max(contract["booked"], math.floor(contract["forecastPax"] * (1 + demand_change / 100) + 0.5))
    protected = max(contract["booked"], contract["minGroup"], demand + buffer)
    release = max(0, min(contract["maxRelease"], contract["seats"] - protected)) if release_enabled and days >= 0 else 0
    retained = contract["seats"] - release
    served = min(demand, retained)
    margin = served * contract["sellPrice"] - retained * contract["unitCost"] - release * contract["releaseFee"]
    baseline = min(demand, contract["seats"]) * contract["sellPrice"] - contract["seats"] * contract["unitCost"]
    status = ("Deadline passed" if days < 0 else "Review release" if days <= 14 and release > 0 else
              "Strong demand" if demand >= contract["seats"] * .9 else "Monitor pace" if release > 0 else "On track")
    return dict(days=days, demand=demand, release=release, retained=retained, served=served,
                margin=margin, baselineMargin=baseline, benefit=margin - baseline,
                unbooked=(contract["seats"] - contract["booked"]) * contract["unitCost"],
                exposure=max(0, retained - served) * contract["unitCost"],
                missed=max(0, demand - retained), status=status)


def filter_contracts(contracts, as_of, region="All regions", origin="All origins", horizon="All departures"):
    maximum_days = {"Next 60 days": 60, "Next 120 days": 120}.get(horizon)
    return [c for c in contracts if (region == "All regions" or c["region"] == region)
            and (origin == "All origins" or c["origin"] == origin)
            and (maximum_days is None or days_until(c["departure"], as_of) <= maximum_days)]


def summarize(contracts, as_of):
    seats = sum(c["seats"] for c in contracts)
    booked = sum(c["booked"] for c in contracts)
    return dict(seats=seats, booked=booked, forecast=sum(c["forecastPax"] for c in contracts),
                utilisation=booked / seats * 100 if seats else 0,
                exposure=sum((c["seats"] - c["booked"]) * c["unitCost"] for c in contracts),
                due=sum(0 <= days_until(c["releaseDate"], as_of) <= 14 for c in contracts),
                overdue=sum(days_until(c["releaseDate"], as_of) < 0 for c in contracts),
                forecastRevenue=sum(c["forecastPax"] * c["sellPrice"] for c in contracts),
                budget=sum(c["budgetPax"] * c["sellPrice"] for c in contracts),
                benefit=sum(recommend(c, as_of)["benefit"] for c in contracts))


def inventory_records(contracts, as_of, demand_change=0, buffer=2, release_enabled=True):
    return [{**c, **recommend(c, as_of, demand_change, buffer, release_enabled)} for c in contracts]
