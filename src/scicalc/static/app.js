const screen = document.getElementById("screen");
const keys = document.querySelector(".keys");
const equalsBtn = document.getElementById("equals");

let expr = "";

function render(v) { screen.textContent = v || "0"; }
function append(v) { expr += v; render(expr); }
function backspace() { expr = expr.slice(0, -1); render(expr); }
function clearAll() { expr = ""; render(expr); }

async function evaluateExpr() {
  if (!expr.trim()) return;
  equalsBtn.disabled = true;
  try {
    const res = await fetch("/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expression: expr })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data?.error || `HTTP ${res.status}`);
    expr = String(data.result);
    render(expr);
  } catch (e) {
    render(`Error: ${e.message}`);
  } finally {
    equalsBtn.disabled = false;
  }
}

const actions = { backspace, clear: clearAll, equals: evaluateExpr };

keys.addEventListener("click", (e) => {
  const t = e.target.closest("button");
  if (!t) return;
  if (t.dataset.val) return append(t.dataset.val);
  const fn = actions[t.dataset.act];
  if (fn) fn();
});

const keyActions = { Enter: evaluateExpr, Backspace: backspace, Escape: clearAll };

document.addEventListener("keydown", (e) => {
  if (/[0-9+\-*/().]/.test(e.key)) { append(e.key); return; }
  const fn = keyActions[e.key];
  if (fn) { e.preventDefault(); fn(); }
});
