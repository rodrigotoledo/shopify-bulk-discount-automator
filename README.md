# Shopify Bulk Discount Automator

A simple Python script to automatically apply bulk discounts to products in specific Shopify collections.

## Description

This script connects to your Shopify store via API and applies discounts to products in collections that match predefined keywords (e.g., "praia", "biquini", etc.). It sets a discounted price and a compare-at price to display the discount on your store.

**Note:** The script runs in dry-run mode by default. Uncomment the relevant sections in the code to apply real changes.

## Features

- Filters products by collection keywords
- Applies percentage or fixed discounts
- Ensures minimum price thresholds
- Dry-run mode for safe testing
- Uses environment variables for secure API access

## Requirements

- Python 3.x
- Shopify store with API access
- `shopify` and `python-dotenv` libraries

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/rodrigotoledo/shopify-bulk-discount-automator.git
   cd shopify-bulk-discount-automator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the root directory:
   ```
   ACCESS_TOKEN=your_shopify_access_token_here
   ```

2. Update the configuration variables in `discount-prices.py`:
   - `SHOP_URL`: Your Shopify store URL
   - `API_VERSION`: Shopify API version
   - `BASE_PRICE`: Minimum price for products to qualify
   - `DISCOUNT_TYPE`: "percent" or "fixed"
   - `DISCOUNT_VALUE`: Discount amount
   - `MINIMUM_PRICE_AFTER_DISCOUNT`: Floor price
   - `COLLECTION_KEYWORDS`: List of keywords to match collections

## Usage

Run the script:
```bash
python discount-prices.py
```

The script will:
- Find matching collections
- Simulate discounts on eligible products
- Print changes (in dry-run mode)

To apply real changes, edit the script and uncomment the lines marked with `# ────────────────────────────────────────────` and `# UNCOMMENT BELOW TO APPLY REAL CHANGES`.

## How It Works in Your Store

- For each eligible product variant, the script sets:
  - `price`: The new discounted price
  - `compare_at_price`: The original price (to show the discount)
- This creates a "sale" appearance in your Shopify store, displaying the crossed-out original price and the discounted price.

## Disclaimer

This script modifies product prices. Test thoroughly in dry-run mode before applying changes. Ensure you have backups and understand the impact on your store.
