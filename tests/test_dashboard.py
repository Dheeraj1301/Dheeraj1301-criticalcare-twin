from streamlit.testing.v1 import AppTest


def test_all_dashboard_pages_render():
    pages = ["Command Center", "Observation Ingestion", "State Explorer", "Risk & Explainability", "Digital Twin Platform", "Evidence Lab"]
    app = AppTest.from_file("app.py", default_timeout=30).run()
    assert not app.exception
    for page in pages:
        app.radio[0].set_value(page).run()
        assert not app.exception, f"{page} raised {app.exception}"
