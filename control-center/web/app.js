const cards = document.querySelector('#agents');
const filter = document.querySelector('#filter');
const select = document.querySelector('#agent-id');
const count = document.querySelector('#count');
let agents = [];
const render = () => {
  const q = filter.value.toLowerCase().trim();
  const shown = agents.filter(a => JSON.stringify(a).toLowerCase().includes(q));
  count.textContent = `${shown.length} de ${agents.length}`;
  cards.innerHTML = shown.map(a => `<article class="card"><span class="tag">${a.status}</span><span class="tag">riesgo ${a.risk}</span><h2>${a.name}</h2><p>${a.description}</p><small>${a.id} · ${a.category}</small></article>`).join('');
};
fetch('/api/agents').then(r => r.json()).then(data => {
  agents = data.agents;
  select.innerHTML = agents.map(a => `<option value="${a.id}">${a.name}</option>`).join('');
  render();
}).catch(error => { cards.textContent = `No fue posible cargar el catálogo: ${error}`; });
// Qué puede ejecutar estos contratos aquí. El panel solo informa: no ejecuta.
fetch('/api/runtimes').then(r => r.json()).then(data => {
  document.querySelector('#runtimes').innerHTML = data.runtimes.map(rt =>
    `<span class="tag">${rt.id} · ${rt.available ? 'disponible' : 'no instalado'} · ${rt.maturity}</span>`).join(' ');
}).catch(error => { document.querySelector('#runtimes').textContent = `Runtimes no disponibles: ${error}`; });
filter.addEventListener('input', render);
document.querySelector('#plan-form').addEventListener('submit', async event => {
  event.preventDefault();
  const payload = {agent_id: select.value, task: document.querySelector('#task').value, target: document.querySelector('#target').value || null};
  const response = await fetch('/api/plan', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  document.querySelector('#plan-output').textContent = JSON.stringify(await response.json(), null, 2);
});
