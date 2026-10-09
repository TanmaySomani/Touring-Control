"""Financial parity, contract constraints and Streamlit interaction checks."""

import json
from pathlib import Path
import subprocess
import unittest
from streamlit.testing.v1 import AppTest
from analytics.streamlit_model import load_portfolio, filter_contracts, recommend, summarize

ROOT = Path(__file__).resolve().parents[1]
DATA = load_portfolio()


class CommercialModelTests(unittest.TestCase):
    def test_python_matches_typescript_for_every_contract_and_scenario(self):
        script = """
import fs from 'node:fs';
import ts from 'typescript';
const source=fs.readFileSync('lib/analytics.ts','utf8');
const code=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext}}).outputText;
const {recommend}=await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64'));
const data=JSON.parse(fs.readFileSync('public/data/portfolio.json','utf8'));
const result=[];
for(const c of data.contracts)for(const demand of [-35,0,35])for(const buffer of [0,2,8])for(const enabled of [true,false])result.push(recommend(c,data.asOf,demand,buffer,enabled));
process.stdout.write(JSON.stringify(result));
"""
        output = subprocess.check_output(["node", "--input-type=module", "-e", script], cwd=ROOT, text=True)
        expected = json.loads(output)
        actual = [recommend(c, DATA["asOf"], demand, buffer, enabled)
                  for c in DATA["contracts"] for demand in [-35, 0, 35]
                  for buffer in [0, 2, 8] for enabled in [True, False]]
        self.assertEqual(actual, expected)  # 864 combinations, all fields including AUD.

    def test_expired_deadlines_never_release_seats(self):
        for c in DATA["contracts"]:
            result = recommend(c, DATA["asOf"], -35, 0)
            if result["days"] < 0:
                self.assertEqual(result["release"], 0)

    def test_capacity_and_bookings_are_protected(self):
        for c in DATA["contracts"]:
            for demand in [-35, 0, 35]:
                result = recommend(c, DATA["asOf"], demand, 2)
                self.assertGreaterEqual(result["retained"], c["booked"])
                self.assertGreaterEqual(result["retained"], c["minGroup"])
                self.assertLessEqual(result["release"], c["maxRelease"])
                self.assertEqual(result["retained"] + result["release"], c["seats"])

    def test_filters_and_weighted_metrics(self):
        rows = filter_contracts(DATA["contracts"], DATA["asOf"], region="Oceania")
        totals = summarize(rows, DATA["asOf"])
        self.assertEqual(len(rows), 8)
        self.assertEqual(totals["seats"], 272)
        self.assertEqual(totals["booked"], 145)
        self.assertAlmostEqual(totals["utilisation"], 145 / 272 * 100)
        self.assertEqual(summarize([], DATA["asOf"])["utilisation"], 0)


class StreamlitInteractionTests(unittest.TestCase):
    def test_six_views_render_without_errors(self):
        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
        self.assertFalse(app.exception)
        for view in ["Flight inventory", "Demand forecast", "Scenario planner", "Data quality", "Project & methodology", "Overview"]:
            app.sidebar.radio[0].set_value(view).run()
            self.assertFalse(app.exception, f"{view}: {app.exception}")

    def test_filters_and_demand_scenario_change_results(self):
        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
        app.selectbox(key="region").set_value("Oceania").run()
        self.assertEqual(app.metric[0].value, "272")
        app.selectbox(key="region").set_value("All regions").run()
        app.sidebar.radio[0].set_value("Scenario planner").run()
        self.assertEqual(app.metric[0].value, "$218,402")
        self.assertEqual(app.metric[1].value, "206")
        app.slider(key="demand_change").set_value(20).run()
        self.assertEqual(app.metric[1].value, "94")
        app.selectbox(key="strategy").set_value("Retain all seats").run()
        self.assertEqual(app.metric[0].value, "$0")
        self.assertEqual(app.metric[1].value, "0")
        self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
