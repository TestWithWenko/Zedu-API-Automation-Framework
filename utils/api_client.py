import requests
import os
from dotenv import load_dotenv

load_dotenv()




class ApiClient:
    def __init__(self, token = None):
        self.base_url = os.getenv("BASE_URL")
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept":"application/json"
            })
        else:
            self.session.headers.update({
                "Content-type": "application/json",
                "Accept": "application/json",
            })
            
    def get(self, path, **kwargs):
        return self.session.get(f"{self.base_url}{path}", **kwargs)
    
    def post(self, path, **kwargs):
        return self.session.post(f"{self.base_url}{path}", **kwargs)
    
    def put(self, path, **kwargs):
        return self.session.put(f"{self.base_url}{path}", **kwargs)
    
    def with_headers(self, extra_headers: dict):
        merged ={**dict(self.session.headers), **extra_headers}
        client = ApiClient()
        client.session.headers.update(merged)
        return client