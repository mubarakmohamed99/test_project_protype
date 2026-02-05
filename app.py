import streamlit as st
from main_ml.agent_code import OdooConnector

st.set_page_config(page_title="Odoo POS AI Dashboard", layout="wide")

st.title("🛡️ POS Data Extraction & AI Agent")
st.sidebar.header("Odoo Configuration")

# 1. Inputs for the configuration
url = st.sidebar.text_input("Odoo URL", value="http://localhost:8069")
db = st.sidebar.text_input("Database Name", value="mubaodoo")
user = st.sidebar.text_input("Username/Email", value="mubarack.mohamud@students.uor...") # Update with full email
api_key = st.sidebar.text_input("API Key", type="password")

if st.sidebar.button("Connect & Extract Data"):
    if not api_key:
        st.error("Please provide an API Key.")
    else:
        # 2. Initialize the Agent Code
        agent = OdooConnector(url, db, user, api_key)

        with st.spinner("Connecting to Odoo and extracting POS data..."):
            # This now returns a dictionary: {"status": ..., "message": ..., "data": [...]}
            result = agent.extract_pos_data()

        if result["status"] == "success":
            st.success(f"Successfully retrieved {len(result['data'])} transactions!")

            # 3. Display ONLY the list of orders in the table
            st.subheader("Extracted POS Transactions")
            st.table(result["data"])

            # Logic for next phase (ML/Agent API)
            st.info("Data ready for Model API processing.")
            
        elif result["status"] == "no_data":
            st.warning(result["message"])
        else:
            # This catches authentication or connection errors specifically
            st.error(result["message"])

st.divider()
st.caption("Computer Science Project - University of Nairobi Class of 2026")
