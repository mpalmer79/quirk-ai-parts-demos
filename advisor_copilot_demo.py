import streamlit as st
import json
from datetime import datetime

st.set_page_config(page_title="Quirk Advisor Copilot (Demo)", page_icon="🤖", layout="centered")

st.title("🤖 Quirk Advisor Copilot — Demo")
st.caption("VIN decoding • Cross-catalog lookup • Price/ETA • Upsell kits (mock)")

with st.form("copilot"):
    vin = st.text_input("VIN (partial or full)", placeholder="1C4HJXDG9MW******")
    make = st.text_input("Make", placeholder="Jeep")
    model = st.text_input("Model", placeholder="Wrangler")
    year = st.number_input("Year", 1990, 2030, 2018)
    query = st.text_area("What do you need?", placeholder="clip for trunk latch; brake pads; cargo liner; ...")
    submitted = st.form_submit_button("Ask Copilot")

if submitted:
    # Mock logic
    suggestions = [
        {"partNumber": "68212345AB", "title": "Latch Clip - Trunk", "oem": "Mopar", "price": 8.75, "etaDays": 0, "fits": [f"{year} {make} {model}"]},
        {"partNumber": "68212345AC", "title": "Latch Clip - Trunk (Superseded)", "oem": "Mopar", "price": 9.25, "etaDays": 2, "fits": [f"{year} {make} {model}"]},
    ]
    upsell = [
        {"partNumber": "82215274", "title": "Cargo Liner, Rear", "oem": "Mopar", "price": 129.00},
        {"partNumber": "82214786", "title": "All-Weather Mats Set", "oem": "Mopar", "price": 179.00},
    ]

    st.success("Found compatible parts (mock data)")

    st.subheader("Results")
    for s in suggestions:
        st.write(
            f"**{s['partNumber']}** — {s['title']} ({s['oem']})  \n"
            f"Price: ${s['price']:.2f} • ETA: {s['etaDays']} day(s)  \n"
            f"Fits: {', '.join(s['fits'])}"
        )

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
        st.write(f"• **{u['partNumber']}** — {u['title']} (${u['price']:.2f})")

st.markdown("---")
st.caption(f"Demo generated {datetime.utcnow().isoformat()}Z • Mock only — connect to real APIs when ready.")
