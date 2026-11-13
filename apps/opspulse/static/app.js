/* OpsPulse dashboard client — polls the JSON API and re-renders. */

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const hm = (ts) => (ts || "").slice(11, 16); // HH:MM
const dt = (ts) => (ts || "").slice(5, 16).replace(" ", " ");
let filter = "open";

async function j(url) { const r = await fetch(url); return r.json(); }

/* ---------- charts ---------- */
function lineChart(el, labels, values, color) {
  const W = 640, H = 160, P = { l: 34, r: 8, t: 10, b: 18 };
  if (!labels.length) { el.innerHTML = `<text x="10" y="80" class="axis-text">no data</text>`; return; }
  const max = Math.max(5, ...values) * 1.15;
  const x = (i) => P.l + (i / Math.max(1, labels.length - 1)) * (W - P.l - P.r);
  const y = (v) => H - P.b - (v / max) * (H - P.t - P.b);
  const pts = values.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const area = `${P.l},${y(0)} ` + pts + ` ${x(values.length - 1).toFixed(1)},${y(0)}`;
  const ticks = [0, .25, .5, .75, 1].map(f => {
    const v = max * f, yy = y(v);
    return `<line x1="${P.l}" x2="${W - P.r}" y1="${yy}" y2="${yy}" stroke="rgba(0,0,0,.06)"/>
            <text x="${P.l - 4}" y="${yy + 3}" text-anchor="end" class="axis-text">${Math.round(v)}%</text>`;
  }).join("");
  const xl = labels.filter((_, i) => i % Math.ceil(labels.length / 6) === 0)
    .map((l) => `<text x="${x(labels.indexOf(l))}" y="${H - 4}" text-anchor="middle" class="axis-text">${hm(l)}</text>`).join("");
  el.innerHTML = `${ticks}
    <polygon points="${area}" fill="${color}" opacity="0.12"/>
    <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="1.6"/>
    ${xl}`;
}

function stackedBars(el, labels, errors, warnings, infos) {
  const W = 640, H = 160, P = { l: 34, r: 8, t: 10, b: 18 };
  if (!labels.length) { el.innerHTML = `<text x="10" y="80" class="axis-text">no data</text>`; return; }
  const max = Math.max(4, ...labels.map((_, i) => errors[i] + warnings[i] + infos[i])) * 1.1;
  const bw = Math.max(2, (W - P.l - P.r) / labels.length - 2);
  const x = (i) => P.l + i * ((W - P.l - P.r) / labels.length);
  const y = (v) => H - P.b - (v / max) * (H - P.t - P.b);
  let out = "";
  labels.forEach((l, i) => {
    const e = errors[i], w = warnings[i], n = infos[i];
    const yE = y(e), yW = y(e + w), yN = y(e + w + n);
    out += `<rect x="${x(i)}" y="${yN}" width="${bw}" height="${yW - yN}" fill="rgba(49,124,255,.30)"/>`;
    out += `<rect x="${x(i)}" y="${yW}" width="${bw}" height="${yE - yW}" fill="rgba(183,119,0,.55)"/>`;
    out += `<rect x="${x(i)}" y="${yE}" width="${bw}" height="${(H - P.b) - yE}" fill="#D92D20"/>`;
  });
  const xl = labels.filter((_, i) => i % Math.ceil(labels.length / 6) === 0)
    .map((l) => `<text x="${x(labels.indexOf(l)) + bw / 2}" y="${H - 4}" text-anchor="middle" class="axis-text">${hm(l)}</text>`).join("");
  el.innerHTML = out + xl;
}

/* ---------- render ---------- */
async function renderSummary() {
  const s = await j("/api/summary");
  $("#stat-open").textContent = s.open_incidents;
  $("#stat-open-sub").textContent = `${s.total_incidents} tracked total`;
  $("#stat-rate").textContent = s.error_rate + "%";
  $("#stat-deploys").textContent = s.deploys;
  $("#stat-events").textContent = s.events;
  $("#stat-window").textContent = "through " + (s.log_window_end || "").slice(5, 16);
  $("#sources").textContent = s.sources.join(", ");
  const t = s.last_refresh ? new Date(s.last_refresh) : null;
  $("#last-refresh").textContent = t ? t.toLocaleTimeString() : "—";
}

