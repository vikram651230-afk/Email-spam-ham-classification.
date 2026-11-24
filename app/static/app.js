const $ = (s) => document.querySelector(s);
const $$ = (s) => document.querySelectorAll(s);

const SAMPLES = [
  "WINNER!! As a valued network customer you have been selected to receive a £900 prize reward! To claim call 09061701461. Claim code KL341. Valid 12 hours only.",
  "Hey, are we still meeting for lunch tomorrow? Let me know what time works for you and I'll book a table.",
  "FREE entry into our weekly competition! Text WIN to 80086 now to claim your free ringtone. T&Cs apply, 18+ only. Reply STOP to opt out.",
  "Hi team, please find attached the agenda for Thursday's project review. Could you send me your updates before end of day Wednesday? Thanks!",
];

/* ---------- helpers ---------- */
async function api(path, opts) {
  const r = await fetch(path, opts);
  if (!r.ok) {
    let msg = "Request failed";
    try { const j = await r.json(); msg = typeof j.detail === "string" ? j.detail : "Invalid input."; } catch {}
    throw new Error(msg);
  }
  return r.json();
}
const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const pct = (x) => (x * 100).toFixed(x === 1 || x === 0 ? 0 : 1) + "%";
const busy = (btn, on) => { btn.disabled = on; btn.querySelector(".spin").classList.toggle("hidden", !on); };

/* ---------- tabs ---------- */
$$(".tab").forEach((t) => t.addEventListener("click", () => {
  $$(".tab").forEach((x) => x.classList.toggle("active", x === t));
  $$(".panel").forEach((p) => p.classList.toggle("active", p.id === "tab-" + t.dataset.tab));
  if (t.dataset.tab === "insights") loadInsights();
}));

/* ---------- health ---------- */
(async () => {
  const el = $("#status");
  try { await api("/api/health"); el.className = "status ok"; el.lastElementChild.textContent = "model online"; }
  catch { el.className = "status err"; el.lastElementChild.textContent = "offline"; }
})();

/* ---------- single check ---------- */
const input = $("#emailInput");
input.addEventListener("input", () => ($("#charCount").textContent = input.value.length));
$$(".chip").forEach((c) => c.addEventListener("click", () => {
  input.value = SAMPLES[c.dataset.sample]; input.dispatchEvent(new Event("input")); analyze();
}));
$("#clearBtn").addEventListener("click", () => {
  input.value = ""; input.dispatchEvent(new Event("input"));
  $("#result").classList.add("hidden"); $("#placeholder").classList.remove("hidden"); input.focus();
});
$("#analyzeBtn").addEventListener("click", analyze);
input.addEventListener("keydown", (e) => { if ((e.ctrlKey || e.metaKey) && e.key === "Enter") analyze(); });

const history = [];
function tags(list, cls) {
  return list.length ? list.map((w) => `<span class="tag ${cls}">${esc(w)}</span>`).join("") : '<span class="tag none">none detected</span>';
}

