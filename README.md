# Amazon Samsung Automation

Selenium script that automates a phone purchase flow on amazon.in, up to the checkout page.

## Flow

1. Open amazon.in
2. Search for "Samsung Galaxy smartphone"
3. Skip sponsored results and pick the first Samsung listing
4. Open the product page and add it to the cart
5. Go to the cart and click "Proceed to checkout"

The order is not placed. Screenshots of each step are saved in `screenshots/`.

## Config

Settings at the top of `amazon_buy_samsung.py`:

- `DOMAIN` - Amazon site (default `amazon.in`)
- `SEARCH_TEXT` - search query
- `PICK` - which result to choose (1 = first)
- `WAIT_TIMEOUT` - max wait in seconds

## Requirements

- Python 3
- Google Chrome
- Selenium 4.20+
