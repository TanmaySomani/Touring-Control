-- Snapshot commercial reporting. Monetary facts and contracts are simulated.
-- SQLite: execute against data/processed/inventory.sqlite.

-- One row per route: percentages are ratios of matching totals, not averages of row percentages.
SELECT route,
       COUNT(*) AS departures,
       SUM(seats) AS contracted_seats,
       SUM(booked) AS confirmed_passengers,
       ROUND(100.0 * SUM(booked) / SUM(seats), 1) AS booked_utilisation_pct,
       SUM((seats - booked) * unitCost) AS gross_unbooked_commitment_aud,
       SUM(forecastPax * sellPrice) AS forecast_air_revenue_aud,
       SUM(budgetPax * sellPrice) AS budget_air_revenue_aud,
       SUM((forecastPax - budgetPax) * sellPrice) AS revenue_variance_aud
FROM contracts
GROUP BY route
ORDER BY gross_unbooked_commitment_aud DESC;

-- Expired deadlines and upcoming release windows, in calendar days.
WITH deadlines AS (
 SELECT *, CAST(julianday(releaseDate) - julianday('2026-10-09') AS INTEGER) AS days_to_release
 FROM contracts
)
SELECT id, route, departure, releaseDate, days_to_release, booked, seats, owner,
       CASE WHEN days_to_release < 0 THEN 'Escalate expired deadline'
            ELSE 'Review before release date' END AS next_action
FROM deadlines
WHERE days_to_release <= 14
ORDER BY releaseDate;

-- Independent reconciliation must return no rows.
SELECT c.id, c.booked AS contract_passengers, COALESCE(SUM(b.passengers), 0) AS booking_passengers
FROM contracts c
LEFT JOIN bookings b ON b.contractId = c.id
GROUP BY c.id, c.booked
HAVING c.booked <> COALESCE(SUM(b.passengers), 0);

-- Year-on-year comparisons use the same lead time and simulated commercial population.
SELECT c.route, SUM(c.booked) AS current_passengers,
       SUM(p.bookedAtComparableLeadTime) AS prior_year_passengers,
       ROUND(100.0 * (SUM(c.booked) * 1.0 / SUM(p.bookedAtComparableLeadTime) - 1), 1) AS yoy_pct
FROM contracts c JOIN prior_year p ON p.contractId = c.id
GROUP BY c.route;
