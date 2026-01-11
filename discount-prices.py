import shopify
import unicodedata
from dotenv import load_dotenv
import os

load_dotenv()

# =====================================================
# CONFIGURATION
# =====================================================

SHOP_URL = "3u5a57-cv.myshopify.com"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = "2025-10"

BASE_PRICE = 150.00         # Minimum price (any variant) for product to qualify

# Choose discount type and value
DISCOUNT_TYPE = "percent"   # Options: "percent" or "fixed"
DISCOUNT_VALUE = 15.0       # 15.0 = 15% if percent   OR   15.00 = R$15 off if fixed

# Optional: prevent prices from going too low
MINIMUM_PRICE_AFTER_DISCOUNT = 29.90

COLLECTION_KEYWORDS = [
    "praia",
    "inverno",
    "verao",
    "verão",
    "biquini",
    "biquíni",
    "biquinis",
    "biquínis",
    "swimwear",
    "resort",
    "beachwear",
    "maio",
    "maiô",
    "body"
]

# =====================================================
# HELPERS
# =====================================================

def normalize(text):
    """Normalize text: remove accents, convert to lowercase, ASCII only"""
    if not text:
        return ""
    return (
        unicodedata
        .normalize("NFKD", text)
        .encode("ASCII", "ignore")
        .decode()
        .lower()
    )

def safe_float(value):
    """Safely convert value to float, return 0.0 on failure"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

# =====================================================
# SHOPIFY SESSION SETUP
# =====================================================

session = shopify.Session(SHOP_URL, API_VERSION, ACCESS_TOKEN)
shopify.ShopifyResource.activate_session(session)

# =====================================================
# FIND MATCHING COLLECTIONS (custom + smart)
# =====================================================

custom_collections = shopify.CustomCollection.find(limit=250)
smart_collections = shopify.SmartCollection.find(limit=250)

collections = list(custom_collections) + list(smart_collections)

matched_collections = []
for collection in collections:
    title_norm = normalize(collection.title)
    if any(normalize(k) in title_norm for k in COLLECTION_KEYWORDS):
        matched_collections.append(collection)

print("\nCollections found:")
for c in matched_collections:
    print(f" - {c.title}")

# =====================================================
# PROCESS PRODUCTS (DRY-RUN MODE)
# =====================================================

updated_products = set()
changes = 0

for collection in matched_collections:
    products = collection.products()

    for product in products:
        if product.status != "active":
            continue

        # Check if product qualifies (at least one variant >= BASE_PRICE with no active discount)
        qualifies = False
        for variant in product.variants:
            current_price = safe_float(variant.price)
            compare_at = safe_float(variant.compare_at_price)
            if current_price >= BASE_PRICE and compare_at <= 0:
                qualifies = True
                break

        if not qualifies:
            continue

        # Apply discount to all eligible variants of this product
        changes_for_product = False

        for variant in product.variants:
            current_price = safe_float(variant.price)
            compare_at = safe_float(variant.compare_at_price)

            # Skip if already has active discount (compare_at_price > 0)
            if compare_at > 0:
                continue

            # Calculate new price based on discount type
            if DISCOUNT_TYPE == "percent":
                discount_factor = DISCOUNT_VALUE / 100
                new_price = round(current_price * (1 - discount_factor), 2)
            elif DISCOUNT_TYPE == "fixed":
                new_price = round(current_price - DISCOUNT_VALUE, 2)
            else:
                print("ERROR: Invalid DISCOUNT_TYPE. Use 'percent' or 'fixed'")
                continue

            # Safety: don't allow negative or too low prices
            new_price = max(new_price, MINIMUM_PRICE_AFTER_DISCOUNT)

            # Only apply if price actually decreases
            if new_price >= current_price:
                continue

            # ────────────────────────────────────────────
            # DRY-RUN: only show what would be changed
            # ────────────────────────────────────────────
            print(
                f"[DRY-RUN] {product.title} | "
                f"Variant {variant.id} → "
                f"price: {current_price:.2f} → {new_price:.2f} | "
                f"compare_at: {current_price:.2f}"
            )

            # ────────────────────────────────────────────
            # UNCOMMENT BELOW TO APPLY REAL CHANGES
            # ────────────────────────────────────────────
            # variant.compare_at_price = f"{current_price:.2f}"
            # variant.price = f"{new_price:.2f}"

            changes += 1
            changes_for_product = True

        # Mark product as processed only if we made changes
        if changes_for_product:
            updated_products.add(product.id)

            # ────────────────────────────────────────────
            # UNCOMMENT TO SAVE REAL CHANGES
            # ────────────────────────────────────────────
            # if product.save():
            #     print(f"✔ Updated: {product.title}")
            # else:
            #     print(f"✖ Error: {product.title} → {product.errors.full_messages()}")

# =====================================================
# CLEANUP & SUMMARY
# =====================================================

shopify.ShopifyResource.clear_session()

print(f"\nDRY-RUN completed. {changes} changes simulated.")
print(f"Products that would be updated: {len(updated_products)}")
