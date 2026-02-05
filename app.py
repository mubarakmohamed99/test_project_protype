import streamlit as st
from main_ml.agent_code import OdooConnector

st.set_page_config(page_title="Odoo AI Agent Tunnel", layout="wide")

st.title("🛡️ POS Data Extraction (Cloud-to-Local Bridge)")
st.sidebar.header("Odoo Cloud Configuration")

# 1. Inputs - Ensure you paste the FORWARDING URL (e.g., https://xyz.ngrok-free.app)
url = st.sidebar.text_input("Ngrok Forwarding URL", placeholder="https://your-id.ngrok-free.app")
db = st.sidebar.text_input("Database Name", value="mubaodoo")
user = st.sidebar.text_input("Username/Email", value="mubarack.mohamud@students.uor...")
api_key = st.sidebar.text_input("API Key", type="password")

if st.sidebar.button("Connect & Extract Data"):
    if not url:
        st.error("Please provide your public Ngrok URL.")
    elif not api_key:
        st.error("Please provide an Odoo API Key.")
    else:
        agent = OdooConnector(url, db, user, api_key)
        
        with st.spinner(f"Requesting data via tunnel {url}..."):
            result = agent.extract_pos_data()

        if result["status"] == "success":
            st.success(f"Bridge Active: Retrieved {len(result['data'])} transactions!")
            
            # Displaying the clean data extracted from POS
            st.subheader("Live POS Transaction Data")
            st.table(result["data"])
            
            st.info("Data flow: Local Odoo ➡️ Ngrok Tunnel ➡️ Streamlit Cloud ➡️ Dashboard")
        else:
            st.error(f"⚠️ {result['message']}")
            st.info("💡 Check http://127.0.0.1:4040 on your host machine to see if the request reached your tunnel.")

st.divider()
st.caption("Computer Science Project - University of Nairobi Class of 2026")
