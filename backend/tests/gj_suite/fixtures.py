
# Data Fixtures from gj_testcases.md

AMPERE_BAD_INPUT = {
    "brand_name": "Ampere",
    "product_category": "Electric Scooter",
    "primary_objective": "growth", # Invalid Enum (Should be Sales/Leads/Awareness)
    "decision_speed": "Fast",
    "price_sensitivity": "Medium",
    "geography": "Tier 2 India",
    "primary_usp": "Affordable EV", # Added required field
    "price_positioning": "Budget" # Added required field
}

LIVGUARD_URGENT_INPUT = {
    "brand_name": "Livguard",
    "product_category": "Inverter Battery",
    "primary_objective": "Sales",
    "decision_speed": "Fast", # Critical check for TOF suppression
    "price_sensitivity": "High",
    "geography": "Pan India",
    "primary_usp": "Instant Power Backup",
    "price_positioning": "Mid-Range"
}

DULUX_SLOW_INPUT = {
    "brand_name": "Dulux",
    "product_category": "Interior Paint",
    "primary_objective": "Awareness",
    "decision_speed": "Slow", # Critical check for TOF requirement
    "price_sensitivity": "Medium",
    "geography": "Metro Cities",
    "primary_usp": "Washable premium finish",
    "price_positioning": "Premium"
}
