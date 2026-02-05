import xmlrpc.client
import ssl

class OdooConnector:
    def __init__(self, url, db, user, api_key):
        # Ensure URL doesn't have a trailing slash
        self.url = url.rstrip('/')
        self.db = db
        self.user = user
        self.password = api_key
        self.uid = None

    def _get_proxy(self, service_path):
        """Creates a secure proxy that handles Ngrok's HTTPS certificate."""
        # Using unverified context is standard for dev-tunnels like Ngrok 
        # to avoid 'Certificate Verify Failed' errors in cloud environments.
        context = ssl._create_unverified_context()
        return xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/{service_path}", 
            context=context, 
            allow_none=True
        )

    def _authenticate(self):
        """Validates credentials via the public tunnel."""
        try:
            common = self._get_proxy('common')
            # The authenticate call returns the UID (int) if successful
            self.uid = common.authenticate(self.db, self.user, self.password, {})
            
            if not self.uid:
                return "Auth Failed: Invalid DB name, Email, or API Key."
            return True
        except Exception as e:
            return f"Tunnel Connection Failed: Ensure Ngrok is 'Online'. Details: {str(e)}"

    def extract_pos_data(self):
        """Fetches 'Paid' orders from the Odoo backend."""
        auth_status = self._authenticate()
        if auth_status is not True:
            return {"status": "error", "message": auth_status, "data": []}

        try:
            models = self._get_proxy('object')
            
            # Fetch IDs for all finalized orders
            order_ids = models.execute_kw(
                self.db, self.uid, self.password,
                'pos.order', 'search',
                [[['state', 'in', ['paid', 'done', 'invoiced']]]]
            )

            if not order_ids:
                return {"status": "no_data", "message": "Connection OK, but no paid orders found.", "data": []}

            # Retrieving specific fields for the 'System Components' part of your diagram
            fields = ['name', 'date_order', 'amount_total', 'pos_reference']
            pos_data = models.execute_kw(
                self.db, self.uid, self.password,
                'pos.order', 'read',
                [order_ids],
                {'fields': fields}
            )
            
            return {"status": "success", "data": pos_data}

        except Exception as e:
            return {"status": "api_error", "message": f"Odoo API Logic Error: {str(e)}", "data": []}
