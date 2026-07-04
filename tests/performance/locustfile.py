from locust import HttpUser, task, between
import uuid

class AeroLockUser(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(1, 3)

    def on_start(self):
        """
        Executed when a simulated user starts.
        Registers a new user and logs in to get a JWT token.
        """
        self.user_email = f"locust_{uuid.uuid4().hex[:8]}@example.com"
        self.user_password = "StrongPassword123!"
        self.token = None
        
        headers = {"X-Forwarded-For": f"203.0.113.{uuid.uuid4().hex[:6]}"}
        
        # Register
        payload = {
            "email": self.user_email,
            "password": self.user_password,
            "first_name": "Locust",
            "last_name": "User"
        }
        with self.client.post("/api/v1/auth/register", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                response.success()
            else:
                response.failure(f"Registration failed: {response.text}")

    @task(1)
    def auth_login(self):
        """
        Simulate a user logging in. Weight: 1
        """
        headers = {"X-Forwarded-For": f"203.0.113.{uuid.uuid4().hex[:6]}"}
        payload = {
            "email": self.user_email,
            "password": self.user_password
        }
        with self.client.post("/api/v1/auth/login", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                response.success()
            else:
                response.failure(f"Login failed: {response.text}")

    @task(4)
    def search_flights(self):
        """
        Simulate a user searching for flights. Weight: 4
        """
        headers = {"X-Forwarded-For": f"203.0.113.{uuid.uuid4().hex[:6]}"}
        with self.client.get("/api/v1/search/?origin=CAI&destination=DXB&date=2024-12-01", headers=headers, catch_response=True, timeout=5) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Search failed with status {response.status_code}")

    @task(1)
    def book_flight(self):
        """
        Simulate a user locking and confirming a flight. Weight: 1
        Using dummy IDs to test API throughput and authentication.
        """
        flight_id = "00000000-0000-0000-0000-000000000000"
        seat_id = str(uuid.uuid4()) # Generate random seat to avoid hitting lock conflicts constantly
        
        payload = {
            "flight_id": flight_id,
            "seat_id": seat_id
        }
        headers = {"X-Forwarded-For": f"203.0.113.{uuid.uuid4().hex[:6]}"}
        
        with self.client.post("/api/v1/booking/lock", json=payload, headers=headers, catch_response=True, timeout=5) as lock_response:
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
            "user_id": f"locust_{uuid.uuid4()}",
            "token": lock_token,
            "idempotency_key": str(uuid.uuid4())
        }
        
        # Inject the JWT token for Auth!
        auth_headers = headers.copy()
        if self.token:
            auth_headers["Authorization"] = f"Bearer {self.token}"
            
        with self.client.post("/api/v1/booking/confirm", json=confirm_payload, headers=auth_headers, catch_response=True, timeout=5) as confirm_res:
            if confirm_res.status_code in (200, 400, 404, 409, 429):
                confirm_res.success()
            else:
                confirm_res.failure(f"Confirm failed with {confirm_res.status_code}")
