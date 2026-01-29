import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.init_client()
        return cls._instance
    
    def init_client(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")
            
        self.client: Client = create_client(url, key)

    def get_client(self) -> Client:
        return self.client

# Helper to get DB instance easily
def get_db() -> Client:
    return Database().get_client()