async function renderSeries() {
  const s = await j("/api/series");
  lineChart($("#chart-rate"), s.labels, s.error_rate, "#D92D20");
  const infos = s.total.map((t, i) => t - s.errors[i] - s.warnings[i]);
  stackedBars($("#chart-vol"), s.labels, s.errors, s.warnings, infos);
}

function incidentCard(i) {
  const meta = [
    `<span class="mono">×${i.count}</span>`,
    `<span>${i.component}</span>`,
    i.tenants.length ? `<span>${i.tenants.length} tenant${i.tenants.length > 1 ? "s" : ""}</span>` : "",
    i.implicated_file ? `<span class="mono" title="${esc(i.implicated_file)}">${esc(i.implicated_file.split("/").pop())}</span>` : "",
  ].filter(Boolean).join("");
  return `<div class="incident" data-id="${i.id}">
    <div class="incident-head">
      <span class="sev ${i.severity}">${i.severity}</span>
      <div>
        <div class="inc-title">${esc(i.title)}</div>
        <div class="inc-meta">${meta}
          <span>owner <b>${esc(i.owner)}</b> <span class="muted" title="${esc(i.owner_source)}">(${esc(i.owner_source)})</span></span>
          <span>${hm(i.first_seen)}–${hm(i.last_seen)}</span>
        </div>
      </div>
      <span class="status ${i.status}">${i.status}</span>
    </div>
    <div class="timeline"></div>
  </div>`;
}

async function renderIncidents() {
  const all = await j("/api/incidents");
  const list = filter === "all" ? all : all.filter((i) => i.status === filter);
  $("#incidents").innerHTML = list.length
    ? list.map(incidentCard).join("")
    : `<div class="muted" style="padding:12px">No ${filter} incidents.</div>`;
  document.querySelectorAll(".incident-head").forEach((h) =>
    h.addEventListener("click", () => toggleIncident(h.parentElement)));
}

async function toggleIncident(el) {
  el.classList.toggle("expanded");
  const tl = el.querySelector(".timeline");
  if (!el.classList.contains("expanded") || tl.dataset.loaded) return;
  const d = await j(`/api/incident?id=${el.dataset.id}`);
  tl.dataset.loaded = "1";
  const kindLabel = { detected: "detected", recurrence: "recurrence", recovery: "recovery", status: "status" };
  tl.innerHTML = d.timeline.map((t) =>
    `<div class="tl-item">
       <span class="tl-ts">${hm(t.ts)}</span>
       <span class="tl-dot ${t.kind}"></span>
       <div class="tl-detail"><span class="tl-kind">${kindLabel[t.kind] || t.kind}</span> ${esc(t.detail)}</div>
     </div>`).join("");
}

async function renderDeploys() {
  const rows = await j("/api/deploys");
  $("#deploys tbody").innerHTML = rows.map((d) =>
    `<tr>
      <td class="mono">${esc(d.version)}<br><span class="sha">${esc(d.sha)}</span></td>
      <td>${esc(d.subject)}</td>
      <td>${esc(d.author)}</td>
      <td class="num">${d.files_changed}</td>
      <td class="mono">${esc((d.ts || "").slice(5, 16).replace("T", " "))}</td>
      <td><span class="pill-deployed">● ${d.status}</span></td>
    </tr>`).join("");
}

async function refreshAll() {
  try {
    await Promise.all([renderSummary(), renderSeries(), renderIncidents(), renderDeploys()]);
  } catch (e) { console.error(e); }
}

document.querySelectorAll(".chip").forEach((c) =>
  c.addEventListener("click", () => {
    document.querySelectorAll(".chip").forEach((x) => x.classList.remove("active"));
    c.classList.add("active");
    filter = c.dataset.f;
    renderIncidents();
  }));

refreshAll();
setInterval(refreshAll, 30000);
