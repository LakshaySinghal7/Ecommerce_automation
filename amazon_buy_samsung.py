import time
import traceback
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

DOMAIN = "amazon.in"
SEARCH_TEXT = "Samsung Galaxy smartphone"
PICK = 1
WAIT_TIMEOUT = 15

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


def take_screenshot(driver, name):
    path = SCREENSHOT_DIR / f"{name}.png"
    driver.save_screenshot(str(path))
    print(f"   Screenshot saved: {path}")


def find_visible(driver, css_selectors, timeout=10):
    end_time = time.time() + timeout
    while time.time() < end_time:
        for selector in css_selectors:
            for el in driver.find_elements(By.CSS_SELECTOR, selector):
                try:
                    if el.is_displayed() and el.is_enabled():
                        return el
                except Exception:
                    pass
        time.sleep(0.5)
    raise TimeoutException(f"Could not find visible element: {css_selectors}")


def main():
    print("[STEP 1] Starting Chrome browser...")
    options = webdriver.ChromeOptions()
    # options.add_argument("--window-size=1366,900")
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    try:
        print(f"[STEP 2] Opening https://www.{DOMAIN}")
        driver.get(f"https://www.{DOMAIN}")

        for btn in driver.find_elements(By.XPATH, "//button[contains(., 'Continue shopping')]"):
            btn.click()
            break

        print(f"[STEP 3] Searching for: {SEARCH_TEXT}")
        search_box = wait.until(EC.element_to_be_clickable((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys(SEARCH_TEXT, Keys.ENTER)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-component-type='s-search-result']")))
        take_screenshot(driver, "01_search_results")

        print("[STEP 4] Collecting search results...")
        items = []
        for r in driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']"):
            if r.find_elements(By.CSS_SELECTOR, ".puis-sponsored-label-text, .s-sponsored-label-text"):
                continue

            titles = r.find_elements(By.CSS_SELECTOR, "h2")
            links = r.find_elements(By.CSS_SELECTOR, "a:has(h2), h2 a")
            if not titles or not links:
                continue

            title = " ".join(t.text.strip() for t in titles if t.text.strip())
            if "samsung" not in title.lower():
                continue

            items.append((title, links[0].get_attribute("href")))

        if not items:
            raise RuntimeError("No Samsung phones found in search results.")

        chosen_title, chosen_href = items[min(PICK, len(items)) - 1]
        print(f"   -> Picked product: {chosen_title[:80]}")

        print("[STEP 5] Opening product page...")
        driver.get(chosen_href)
        wait.until(EC.presence_of_element_located((By.ID, "productTitle")))
        take_screenshot(driver, "02_product_page")

        print("[STEP 6] Adding item to cart...")
        btn = find_visible(driver, ["#add-to-cart-button"])
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        time.sleep(0.5)
        btn.click()

        try:
            find_visible(driver, ["#attachSiNoCoverage input", "#attachSiNoCoverage-announce"], timeout=4).click()
        except TimeoutException:
            pass

        wait.until(lambda d: d.find_element(By.ID, "nav-cart-count").text.strip() not in ("", "0"))
        take_screenshot(driver, "03_added_to_cart")

        print("[STEP 7] Proceeding to checkout...")
        driver.get(f"https://www.{DOMAIN}/gp/cart/view.html")
        take_screenshot(driver, "03a_cart_page")
        checkout_btn = wait.until(EC.element_to_be_clickable((By.NAME, "proceedToRetailCheckout")))
        checkout_btn.click()
        time.sleep(3)
        take_screenshot(driver, "04_checkout_screen")

        print("\n[SUCCESS] Reached checkout flow successfully!")

    except Exception as e:
        print("\n" + "=" * 60)
        print("[FAIL] Test encountered an error!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Details: {e if str(e).strip() else 'No error message provided by Selenium'}")
        print("\n--- TRACEBACK ---")
        traceback.print_exc()
        print("=" * 60 + "\n")
        take_screenshot(driver, "error_state")

    finally:
        print("Closing browser...")
        driver.quit()


if __name__ == "__main__":
    main()