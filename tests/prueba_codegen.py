import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page.goto("http://127.0.0.1:5001/auth/login")
    expect(page.locator("#loginForm")).to_contain_text("8888")
    page.get_by_role("textbox", name="Contrasena").click()
    page.get_by_role("textbox", name="Contrasena").fill("21")
    page.get_by_role("button", name=" Ingresar").click()
    page.get_by_role("button", name=" Ingresar").click(click_count=3)
    page.get_by_role("button", name=" Ingresar").click()
    page.get_by_role("textbox", name="Correo Electronico").click()
    page.get_by_role("textbox", name="Correo Electronico").fill("8")
    page.get_by_role("button", name=" Ingresar").click()
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
