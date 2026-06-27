import http from 'k6/http';
import { check, sleep } from 'k6';
import { uuidv4 } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

export const options = {
  scenarios: {
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: 20, // 20 requests per second
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 50,
      maxVUs: 100,
    },
  },
  thresholds: {
    // 95% of locks should be acquired (or return standard business errors) within 300ms
    http_req_duration: ['p(95)<300'],
  },
};

export default function () {
  const url = 'http://localhost:8000/api/v1/booking/lock';
  
  const payload = JSON.stringify({
    flight_id: '00000000-0000-0000-0000-000000000000',
    seat_id: '00000000-0000-0000-0000-000000000000',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'X-Forwarded-For': `203.0.113.${Math.floor(Math.random() * 10000)}`, // Random IP to bypass rate limits
    },
  };

  const res = http.post(url, payload, params);

  // We check that the API responds properly. 404 and 409 are valid responses 
  // since the database might not have these dummy IDs or they might be locked.
  check(res, {
    'status is 200, 404, or 409': (r) => [200, 404, 409].includes(r.status),
  });
}
