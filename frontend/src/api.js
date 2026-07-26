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

export async function telemetriaIniciar() {
  const res = await fetch(`${API_BASE}/telemetria/iniciar`, { method: 'POST' });
  return res.json();
}

export async function telemetriaDetener() {
  const res = await fetch(`${API_BASE}/telemetria/detener`, { method: 'POST' });
  return res.json();
}

export async function telemetriaEstado() {
  const res = await fetch(`${API_BASE}/telemetria/estado`);
  return res.json();
}

export async function calibrar(params) {
  const res = await fetch(`${API_BASE}/calibrar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Error al calibrar');
  return data;
}
