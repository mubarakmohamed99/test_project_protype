import xmlrpc.client


class OdooConnector:
	def __init__(self, url, db, user, api_key):
		self.url = url
		self.db = db
		self.user = user
		self.password = api_key
		self.uid = None
		self.models = None

	def _authenticate(self):
		"""Authenticates with Odoo and sets up the object proxy."""
		try:
			common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
			self.uid = common.authenticate(self.db, self.user, self.password, {})
			self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
			return True
		except Exception as e:
			print(f"Auth Error: {e}")
			return False

	def extract_pos_data(self):
		"""Retrieves POS orders and their specific details."""
		if not self.uid:
			if not self._authenticate():
				return None

		try:
			# Search for paid orders
			# We filter for 'paid' or 'done' states to ensure we get completed transactions
			order_ids = self.models.execute_kw(
				self.db,
				self.uid,
				self.password,
				"pos.order",
				"search",
				[[["state", "in", ["paid", "done"]]]],
			)

			if not order_ids:
				return []

			# Read the specific fields (File Output equivalent)
			fields = ["name", "date_order", "amount_total", "amount_tax", "pos_reference"]
			pos_data = self.models.execute_kw(
				self.db,
				self.uid,
				self.password,
				"pos.order",
				"read",
				[order_ids],
				{"fields": fields},
			)

			return pos_data

		except Exception as e:
			print(f"Data Extraction Error: {e}")
			return None
