# Streamlit deployment

Live app: https://touring-control-tanmaysomani.streamlit.app/

- Repository: `TanmaySomani/Touring-Control`
- Branch: `main`
- Entry point: `streamlit_app.py`
- Python version: `3.12`
- Dependencies: root `requirements.txt`
- Theme: `.streamlit/config.toml`
- Sharing: public, verified in the app sharing dialog
- Secrets: none required

The app runs against the pinned analytical snapshot in `public/data/portfolio.json`. Report and workbook downloads are included in the repository. Cloud deployment does not run the ETL or install Node.js; the Python dashboard is independent of the React build.

Push updates to `main` to update the connected Streamlit app. Refresh the data intentionally by following the README; the current project is a fixed October 2026 case study rather than a live airline feed.

Validation: all six views render in Streamlit AppTest; filters and release strategies change results. The Python commercial model matches the TypeScript model for 864 contract/scenario combinations. Desktop and mobile layouts were inspected and the deployed app was checked interactively.

Source: [Streamlit Community Cloud deployment documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).
