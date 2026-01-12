import streamlit as st
import json
import re
from datetime import datetime

st.set_page_config(page_title="Quirk Advisor Copilot (Demo)", page_icon="🤖", layout="centered")


def validate_vin(vin: str) -> tuple[bool, str]:
    """
    Validate a VIN (Vehicle Identification Number).
    Returns (is_valid, error_message).
    """
    if not vin:
        return True, ""  # Empty VIN is allowed (partial searches)

    # Remove spaces and convert to uppercase
    vin = vin.strip().upper()

    # VINs cannot contain I, O, or Q
    invalid_chars = set("IOQ")
    if any(c in invalid_chars for c in vin):
        return False, "VIN cannot contain letters I, O, or Q"

    # Check for valid characters (alphanumeric only, no I/O/Q)
    valid_pattern = re.compile(r'^[A-HJ-NPR-Z0-9*]+$')
    if not valid_pattern.match(vin):
        return False, "VIN can only contain letters A-Z (except I, O, Q), numbers, and * for wildcards"

    # Full VIN must be exactly 17 characters
    if len(vin) == 17 or '*' in vin:
        return True, ""
    elif len(vin) > 17:
        return False, "VIN cannot exceed 17 characters"
    elif len(vin) < 17 and '*' not in vin:
        return False, f"Partial VIN detected ({len(vin)} chars). Use * for unknown characters or enter full 17-character VIN"

    return True, ""


def filter_by_query(items: list[dict], query: str, title_key: str = "title") -> list[dict]:
    """
    Filter items by matching query keywords against item titles.
    Returns all items if query is empty.
    """
    if not query or not query.strip():
        return items

    # Extract keywords from query (split on common delimiters)
    keywords = re.split(r'[;,\s]+', query.lower().strip())
    keywords = [k for k in keywords if k and len(k) > 1]  # Filter out single chars and empty

    if not keywords:
        return items

    # Score items by how many keywords they match
    scored_items = []
    for item in items:
        title_lower = item.get(title_key, "").lower()
        score = sum(1 for kw in keywords if kw in title_lower)
        if score > 0:
            scored_items.append((score, item))

    # Sort by score descending, return items
    scored_items.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored_items] if scored_items else items


def add_to_search_history(vin: str, make: str, model: str, year: int, query: str):
    """Add a search to session state history."""
    if "search_history" not in st.session_state:
        st.session_state.search_history = []

    search_entry = {
        "vin": vin,
        "make": make,
        "model": model,
        "year": year,
        "query": query,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    # Add to beginning, keep only last 5 searches
    st.session_state.search_history.insert(0, search_entry)
    st.session_state.search_history = st.session_state.search_history[:5]


# Initialize session state
if "search_history" not in st.session_state:
    st.session_state.search_history = []

st.title("🤖 Quirk Advisor Copilot - Demo")
st.caption("VIN decoding | Cross-catalog lookup | Price/ETA | Upsell kits (mock)")

# Search History Sidebar
with st.sidebar:
    st.subheader("Recent Searches")
    if st.session_state.search_history:
        for i, search in enumerate(st.session_state.search_history):
            vehicle = f"{search['year']} {search['make']} {search['model']}".strip()
            if vehicle.strip() == str(search['year']):
                vehicle = search.get('vin', 'Unknown') or 'Unknown'
            st.text(f"{i+1}. {vehicle}")
            if search.get('query'):
                st.caption(f"   Query: {search['query'][:30]}...")
    else:
        st.caption("No recent searches")

with st.form("copilot"):
    vin = st.text_input("VIN (partial or full)", placeholder="1C4HJXDG9MW****** or full 17-char VIN")
    make = st.text_input("Make", placeholder="Jeep")
    model = st.text_input("Model", placeholder="Wrangler")
    year = st.number_input("Year", 1990, 2030, 2018)
    query = st.text_area("What do you need?", placeholder="clip for trunk latch; brake pads; cargo liner; ...")
    submitted = st.form_submit_button("Ask Copilot")

if submitted:
    # Input validation
    errors = []

    # Validate VIN if provided
    if vin:
        vin_valid, vin_error = validate_vin(vin)
        if not vin_valid:
            errors.append(f"VIN Error: {vin_error}")

    # Require at least some identifying info
    has_vehicle_info = bool(make and model) or bool(vin and len(vin.replace('*', '')) >= 8)
    if not has_vehicle_info:
        errors.append("Please provide Make and Model, or at least 8 characters of a VIN")

    # Show errors or proceed
    if errors:
        for error in errors:
            st.error(error)
    else:
        # Add to search history
        add_to_search_history(vin, make, model, year, query)

        # Mock parts data (expanded for filtering demo)
        all_suggestions = [
            {"partNumber": "68212345AB", "title": "Latch Clip - Trunk", "oem": "Mopar", "price": 8.75, "etaDays": 0, "fits": [f"{year} {make} {model}"]},
            {"partNumber": "68212345AC", "title": "Latch Clip - Trunk (Superseded)", "oem": "Mopar", "price": 9.25, "etaDays": 2, "fits": [f"{year} {make} {model}"]},
            {"partNumber": "68056754AA", "title": "Brake Pad Set - Front", "oem": "Mopar", "price": 89.99, "etaDays": 1, "fits": [f"{year} {make} {model}"]},
            {"partNumber": "68056755AA", "title": "Brake Pad Set - Rear", "oem": "Mopar", "price": 79.99, "etaDays": 1, "fits": [f"{year} {make} {model}"]},
            {"partNumber": "82215274", "title": "Cargo Liner - Rear", "oem": "Mopar", "price": 129.00, "etaDays": 3, "fits": [f"{year} {make} {model}"]},
            {"partNumber": "68318365AA", "title": "Air Filter Element", "oem": "Mopar", "price": 32.50, "etaDays": 0, "fits": [f"{year} {make} {model}"]},
        ]

        upsell = [
            {"partNumber": "82215274", "title": "Cargo Liner, Rear", "oem": "Mopar", "price": 129.00},
            {"partNumber": "82214786", "title": "All-Weather Mats Set", "oem": "Mopar", "price": 179.00},
        ]

        # Filter suggestions based on query
        suggestions = filter_by_query(all_suggestions, query)

        st.success(f"Found {len(suggestions)} compatible part(s) (mock data)")

        st.subheader("Results")
        if query and len(suggestions) < len(all_suggestions):
            st.info(f"Filtered by query: \"{query}\"")

        for s in suggestions:
            eta_text = "In Stock" if s['etaDays'] == 0 else f"ETA: {s['etaDays']} day(s)"
            st.write(
                f"**{s['partNumber']}** - {s['title']} ({s['oem']})  \n"
                f"Price: ${s['price']:.2f} | {eta_text}  \n"
                f"Fits: {', '.join(s['fits'])}"
            )
            st.divider()

        st.subheader("Supersession Chain")
        st.json({
            "root": "68212345",
            "chain": ["68212345AA", "68212345AB", "68212345AC"],
            "current": "68212345AC"
        })

        st.subheader("Cross References")
        st.json([
            {"partNumber": "DORMAN-12345", "type": "aftermarket", "note": "Aftermarket equivalent"},
            {"partNumber": "MOPAR-68212345AA", "type": "oem-equivalent", "note": "Earlier supersession"}
        ])

        st.subheader("Upsell Kit Suggestions")
        for u in upsell:
            st.write(f"- **{u['partNumber']}** - {u['title']} (${u['price']:.2f})")

st.markdown("---")
st.caption(f"Demo generated {datetime.utcnow().isoformat()}Z | Mock only - connect to real APIs when ready.")
