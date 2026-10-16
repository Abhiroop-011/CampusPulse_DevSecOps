/**
 * Thin API client that uses relative /api/... paths.
 * In development, Vite proxies /api → http://localhost:8000
 * In Docker/K8s, Nginx routes /api → backend service.
 */

const BASE = '';  // relative — never hardcode backend host

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── Stats ────────────────────────────────────────────────────
export const getStats = () => request('/api/stats');

// ── Clubs ────────────────────────────────────────────────────
export const getClubs = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return request(`/api/clubs${qs ? '?' + qs : ''}`);
};

// ── Events ───────────────────────────────────────────────────
export const getEvents = (params = {}) => {
  const qs = new URLSearchParams(params).toString();
  return request(`/api/events${qs ? '?' + qs : ''}`);
};

export const getEvent = (id) => request(`/api/events/${id}`);

export const createEvent = (data) =>
  request('/api/events', { method: 'POST', body: JSON.stringify(data) });

export const updateEvent = (id, data) =>
  request(`/api/events/${id}`, { method: 'PUT', body: JSON.stringify(data) });

export const deleteEvent = (id) =>
  request(`/api/events/${id}`, { method: 'DELETE' });

// ── Registrations ────────────────────────────────────────────
export const registerForEvent = (eventId, data) =>
  request(`/api/events/${eventId}/registrations`, {
    method: 'POST',
    body: JSON.stringify(data),
  });

export const cancelRegistration = (eventId, regId) =>
  request(`/api/events/${eventId}/registrations/${regId}`, { method: 'DELETE' });

export const getRegistrations = (eventId) =>
  request(`/api/events/${eventId}/registrations`);