async function analyze() {
  const text = input.value.trim();
  if (!text) { input.focus(); return; }
  const btn = $("#analyzeBtn"); busy(btn, true);
  try {
    const r = await api("/api/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) });
    showResult(r);
    history.unshift({ text, label: r.label, p: r.spam_probability });
    if (history.length > 8) history.pop();
    renderHistory();
  } catch (e) { alert(e.message); }
  finally { busy(btn, false); }
}

function showResult(r) {
  const spam = r.label === "spam";
  $("#placeholder").classList.add("hidden"); $("#result").classList.remove("hidden");
  $("#verdict").className = "verdict " + (spam ? "spam" : "ham");
  $("#vIcon").textContent = spam ? "🚨" : "✅";
  $("#vLabel").textContent = spam ? "SPAM" : "HAM (Legitimate)";
  $("#vSub").textContent = `${pct(r.confidence)} confidence`;
  $("#pctText").textContent = `${pct(r.spam_probability)} spam probability`;
  requestAnimationFrame(() => ($("#barFill").style.left = Math.min(98, Math.max(2, r.spam_probability * 100)) + "%"));
  $("#spamSignals").innerHTML = tags(r.spam_signals, "s");
  $("#hamSignals").innerHTML = tags(r.ham_signals, "h");
  $("#termsMeta").textContent = r.known_terms === 0
    ? "⚠️ No words from the model vocabulary were found — treat this result with caution."
    : `${r.known_terms} recognised terms analysed.`;
}

function renderHistory() {
  $("#historyEmpty").classList.toggle("hidden", history.length > 0);
  $("#historyList").innerHTML = history.map((h, i) =>
    `<li data-i="${i}"><span class="pill ${h.label}">${h.label}</span><span class="txt">${esc(h.text)}</span><span class="muted">${pct(h.p)}</span></li>`).join("");
}
$("#historyList").addEventListener("click", (e) => {
  const li = e.target.closest("li"); if (!li) return;
  input.value = history[li.dataset.i].text; input.dispatchEvent(new Event("input")); analyze();
  window.scrollTo({ top: 0, behavior: "smooth" });
});
$("#clearHistory").addEventListener("click", () => { history.length = 0; renderHistory(); });
renderHistory();

/* ---------- batch ---------- */
$("#fileInput").addEventListener("change", async (e) => {
  const f = e.target.files[0]; if (!f) return;
  const fd = new FormData(); fd.append("file", f);
  const btn = $("#batchBtn"); busy(btn, true);
  try { showBatch(await api("/api/predict-file", { method: "POST", body: fd })); }
  catch (err) { alert(err.message); } finally { busy(btn, false); e.target.value = ""; }
});
$("#batchBtn").addEventListener("click", async () => {
  const emails = $("#batchInput").value.split("\n").map((s) => s.trim()).filter(Boolean);
  if (!emails.length) return;
  const btn = $("#batchBtn"); busy(btn, true);
  try {
    showBatch(await api("/api/predict-batch", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ emails: emails.slice(0, 200) }) }));
  } catch (e) { alert(e.message); } finally { busy(btn, false); }
});
function showBatch(d) {
  $("#batchOut").classList.remove("hidden");
  $("#bTotal").textContent = d.total; $("#bSpam").textContent = d.spam; $("#bHam").textContent = d.ham;
  $("#batchRows").innerHTML = d.results.map((r, i) =>
    `<tr><td>${i + 1}</td><td class="msg" title="${esc(r.preview)}">${esc(r.preview)}</td><td><span class="pill ${r.label}">${r.label}</span></td><td>${pct(r.spam_probability)}</td></tr>`).join("");
}

/* ---------- insights ---------- */
let loaded = false;
async function loadInsights() {
  if (loaded) return;
  try {
    const d = await api("/api/insights"); loaded = true;
    $("#metricStats").innerHTML = [
      ["Accuracy", d.accuracy], ["Spam precision", d.spam_precision], ["Spam recall", d.spam_recall], ["Spam F1-score", d.spam_f1],
    ].map(([k, v]) => `<div class="stat"><b>${pct(v)}</b><span>${k}</span></div>`).join("");
    const c = d.confusion_matrix;
    $("#cm").innerHTML = `
      <div></div><div class="h">Predicted spam</div><div class="h">Predicted ham</div>
      <div class="h">Actual<br>spam</div><div class="cell ok"><b>${c.true_spam_pred_spam}</b>caught</div><div class="cell no"><b>${c.true_spam_pred_ham}</b>missed</div>
      <div class="h">Actual<br>ham</div><div class="cell no"><b>${c.true_ham_pred_spam}</b>false alarm</div><div class="cell ok"><b>${c.true_ham_pred_ham}</b>correct</div>`;
    const kv = (k, v) => `<div class="kv"><span>${k}</span><span>${v}</span></div>`;
    $("#dataInfo").innerHTML = kv("Algorithm", d.algorithm) + kv("Features", d.features) +
      kv("Total emails", d.dataset.total) + kv("Spam / Ham", `${d.dataset.spam} / ${d.dataset.ham}`) + kv("Test set size", d.test_size);
    $("#topSpam").innerHTML = d.top_spam_words.map((w) => `<span class="tag s">${esc(w)}</span>`).join("");
    $("#topHam").innerHTML = d.top_ham_words.map((w) => `<span class="tag h">${esc(w)}</span>`).join("");
  } catch (e) { $("#metricStats").innerHTML = `<p class="muted">Could not load insights: ${esc(e.message)}</p>`; }
}
