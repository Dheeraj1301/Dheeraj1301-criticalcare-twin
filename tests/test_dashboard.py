from streamlit.testing.v1 import AppTest


def test_all_dashboard_pages_render_and_scenario_runs():
    pages = ["Command Center", "Live Twin", "State Explorer", "Risk & Explainability", "What-If Lab", "Cloud & Edge", "Evidence Lab"]
    app = AppTest.from_file("app.py", default_timeout=30).run()
    assert not app.exception
    for page in pages:
        app.radio[0].set_value(page).run()
        assert not app.exception, f"{page} raised {app.exception}"
    app.radio[0].set_value("What-If Lab").run()
    app.button[0].click().run()
    assert not app.exception
    isolation = [metric for metric in app.metric if metric.label == "Actual twin isolation"]
    assert isolation and isolation[0].value == "VERIFIED"
