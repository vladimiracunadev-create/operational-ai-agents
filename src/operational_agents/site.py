"""Generador de la landing page publicada en GitHub Pages.

La página se deriva del catálogo igual que el resto de vistas: si alguien
añade un agente y no vuelve a ejecutar `sync`, CI falla. Ninguna cifra de la
landing se escribe a mano.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

REPO = "https://github.com/vladimiracunadev-create/operational-ai-agents"

RISK_LABEL = {"low": "riesgo bajo", "medium": "riesgo medio", "high": "riesgo alto"}

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='8' fill='%238b5cf6'/%3E"
    "%3Crect x='8' y='11' width='16' height='12' rx='3' fill='%23fff'/%3E"
    "%3Ccircle cx='13' cy='17' r='1.8' fill='%238b5cf6'/%3E"
    "%3Ccircle cx='19' cy='17' r='1.8' fill='%238b5cf6'/%3E"
    "%3Crect x='15' y='6' width='2' height='5' rx='1' fill='%23fff'/%3E"
    "%3C/svg%3E"
)


def _e(value: object) -> str:
    return html.escape(str(value), quote=True)


def site_stats(root: Path, catalog: dict[str, Any]) -> dict[str, int]:
    """Cifras verificables leídas del propio repositorio."""
    evals = 0
    for agent in catalog["agents"]:
        path = root / "agents" / agent["id"] / "evals" / "cases.jsonl"
        evals += sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    tests = (root / "tests" / "test_repository.py").read_text(encoding="utf-8").count("    def test_")
    return {"agentes": len(catalog["agents"]), "evaluaciones": evals, "pruebas": tests}


def _agent_card(agent: dict[str, Any]) -> str:
    phases = "".join(
        f"<li>{_e(phase.replace('-', ' '))}</li>" for phase in agent["phases"]
    )
    tools = "".join(f"<code>{_e(tool)}</code>" for tool in agent["tools"])
    scenarios = "".join(
        f"<li><b>{_e(item['title'])}</b>"
        f"<span class=\"scn__sit\">{_e(item['context'])}</span>"
        f"<span class=\"scn__ask\">«{_e(item['ask'])}»</span>"
        f"<span class=\"scn__get\">→ {_e(item['status'])}</span></li>"
        for item in agent["scenarios"]
    )
    # El buscador indexa también los escenarios: la gente busca su problema
    # («el README no coincide»), no la categoría del contrato.
    haystack = " ".join([
        agent["name"], agent["id"], agent["category"], agent["description"],
        *(f"{s['title']} {s['context']} {s['ask']}" for s in agent["scenarios"]),
    ]).lower()
    return f"""        <article class="card" data-search="{_e(haystack)}">
          <header class="card__head">
            <span class="card__icon" aria-hidden="true">{_e(agent['icon'])}</span>
            <div>
              <h3>{_e(agent['name'])}</h3>
              <p class="card__id"><code>{_e(agent['id'])}</code></p>
            </div>
          </header>
          <p class="card__mission">{_e(agent['description'])}</p>
          <p class="card__ask">Le escribes: <q>{_e(agent['scenarios'][0]['ask'])}</q></p>
          <ul class="chips">
            <li class="chip chip--risk-{_e(agent['risk'])}">{_e(RISK_LABEL.get(agent['risk'], agent['risk']))}</li>
            <li class="chip">permisos <code>{_e(agent['permission_mode'])}</code></li>
            <li class="chip">{_e(agent['category'])}</li>
          </ul>
          <details>
            <summary>Cuándo lo necesitas · {len(agent['scenarios'])} ejemplos</summary>
            <ul class="scn">{scenarios}</ul>
          </details>
          <details>
            <summary>Flujo y capacidades</summary>
            <p class="detail-title">Fases</p>
            <ol class="phases">{phases}</ol>
            <p class="detail-title">Tools</p>
            <p class="tools">{tools}</p>
            <p class="detail-title">Se detiene y pregunta antes de</p>
            <ul class="gates">{''.join(f'<li>{_e(gate)}</li>' for gate in agent['approval_points'])}</ul>
          </details>
          <a class="card__link" href="{REPO}/blob/main/agents/{_e(agent['id'])}/README.md">
            Ver contrato completo <span aria-hidden="true">→</span>
          </a>
        </article>"""


def render_landing(catalog: dict[str, Any], stats: dict[str, int]) -> str:
    cards = "\n".join(_agent_card(agent) for agent in catalog["agents"])
    version = catalog["repository_version"]
    maturity_rows = "\n".join(
        f"          <tr><td><code>{_e(state)}</code></td><td>{_e(description)}</td>"
        f"<td class=\"num\">{stats['agentes'] if state == 'IMPLEMENTED' else 0}</td></tr>"
        for state, description in catalog["maturity_model"].items()
    )
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark light">
<title>Operational AI Agents · agentes operativos con evidencia verificable</title>
<meta name="description" content="Colección de {stats['agentes']} agentes operativos reutilizables: reciben una misión completa, respetan gates humanos y entregan evidencia verificable. Contratos versionados y adaptador para Claude Code.">
<link rel="canonical" href="https://vladimiracunadev-create.github.io/operational-ai-agents/">
<link rel="icon" href="{FAVICON}">
<meta property="og:type" content="website">
<meta property="og:title" content="Operational AI Agents">
<meta property="og:description" content="{stats['agentes']} agentes operativos que reciben una misión completa, respetan gates humanos y entregan evidencia verificable.">
<meta property="og:url" content="https://vladimiracunadev-create.github.io/operational-ai-agents/">
<meta name="twitter:card" content="summary_large_image">
<!-- Página generada por `operational-agents sync` desde catalog/agents.yaml. No editar a mano. -->
<style>
*,*::before,*::after{{box-sizing:border-box}}
:root{{
  --bg:#07101f; --bg-soft:#0b1527; --panel:#111c31; --line:#2a3c5c;
  --text:#e8ecf5; --muted:#9badc8; --accent:#8b5cf6; --accent-soft:#c4b5fd;
  --ok:#34d399; --warn:#fbbf24; --danger:#f87171;
  --radius:18px; --shadow:0 20px 55px rgba(0,0,0,.28);
  --font:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
}}
@media (prefers-color-scheme:light){{
  :root{{
    --bg:#f6f8ff; --bg-soft:#eef2f8; --panel:#fff; --line:#cad4e5;
    --text:#172033; --muted:#52647f; --accent:#7c3aed; --accent-soft:#5b21b6;
    --ok:#047857; --warn:#a16207; --danger:#b91c1c;
    --shadow:0 18px 45px rgba(23,32,51,.10);
  }}
}}
html{{scroll-behavior:smooth}}
body{{
  margin:0; font-family:var(--font); color:var(--text); line-height:1.65;
  background:radial-gradient(ellipse 80% 60% at 75% -10%,rgba(139,92,246,.22),transparent 60%),var(--bg);
  -webkit-font-smoothing:antialiased;
}}
.wrap{{width:min(1140px,92vw);margin-inline:auto}}
a{{color:var(--accent-soft);text-decoration-thickness:1px;text-underline-offset:3px}}
code{{font-family:var(--mono);font-size:.88em}}
h1,h2,h3{{line-height:1.15;letter-spacing:-.025em;margin:0}}
:focus-visible{{outline:2px solid var(--accent);outline-offset:3px;border-radius:6px}}
.skip{{position:absolute;left:-9999px}}
.skip:focus{{left:1rem;top:1rem;z-index:99;background:var(--panel);padding:.7rem 1rem;border-radius:10px;border:1px solid var(--line)}}

/* ---------- nav ---------- */
.nav{{position:sticky;top:0;z-index:20;backdrop-filter:blur(12px);
  background:color-mix(in srgb,var(--bg) 82%,transparent);border-bottom:1px solid var(--line)}}
.nav__in{{display:flex;align-items:center;gap:1.5rem;padding:.85rem 0}}
.nav__brand{{display:flex;align-items:center;gap:.6rem;font-weight:800;letter-spacing:-.03em;color:var(--text);text-decoration:none}}
.nav__dot{{width:26px;height:26px;border-radius:8px;background:linear-gradient(135deg,var(--accent),#6366f1);
  display:grid;place-items:center;font-size:.9rem}}
.nav__links{{display:flex;gap:1.25rem;margin-left:auto;font-size:.92rem;flex-wrap:wrap}}
.nav__links a{{color:var(--muted);text-decoration:none}}
.nav__links a:hover{{color:var(--text)}}
@media(max-width:720px){{.nav__links a:not(.btn--sm){{display:none}}}}

/* ---------- hero ---------- */
.hero{{padding:clamp(3rem,9vw,6.5rem) 0 3rem}}
.eyebrow{{color:var(--accent-soft);font-weight:800;letter-spacing:.18em;font-size:.76rem;text-transform:uppercase;margin:0 0 1rem}}
.hero h1{{font-size:clamp(2.4rem,6.5vw,4.6rem);font-weight:850;letter-spacing:-.055em;max-width:16ch}}
.hero__lead{{font-size:clamp(1.05rem,2.2vw,1.3rem);color:var(--muted);max-width:62ch;margin:1.4rem 0 0}}
.hero__lead strong{{color:var(--text);font-weight:650}}
.cta{{display:flex;gap:.8rem;flex-wrap:wrap;margin:2.2rem 0 0}}
.btn{{display:inline-flex;align-items:center;gap:.5rem;padding:.8rem 1.4rem;border-radius:12px;
  font-weight:700;text-decoration:none;border:1px solid transparent;transition:transform .15s,filter .15s}}
.btn:hover{{transform:translateY(-2px)}}
.btn--primary{{background:linear-gradient(135deg,var(--accent),#6366f1);color:#fff}}
.btn--ghost{{border-color:var(--line);color:var(--text);background:var(--panel)}}
.btn--sm{{padding:.45rem .9rem;font-size:.88rem}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1px;margin:3.2rem 0 0;
  background:var(--line);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden}}
.stat{{background:var(--panel);padding:1.25rem 1.4rem}}
.stat b{{display:block;font-size:clamp(1.7rem,4vw,2.3rem);font-weight:850;letter-spacing:-.04em;
  background:linear-gradient(135deg,var(--accent-soft),var(--accent));-webkit-background-clip:text;background-clip:text;color:transparent}}
.stat span{{color:var(--muted);font-size:.86rem}}

/* ---------- secciones ---------- */
section{{padding:clamp(3rem,7vw,5rem) 0;scroll-margin-top:70px}}
.sec-head{{max-width:64ch;margin:0 0 2.5rem}}
.sec-head h2{{font-size:clamp(1.7rem,3.6vw,2.5rem);font-weight:800}}
.sec-head p{{color:var(--muted);margin:.9rem 0 0;font-size:1.03rem}}
.rule{{border:0;border-top:1px solid var(--line);margin:0}}

/* ---------- terminal ---------- */
.term{{border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;background:var(--bg-soft);box-shadow:var(--shadow)}}
.term__bar{{display:flex;align-items:center;gap:.45rem;padding:.7rem 1rem;border-bottom:1px solid var(--line);background:var(--panel)}}
.term__bar i{{width:11px;height:11px;border-radius:50%;background:var(--line)}}
.term__bar span{{margin-left:auto;color:var(--muted);font-size:.78rem;font-family:var(--mono)}}
.term pre{{margin:0;padding:1.3rem;overflow-x:auto;font-family:var(--mono);font-size:.87rem;line-height:1.85}}
.term .p{{color:var(--accent-soft);user-select:none}}
.term .c{{color:var(--muted)}}
.copy{{position:absolute;top:.6rem;right:.6rem}}
.term-wrap{{position:relative}}
.copy button{{font:inherit;font-size:.78rem;padding:.35rem .7rem;border-radius:8px;cursor:pointer;
  border:1px solid var(--line);background:var(--panel);color:var(--muted)}}
.copy button:hover{{color:var(--text)}}

/* ---------- comparativa ---------- */
.table-wrap{{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);background:var(--panel)}}
table{{border-collapse:collapse;width:100%;min-width:560px}}
th,td{{text-align:left;padding:.85rem 1.1rem;border-bottom:1px solid var(--line);font-size:.95rem}}
thead th{{background:var(--bg-soft);font-size:.8rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}}
tbody tr:last-child td{{border-bottom:0}}
td.num{{text-align:right;font-family:var(--mono);font-weight:700}}
.yes{{color:var(--ok);font-weight:700}}

/* ---------- catálogo ---------- */
.filter{{display:flex;gap:.8rem;align-items:center;flex-wrap:wrap;margin:0 0 1.8rem}}
.filter input{{font:inherit;flex:1;min-width:240px;padding:.75rem 1rem;border-radius:12px;
  border:1px solid var(--line);background:var(--panel);color:var(--text)}}
.filter output{{color:var(--muted);font-size:.9rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:1.1rem}}
.card{{border:1px solid var(--line);border-radius:var(--radius);padding:1.4rem;background:var(--panel);
  box-shadow:var(--shadow);display:flex;flex-direction:column;gap:.9rem;transition:transform .18s,border-color .18s}}
.card:hover{{transform:translateY(-3px);border-color:var(--accent)}}
.card[hidden]{{display:none}}
.card__head{{display:flex;gap:.9rem;align-items:flex-start}}
.card__icon{{font-size:1.7rem;line-height:1}}
.card h3{{font-size:1.08rem;font-weight:750}}
.card__id{{margin:.25rem 0 0}}
.card__id code{{color:var(--muted);font-size:.78rem}}
.card__mission{{margin:0;color:var(--muted);font-size:.93rem;flex:1}}
.card__ask{{margin:0;font-size:.88rem;color:var(--text);border-left:2px solid var(--accent);padding-left:.7rem}}
.card__ask q{{color:var(--accent-soft);font-style:italic}}
.scn{{list-style:none;margin:.6rem 0 0;padding:0;display:grid;gap:.85rem}}
.scn li{{display:grid;gap:.2rem;font-size:.85rem}}
.scn b{{color:var(--text);font-size:.88rem}}
.scn__sit{{color:var(--muted)}}
.scn__ask{{color:var(--accent-soft);font-style:italic}}
.scn__get{{color:var(--muted)}}
.chips{{display:flex;flex-wrap:wrap;gap:.4rem;list-style:none;padding:0;margin:0}}
.chip{{font-size:.74rem;padding:.22rem .6rem;border-radius:999px;border:1px solid var(--line);color:var(--muted)}}
.chip code{{color:inherit}}
.chip--risk-low{{color:var(--ok);border-color:color-mix(in srgb,var(--ok) 45%,transparent)}}
.chip--risk-medium{{color:var(--warn);border-color:color-mix(in srgb,var(--warn) 45%,transparent)}}
.chip--risk-high{{color:var(--danger);border-color:color-mix(in srgb,var(--danger) 45%,transparent)}}
details{{border-top:1px solid var(--line);padding-top:.8rem}}
summary{{cursor:pointer;font-size:.86rem;color:var(--muted);font-weight:600}}
summary:hover{{color:var(--text)}}
.detail-title{{font-size:.72rem;text-transform:uppercase;letter-spacing:.09em;color:var(--muted);margin:.9rem 0 .35rem}}
.phases{{margin:0;padding-left:1.2rem;font-size:.85rem;color:var(--muted);columns:2;gap:1rem}}
.gates{{margin:0;padding-left:1.2rem;font-size:.85rem;color:var(--muted)}}
.tools{{margin:0;display:flex;flex-wrap:wrap;gap:.3rem}}
.tools code{{font-size:.75rem;padding:.15rem .45rem;border-radius:6px;background:var(--bg-soft);border:1px solid var(--line)}}
.card__link{{font-size:.88rem;font-weight:650;text-decoration:none;margin-top:auto}}
.card__link:hover{{text-decoration:underline}}

/* ---------- flujo ---------- */
.flow{{border:1px solid var(--line);border-radius:var(--radius);background:var(--panel);padding:1.5rem;overflow-x:auto;box-shadow:var(--shadow)}}
.flow svg{{display:block;width:100%;min-width:640px;height:auto}}
.flow-legend{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:1.1rem;margin:1.8rem 0 0}}
.flow-legend div{{border-left:2px solid var(--accent);padding-left:.9rem}}
.flow-legend b{{display:block;font-size:.95rem}}
.flow-legend p{{margin:.25rem 0 0;color:var(--muted);font-size:.89rem}}

/* ---------- notas ---------- */
.note{{border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:12px;
  background:var(--panel);padding:1.1rem 1.3rem;margin:1.8rem 0 0;color:var(--muted);font-size:.95rem}}
.note b{{color:var(--text)}}

/* ---------- docs ---------- */
.links{{display:grid;grid-template-columns:repeat(auto-fill,minmax(255px,1fr));gap:.9rem}}
.links a{{display:block;border:1px solid var(--line);border-radius:14px;padding:1.05rem 1.2rem;
  background:var(--panel);text-decoration:none;color:var(--text);transition:border-color .18s,transform .18s}}
.links a:hover{{border-color:var(--accent);transform:translateY(-2px)}}
.links b{{display:block;font-size:.97rem}}
.links span{{color:var(--muted);font-size:.86rem}}

/* ---------- footer ---------- */
footer{{border-top:1px solid var(--line);padding:2.5rem 0 3.5rem;color:var(--muted);font-size:.9rem}}
.foot{{display:flex;justify-content:space-between;gap:1.5rem;flex-wrap:wrap;align-items:center}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important;scroll-behavior:auto!important}}}}
</style>
</head>
<body>
<a class="skip" href="#catalogo">Saltar al catálogo</a>

<nav class="nav">
  <div class="wrap nav__in">
    <a class="nav__brand" href="#top"><span class="nav__dot" aria-hidden="true">🤖</span> operational-ai-agents</a>
    <div class="nav__links">
      <a href="#que-es">Qué es</a>
      <a href="#instalacion">Instalación</a>
      <a href="#catalogo">Catálogo</a>
      <a href="#como-funciona">Cómo funciona</a>
      <a href="#seguridad">Seguridad</a>
      <a class="btn btn--ghost btn--sm" href="{REPO}">GitHub ↗</a>
    </div>
  </div>
</nav>

<header class="hero wrap" id="top">
  <p class="eyebrow">Catálogo contractual · v{_e(version)}</p>
  <h1>Agentes que responden por un resultado, no por un prompt.</h1>
  <p class="hero__lead">
    {stats['agentes']} agentes operativos reutilizables. Cada uno recibe una <strong>misión completa</strong>,
    decide su propia secuencia de trabajo, usa capacidades dentro de límites declarados,
    <strong>se detiene en gates humanos</strong> y entrega <strong>evidencia verificable</strong>.
  </p>
  <div class="cta">
    <a class="btn btn--primary" href="#instalacion">Instalar en 4 líneas</a>
    <a class="btn btn--ghost" href="#catalogo">Ver los {stats['agentes']} agentes</a>
    <a class="btn btn--ghost" href="{REPO}">Código en GitHub ↗</a>
  </div>
  <div class="stats">
    <div class="stat"><b>{stats['agentes']}</b><span>agentes con contrato</span></div>
    <div class="stat"><b>{stats['evaluaciones']}</b><span>evaluaciones deterministas</span></div>
    <div class="stat"><b>{stats['pruebas']}</b><span>pruebas automatizadas</span></div>
    <div class="stat"><b>0</b><span>dependencias runtime</span></div>
  </div>
</header>

<hr class="rule">

<section id="que-es" class="wrap">
  <div class="sec-head">
    <h2>Un skill no es un agente</h2>
    <p>
      La diferencia no es de tamaño, es de responsabilidad. Un skill aporta una capacidad dentro
      de tu contexto actual. Un agente abre un contexto propio, sostiene una misión y responde
      por el resultado completo — incluidos sus límites.
    </p>
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Dimensión</th><th>Skill</th><th>Agente operativo</th></tr></thead>
      <tbody>
        <tr><td>Contexto</td><td>el de la sesión actual</td><td>separado y propio</td></tr>
        <tr><td>Alcance</td><td>una capacidad concreta</td><td>una misión completa</td></tr>
        <tr><td>Decisión</td><td>la toma quien lo invoca</td><td>la toma el agente dentro de límites</td></tr>
        <tr><td>Permisos</td><td>heredados</td><td>allowlist declarada por contrato</td></tr>
        <tr><td>Cierre</td><td>devuelve un resultado</td><td>responde por evidencia y riesgos residuales</td></tr>
      </tbody>
    </table>
  </div>
  <p class="note">
    <b>Vendor-neutral en el núcleo.</b> El catálogo, las políticas, los schemas y las evaluaciones
    no dependen de ningún proveedor. Claude Code es el primer adaptador, no un requisito del contrato.
  </p>
</section>

<hr class="rule">

<section id="instalacion" class="wrap">
  <div class="sec-head">
    <h2>Instalación</h2>
    <p>Python 3.11 o superior. No necesitas clave API para validar contratos, generar planes,
       ejecutar las evaluaciones ni abrir el panel local.</p>
  </div>
  <div class="term-wrap">
    <div class="copy"><button type="button" id="copy-install">Copiar</button></div>
    <div class="term">
      <div class="term__bar"><i></i><i></i><i></i><span>bash</span></div>
<pre id="install-code"><span class="p">$</span> git clone {REPO}.git
<span class="p">$</span> cd operational-ai-agents
<span class="p">$</span> python -m pip install -e .
<span class="p">$</span> operational-agents validate <span class="c"># OK: {stats['agentes']} agentes válidos</span></pre>
    </div>
  </div>
  <div class="flow-legend">
    <div><b>Explora sin gastar tokens</b><p><code>plan</code> genera la secuencia completa de fases y gates de forma determinista, sin invocar ningún modelo.</p></div>
    <div><b>Instala en Claude Code</b><p><code>export claude</code> proyecta los contratos a <code>~/.claude/agents/</code> sin sobrescribir agentes que no administra.</p></div>
    <div><b>Panel local</b><p><code>serve</code> levanta el control center en loopback para explorar contratos desde el navegador.</p></div>
  </div>
</section>

<hr class="rule">

<section id="catalogo" class="wrap">
  <div class="sec-head">
    <h2>Catálogo</h2>
    <p>Todos los agentes se generan desde una única fuente de verdad —<code>catalog/agents.yaml</code>—
       y CI rechaza cualquier divergencia entre el catálogo, los manifiestos y esta misma página.</p>
  </div>
  <div class="filter">
    <label class="skip" for="q">Filtrar agentes</label>
    <input id="q" type="search" placeholder="Filtrar por nombre, categoría o misión…" autocomplete="off">
    <output id="count" for="q">{stats['agentes']} agentes</output>
  </div>
  <div class="grid" id="grid">
{cards}
  </div>
</section>

<hr class="rule">

<section id="como-funciona" class="wrap">
  <div class="sec-head">
    <h2>Cómo funciona</h2>
    <p>Ninguna fase asume la autorización de la anterior. El agente inspecciona primero,
       propone después y sólo muta cuando existe una decisión humana explícita.</p>
  </div>
  <div class="flow">
    <svg viewBox="0 0 900 200" role="img" aria-label="Flujo: objetivo, inspección, plan, gate humano, ejecución y evidencia verificada">
      <defs>
        <marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
          <path d="M0 0 10 5 0 10z" fill="currentColor" opacity=".55"/>
        </marker>
        <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="#8b5cf6"/><stop offset="100%" stop-color="#6366f1"/>
        </linearGradient>
      </defs>
      <g font-family="var(--font)" font-size="13" text-anchor="middle" color="currentColor">
        <g stroke="currentColor" stroke-width="1.5" marker-end="url(#a)" opacity=".55">
          <line x1="132" y1="80" x2="168" y2="80"/><line x1="272" y1="80" x2="308" y2="80"/>
          <line x1="412" y1="80" x2="448" y2="80"/><line x1="552" y1="80" x2="588" y2="80"/>
          <line x1="692" y1="80" x2="728" y2="80"/>
        </g>
        <g>
          <rect x="12" y="52" width="120" height="56" rx="12" fill="var(--bg-soft)" stroke="var(--line)"/>
          <text x="72" y="77" fill="currentColor" font-weight="700">Misión</text>
          <text x="72" y="94" fill="var(--muted)" font-size="11">del usuario</text>
        </g>
        <g>
          <rect x="168" y="52" width="104" height="56" rx="12" fill="var(--bg-soft)" stroke="var(--line)"/>
          <text x="220" y="77" fill="currentColor" font-weight="700">Inspección</text>
          <text x="220" y="94" fill="var(--muted)" font-size="11">solo lectura</text>
        </g>
        <g>
          <rect x="308" y="52" width="104" height="56" rx="12" fill="var(--bg-soft)" stroke="var(--line)"/>
          <text x="360" y="77" fill="currentColor" font-weight="700">Plan</text>
          <text x="360" y="94" fill="var(--muted)" font-size="11">determinista</text>
        </g>
        <g>
          <rect x="448" y="46" width="104" height="68" rx="12" fill="url(#g)" stroke="none"/>
          <text x="500" y="74" fill="#fff" font-weight="800">Gate</text>
          <text x="500" y="92" fill="#fff" font-size="11" opacity=".9">decisión humana</text>
        </g>
        <g>
          <rect x="588" y="52" width="104" height="56" rx="12" fill="var(--bg-soft)" stroke="var(--line)"/>
          <text x="640" y="77" fill="currentColor" font-weight="700">Ejecución</text>
          <text x="640" y="94" fill="var(--muted)" font-size="11">acotada</text>
        </g>
        <g>
          <rect x="728" y="52" width="160" height="56" rx="12" fill="var(--bg-soft)" stroke="var(--line)"/>
          <text x="808" y="77" fill="currentColor" font-weight="700">Evidencia</text>
          <text x="808" y="94" fill="var(--muted)" font-size="11">verificada</text>
        </g>
        <g opacity=".8">
          <path d="M500 122 L500 150 L220 150 L220 114" fill="none" stroke="currentColor"
                stroke-width="1.5" stroke-dasharray="4 4" marker-end="url(#a)"/>
          <text x="360" y="168" fill="var(--muted)" font-size="11">si se deniega o falta autorización, vuelve a inspección</text>
        </g>
      </g>
    </svg>
  </div>
  <div class="flow-legend">
    <div><b>Read-only primero</b><p>Las fases iniciales sólo inspeccionan. Las mutaciones llegan después del alcance y del plan.</p></div>
    <div><b>Acceso ≠ autorización</b><p>Poder leer un repositorio no autoriza publicar, desplegar, borrar ni rotar credenciales.</p></div>
    <div><b>Aprobación real</b><p>Otro agente no puede aprobar en tu lugar, y una aprobación acotada no habilita fases posteriores.</p></div>
  </div>
</section>

<hr class="rule">

<section id="seguridad" class="wrap">
  <div class="sec-head">
    <h2>Seguridad verificada, no prometida</h2>
    <p>Cada garantía de esta tabla está cubierta por una prueba automatizada que corre en cada push,
       no sólo por un párrafo de documentación.</p>
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Control</th><th>Garantía</th><th>En CI</th></tr></thead>
      <tbody>
        <tr><td>Ejecución de procesos</td><td>la CLI no usa <code>shell=True</code> ni añade flags que omitan permisos</td><td class="yes">sí</td></tr>
        <tr><td>Agentes que mutan</td><td><code>permissionMode: default</code> e <code>isolation: worktree</code></td><td class="yes">sí</td></tr>
        <tr><td>Agentes de solo lectura</td><td><code>Write</code> y <code>Edit</code> en la lista de tools denegadas</td><td class="yes">sí</td></tr>
        <tr><td>Panel local</td><td>escucha en loopback; el bind externo exige una variable explícita</td><td class="yes">sí</td></tr>
        <tr><td>Evidencia</td><td>opt-in y con redacción de secretos antes de persistir</td><td class="yes">sí</td></tr>
        <tr><td>Instalación</td><td>el exportador nunca sobrescribe un agente que no administra</td><td class="yes">sí</td></tr>
      </tbody>
    </table>
  </div>
</section>

<hr class="rule">

<section id="madurez" class="wrap">
  <div class="sec-head">
    <h2>Madurez honesta</h2>
    <p>Ningún agente se presenta como productivo sólo porque su Markdown sea válido.
       Esta es la posición real del catálogo hoy.</p>
  </div>
  <div class="table-wrap">
    <table>
      <thead><tr><th>Estado</th><th>Requisito mínimo</th><th>Hoy</th></tr></thead>
      <tbody>
{maturity_rows}
      </tbody>
    </table>
  </div>
  <p class="note">
    <b>Qué significa esto.</b> Los {stats['agentes']} agentes declaran <code>IMPLEMENTED</code>: contrato,
    instrucciones, schemas y evaluaciones validados localmente. Eso demuestra integridad del paquete,
    <b>no</b> adopción productiva. La promoción de estado exige evidencia real y revisada.
  </p>
</section>

<hr class="rule">

<section id="docs" class="wrap">
  <div class="sec-head">
    <h2>Documentación</h2>
    <p>Todo el proyecto es inspeccionable sin ejecutar nada.</p>
  </div>
  <div class="links">
    <a href="{REPO}#readme"><b>README</b><span>catálogo, arquitectura y uso</span></a>
    <a href="{REPO}/blob/main/docs/CLI.md"><b>Referencia de CLI</b><span>comandos, flags y códigos de retorno</span></a>
    <a href="{REPO}/blob/main/docs/ARCHITECTURE.md"><b>Arquitectura</b><span>límites, componentes y flujos</span></a>
    <a href="{REPO}/blob/main/docs/AGENT_CONTRACT.md"><b>Contrato de agente</b><span>anatomía e invariantes</span></a>
    <a href="{REPO}/blob/main/docs/SECURITY_MODEL.md"><b>Modelo de seguridad</b><span>permisos, amenazas y gates</span></a>
    <a href="{REPO}/blob/main/docs/MATURITY_MODEL.md"><b>Modelo de madurez</b><span>criterios de promoción</span></a>
    <a href="{REPO}/blob/main/docs/EVALUATION.md"><b>Evaluación</b><span>capas deterministas y model-graded</span></a>
    <a href="{REPO}/blob/main/CONTRIBUTING.md"><b>Contribuir</b><span>cómo proponer un agente nuevo</span></a>
  </div>
</section>

<footer>
  <div class="wrap foot">
    <div>
      <b>operational-ai-agents</b> · MIT © 2026
      <a href="https://github.com/vladimiracunadev-create">Vladimir Acuña</a>
    </div>
    <div>Evidencia sobre apariencia · aprobación humana · cero dependencias runtime</div>
  </div>
</footer>

<script>
(function () {{
  var input = document.getElementById('q');
  var count = document.getElementById('count');
  var cards = Array.prototype.slice.call(document.querySelectorAll('#grid .card'));
  if (input) {{
    input.addEventListener('input', function () {{
      var term = input.value.trim().toLowerCase();
      var shown = 0;
      cards.forEach(function (card) {{
        var match = !term || card.dataset.search.indexOf(term) !== -1;
        card.hidden = !match;
        if (match) shown++;
      }});
      count.textContent = shown + (shown === 1 ? ' agente' : ' agentes');
    }});
  }}
  var button = document.getElementById('copy-install');
  if (button && navigator.clipboard) {{
    button.addEventListener('click', function () {{
      var lines = document.getElementById('install-code').innerText
        .split('\\n')
        .map(function (line) {{ return line.replace(/^\\$\\s?/, '').replace(/\\s*#.*$/, ''); }})
        .filter(Boolean)
        .join('\\n');
      navigator.clipboard.writeText(lines).then(function () {{
        button.textContent = 'Copiado';
        setTimeout(function () {{ button.textContent = 'Copiar'; }}, 1800);
      }});
    }});
  }}
}})();
</script>
</body>
</html>
"""
