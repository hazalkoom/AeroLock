from locust import HttpUser, task, between
import uuid
import itertools

import time
import random

# Global fast counter for user IDs to avoid expensive uuid4 calls during high-stress
run_id = int(time.time())
user_counter = itertools.count(1)
request_counter = itertools.count(1)

class AeroLockUser(HttpUser):
    host = "http://localhost:8000"
    # wait_time removed for pure stress testing

    def on_start(self):
        """
        Executed when a simulated user starts.
        Registers a new user and logs in to get a JWT token.
        """
        self.user_id = next(user_counter)
        unique_suffix = uuid.uuid4().hex[:8]
        self.user_email = f"locust_{run_id}_{self.user_id}_{unique_suffix}@example.com"
        self.user_password = "StrongPassword123!"
        self.token = None
        
        self.base_headers = {"X-Forwarded-For": f"203.0.113.{self.user_id % 255}"}
        
        # Register
        payload = {
            "email": self.user_email,
            "password": self.user_password,
            "first_name": "Locust",
            "last_name": "User"
        }
        with self.client.post("/api/v1/auth/register", json=payload, headers=self.base_headers, catch_response=True) as response:
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                response.success()
            else:
                response.failure(f"Registration failed: {response.text}")

    @task(1)
    def auth_login(self):
        payload = {
            "email": self.user_email,
            "password": self.user_password
        }
        with self.client.post("/api/v1/auth/login", json=payload, headers=self.base_headers, catch_response=True) as response:
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                response.success()
            else:
                response.failure(f"Login failed: {response.text}")



    @task(4)
    def search_flights(self):
        with self.client.get("/api/v1/search/?origin=CAI&destination=DXB&date=2024-12-01", headers=self.base_headers, catch_response=True, timeout=5) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Search failed with status {response.status_code}")

    @task(1)
    def book_flight(self):
        req_id = next(request_counter)
        flight_id = "00000000-0000-0000-0000-000000000000"
        seat_id = f"00000000-0000-0000-0000-{req_id:012d}" # Valid UUID format
        
        payload = {
            "flight_id": flight_id,
            "seat_id": seat_id
        }
        
        with self.client.post("/api/v1/booking/lock", json=payload, headers=self.base_headers, catch_response=True, timeout=5) as lock_response:
            if lock_response.status_code in (200, 404, 409, 429):
                lock_response.success()
            else:
                lock_response.failure(f"Lock failed with unexpected status {lock_response.status_code}")

        # Try to confirm
        try:
            lock_token = lock_response.json().get("token", "dummy-token-123") if lock_response.text else "dummy-token"
        except Exception:
            lock_token = "dummy-token-error"
            
        confirm_payload = {
            "seat_id": seat_id,
            "user_id": f"locust_{self.user_id}",
            "token": lock_token,
            "idempotency_key": f"idemp-{req_id}"
        }
        
        # Inject the JWT token for Auth!
        auth_headers = self.base_headers.copy()
        if self.token:
            auth_headers["Authorization"] = f"Bearer {self.token}"
            
        with self.client.post("/api/v1/booking/confirm", json=confirm_payload, headers=auth_headers, catch_response=True, timeout=5) as confirm_res:
            if confirm_res.status_code in (200, 400, 404, 409, 429):
                confirm_res.success()
            else:
                confirm_res.failure(f"Confirm failed with {confirm_res.status_code}")
