const API_BASE = '/api';

export async function getPistas() {
  const res = await fetch(`${API_BASE}/pistas`);
  return res.json();
}

export async function getCoches() {
  const res = await fetch(`${API_BASE}/coches`);
  return res.json();
}

export async function evolucionar(params) {
  const res = await fetch(`${API_BASE}/evolucionar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  return res.json();
}
