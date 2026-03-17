import pytest
import re
from playwright.sync_api import Page, expect
from shiny.pytest import create_app_fixture

app = create_app_fixture("../src/app.py", timeout_secs=120)

@pytest.mark.playwright
def test_initial_load_and_sync(page: Page, app):
    """Verifies that the initial 'Total Squirrels' count in the map legend matches the full dataset length displayed in the data table footer to ensure data integrity on startup."""
    page.goto(app.url)
    
    legend_text = page.frame_locator("iframe").locator("#fur-legend").inner_text()
    legend_match = re.search(r"Total Squirrels\n([\d,]+)", legend_text)
    legend_count = legend_match.group(1).replace(",", "")
    
    table_footer = page.locator("#table_view").inner_text()
    table_match = re.search(r"of (\d+)", table_footer)
    table_count = table_match.group(1)
    
    assert legend_count == table_count == "3023"

@pytest.mark.playwright
def test_unknown_age_filter_logic(page: Page, app):
    """Ensures that filtering for 'Unknown' age successfully captures records where age data was missing or imputed from '?', validating the data cleaning pipeline."""
    page.goto(app.url)
    page.get_by_label("Adult").uncheck()
    page.get_by_label("Juvenile").uncheck()
    
    legend_count = page.frame_locator("iframe").locator("#fur-legend")
    expect(legend_count).to_contain_text("125", timeout=15000)

@pytest.mark.playwright
def test_issue_56_empty_filter_behavior(page: Page, app):
    """Verifies that unselecting all checkboxes in the 'Shift' group results in a 'show all' state (Issue #56) rather than returning zero results, ensuring dashboard robustness."""
    page.goto(app.url)
    page.get_by_label("AM", exact=True).uncheck()
    page.get_by_label("PM").uncheck()
    
    legend_count = page.frame_locator("iframe").locator("#fur-legend")
    expect(legend_count).to_contain_text("3,023", timeout=15000)

@pytest.mark.playwright
def test_ai_tab_navigation_and_chat(page: Page, app):
    """Checks that the AI Analysis tab is accessible and that the Chat interface successfully loads its interactive components for user engagement."""
    page.goto(app.url)
    page.get_by_role("tab", name="🤖 AI Analysis").click()
    
    expect(page.get_by_text("💬 Ask the AI to filter the data")).to_be_visible(timeout=10000)
    expect(page.locator("text=💬 Ask the AI to filter the data")).to_be_visible()