import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 50 }, // Ramp up to 50 users over 10s
    { duration: '30s', target: 50 }, // Stay at 50 users for 30s
    { duration: '10s', target: 0 },  // Ramp down to 0 users over 10s
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'], // 95% of requests should be below 200ms
    http_req_failed: ['rate<0.01'],   // Error rate should be less than 1%
  },
};

export default function () {
  // Use a random IP to bypass basic rate limiting in tests if needed,
  // or let rate limits be tested by not randomizing.
  const headers = { 'X-Forwarded-For': `203.0.113.${__VU}` };

  const res = http.get('http://localhost:8000/api/v1/search/?origin=CAI&destination=DXB&date=2024-12-01', {
    headers: headers,
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
    'status is not 429': (r) => r.status !== 429,
  });

  sleep(1);
}
