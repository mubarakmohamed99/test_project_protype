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
        """Returns True if successful, or the error message if it fails."""
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common', allow_none=True)
            # Check if we can even reach the server
            self.uid = common.authenticate(self.db, self.user, self.password, {})
            
            if not self.uid:
                return "Authentication Failed: Invalid credentials or API Key."
            
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object', allow_none=True)
            return True
        except Exception as e:
            return f"Connection Error: Could not reach Odoo at {self.url}. Details: {str(e)}"

    def extract_pos_data(self):
        """
        Returns a dictionary with status and data.
        Possible statuses: 'success', 'auth_error', 'no_data', 'api_error'
        """
        auth_status = self._authenticate()
        
        # 1. Handle Connection/Auth failures
        if auth_status is not True:
            return {"status": "auth_error", "message": auth_status, "data": []}

        try:
            # 2. Search for paid orders
            order_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'pos.order', 'search',
                [[['state', 'in', ['paid', 'done', 'invoiced']]]]
            )

            # 3. Handle specific case: Connection works, but no orders exist
            if not order_ids:
                return {
                    "status": "no_data", 
                    "message": "Connection successful, but no orders were found in 'paid' or 'done' state.",
                    "data": []
                }

            # 4. Success: Retrieve the data
            fields = ['name', 'date_order', 'amount_total', 'amount_tax', 'pos_reference']
            pos_data = self.models.execute_kw(
                self.db, self.uid, self.password,
                'pos.order', 'read',
                [order_ids],
                {'fields': fields}
            )
            
            return {"status": "success", "message": "Data retrieved successfully.", "data": pos_data}

        except Exception as e:
            return {"status": "api_error", "message": f"Odoo API Error: {str(e)}", "data": []}
