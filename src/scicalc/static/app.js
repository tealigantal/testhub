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

keys.addEventListener("click", (e) => {
  const t = e.target.closest("button"); if (!t) return;
  const val = t.dataset.val, act = t.dataset.act;
  if (val) return append(val);
  if (act === "backspace") return backspace();
  if (act === "clear") return clearAll();
  if (act === "equals") return evaluateExpr();
});

document.addEventListener("keydown", (e) => {
  if (/[0-9+\-*/().]/.test(e.key)) { append(e.key); return; }
  if (e.key === "Enter") { e.preventDefault(); evaluateExpr(); }
  if (e.key === "Backspace") { e.preventDefault(); backspace(); }
  if (e.key === "Escape") { e.preventDefault(); clearAll(); }
});
