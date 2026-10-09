CREATE TABLE market_actuals (route TEXT, month TEXT, inbound INTEGER, outbound INTEGER, total INTEGER, source TEXT);
CREATE TABLE contracts (id TEXT, route TEXT, tour TEXT, airline TEXT, departure TEXT, releaseDate TEXT, seats INTEGER, booked INTEGER, forecastPax INTEGER, forecastLow INTEGER, forecastHigh INTEGER, unitCost INTEGER, sellPrice INTEGER, releaseFee INTEGER, maxRelease INTEGER, minGroup INTEGER, budgetPax INTEGER, owner TEXT, region TEXT, origin TEXT, status TEXT);
CREATE TABLE bookings (id TEXT, contractId TEXT, bookedAt TEXT, passengers INTEGER, channel TEXT, status TEXT, airRevenue INTEGER, source TEXT);
CREATE TABLE prior_year (contractId TEXT, departure TEXT, seats INTEGER, bookedAtComparableLeadTime INTEGER, revenue INTEGER, source TEXT);
CREATE UNIQUE INDEX market_grain ON market_actuals(route,month);
CREATE UNIQUE INDEX contract_key ON contracts(id);
CREATE UNIQUE INDEX booking_key ON bookings(id);
