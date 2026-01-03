import streamlit as st
from main_ml.agent_code import OdooConnector

st.set_page_config(page_title="Odoo POS AI Dashboard", layout="wide")

st.title("🛡️ POS Data Extraction & AI Agent")
st.sidebar.header("Odoo Configuration")

# 1. Inputs for the configuration
url = st.sidebar.text_input("Odoo URL", value="http://localhost:8069")
db = st.sidebar.text_input("Database Name", value="my_pos_db")
user = st.sidebar.text_input("Username/Email", value="admin")
api_key = st.sidebar.text_input("API Key", type="password")

if st.sidebar.button("Connect & Extract Data"):
	if not api_key:
		st.error("Please provide an API Key.")
	else:
		# 2. Initialize the Agent Code
		agent = OdooConnector(url, db, user, api_key)

		with st.spinner("Connecting to Odoo and extracting POS data..."):
			data = agent.extract_pos_data()

		if data:
			st.success(f"Successfully retrieved {len(data)} transactions!")

			# 3. Display the raw data as it's retrieved from POS
			st.subheader("Extracted POS Transactions")
			st.table(data)

			# This is where you'd pass 'data' to your Model API/ML logic
			st.info("Data ready for Model API processing.")
		else:
			st.warning("No paid POS orders found or connection failed.")

st.divider()
st.caption("Computer Science Project - University of Nairobi Class of 2026")
