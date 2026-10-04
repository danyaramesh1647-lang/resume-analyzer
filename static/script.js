const $ = (id) => document.getElementById(id);
const fileInput = $("file");
const drop = $("drop");
const btn = $("analyze");
let lastText = "";

fileInput.addEventListener("change", () => setFile(fileInput.files[0]));
["dragenter", "dragover"].forEach((ev) =>
  drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("over"); })
);
["dragleave", "drop"].forEach((ev) =>
  drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("over"); })
);
drop.addEventListener("drop", (e) => {
  const f = e.dataTransfer.files[0];
  if (f) { fileInput.files = e.dataTransfer.files; setFile(f); }
});
drop.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fileInput.click(); }
});
btn.addEventListener("click", analyze);
$("copy").addEventListener("click", copyResults);

function setFile(f) {
  $("error").hidden = true;
  if (!f) return;
  $("drop-title").textContent = f.name;
  $("drop-sub").textContent = `${(f.size / 1024).toFixed(0)} KB. Click Analyze resume.`;
  btn.disabled = false;
}

async function analyze() {
  const f = fileInput.files[0];
  if (!f) return;
  const fd = new FormData();
  fd.append("resume", f);
  $("error").hidden = true;
  btn.disabled = true;
  btn.textContent = "Analyzing...";
  try {
    const res = await fetch("/analyze", { method: "POST", body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Something went wrong.");
    render(data);
  } catch (err) {
    $("result").hidden = true;
    $("error").textContent = err.message;
    $("error").hidden = false;
  } finally {
    btn.disabled = false;
    btn.textContent = "Analyze resume";
  }
}

function render(d) {
  $("result").hidden = false;
  const tone = d.score >= 75 ? "var(--good)" : d.score >= 50 ? "var(--mid)" : "var(--low)";
  $("result").style.setProperty("--tone", tone);
  $("score").textContent = d.score;
  $("verdict").textContent = d.score >= 75 ? "Strong resume" : d.score >= 50 ? "Good start, needs polish" : "Needs work";
  $("meta").textContent = `${d.stats.words} words, ${d.stats.pages} page${d.stats.pages > 1 ? "s" : ""}`;
  requestAnimationFrame(() => {
    $("arc").style.strokeDashoffset = 326.7 * (1 - d.score / 100);
  });

  const bd = $("breakdown");
  bd.innerHTML = "";
  d.breakdown.forEach((b) => {
    const row = document.createElement("div");
    row.innerHTML = `<span>${b.name}</span><div class="bar"><i style="width:${(b.got / b.max) * 100}%"></i></div><b>${b.got}/${b.max}</b>`;
    bd.appendChild(row);
  });

  $("skill-count").textContent = `(${d.skill_count})`;
  const sk = $("skills");
  sk.innerHTML = "";
  Object.entries(d.skills).forEach(([cat, list]) => {
    const wrap = document.createElement("div");
    wrap.className = "cat";
    wrap.innerHTML = `<p>${cat}</p>`;
    const ul = document.createElement("ul");
    ul.className = "chips";
    list.forEach((s) => {
      const li = document.createElement("li");
      li.className = "chip";
      li.textContent = s;
      ul.appendChild(li);
    });
    wrap.appendChild(ul);
    sk.appendChild(wrap);
  });
  if (!d.skill_count) sk.textContent = "No technical skills detected.";

  fill("keywords", d.keywords);
  fill("suggestions", d.suggestions);

  lastText = [
    "RESUME ANALYSIS", "",
    "Skills Found:", ...Object.values(d.skills).flat().map((s) => "✓ " + s), "",
    "Keywords:", d.keywords.join(" • "), "",
    "Resume Score:", `${d.score} / 100`, "",
    "Suggestions:", ...d.suggestions.map((s) => "• " + s),
  ].join("\n");
  $("copy").textContent = "Copy results";
}

function fill(id, items) {
  const ul = $(id);
  ul.innerHTML = "";
  items.forEach((t) => {
    const li = document.createElement("li");
    li.textContent = t;
    ul.appendChild(li);
  });
}

async function copyResults() {
  try {
    await navigator.clipboard.writeText(lastText);
    $("copy").textContent = "Copied";
  } catch {
    $("copy").textContent = "Copy failed";
  }
  setTimeout(() => ($("copy").textContent = "Copy results"), 1800);
}