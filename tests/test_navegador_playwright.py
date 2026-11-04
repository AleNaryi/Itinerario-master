
from playwright.sync_api import sync_playwright


def test_pagina_principal():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        response = page.goto(
            "http://127.0.0.1:5001",
            wait_until="domcontentloaded",
            timeout=30000
        )

        assert response is not None, "El servidor no devolvió respuesta"
        assert response.status < 400, (
            f"La página devolvió el estado HTTP {response.status}"
        )
        assert page.locator("body").is_visible(), (
            "El contenido de la página no está visible"
        )

        print("Prueba superada: la página principal responde correctamente.")

        browser.close()

