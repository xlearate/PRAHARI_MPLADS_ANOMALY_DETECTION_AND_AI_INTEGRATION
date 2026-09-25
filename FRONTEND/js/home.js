// ============================================
// PRAHARI — home page logic
// ============================================

let riskChart = null; // Chart.js instance, re-used across refreshes

// ---------- Splash ----------
function dismissSplash() {
  document.getElementById("splash").classList.add("hide");
}
document.getElementById("splash").addEventListener("click", dismissSplash);
window.addEventListener("load", () => setTimeout(dismissSplash, 1600));

// ---------- Scroll reveal ----------
const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) entry.target.classList.add("in-view");
    });
  },
  { threshold: 0.15 }
);
document.querySelectorAll(".section").forEach((el) => revealObserver.observe(el));

// ---------- Rendering: Anomaly table ----------
function renderAnomalyTable(projects) {
  const sorted = [...projects].sort((a, b) => b.risk_score - a.risk_score);
  const tbody = document.getElementById("anomaly-table-body");
  tbody.innerHTML = sorted
    .map((p, i) => {
      const severity = severityFromScore(p.risk_score);
      return `
        <tr>
          <td class="rank-cell">#${i + 1}</td>
          <td>
            <span class="project-name">${p.name}</span>
            <span class="project-sub">${p.project_id}</span>
          </td>
          <td>
            ${p.mp}
            <span class="project-sub">${p.district}</span>
          </td>
          <td>${p.anomaly_type}</td>
          <td><span class="badge ${severity}">${severity}</span></td>
          <td class="score-cell">${p.risk_score}</td>
        </tr>`;
    })
    .join("");
}

// ---------- Rendering: Risk chart + explanation cards ----------
function renderRiskSection(projects) {
  const top = [...projects].sort((a, b) => b.risk_score - a.risk_score).slice(0, 5);

  const ctx = document.getElementById("risk-chart");
  const colors = top.map((p) => {
    const sev = severityFromScore(p.risk_score);
    return sev === "high" ? "#C0392B" : sev === "moderate" ? "#D98E3D" : "#1AA6A0";
  });

  const chartData = {
    labels: top.map((p) => p.project_id),
    datasets: [{ label: "Risk score", data: top.map((p) => p.risk_score), backgroundColor: colors }]
  };

  if (riskChart) {
    riskChart.data = chartData;
    riskChart.update();
  } else {
    riskChart = new Chart(ctx, {
      type: "bar",
      data: chartData,
      options: {
        indexAxis: "y",
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { x: { min: 0, max: 100 } }
      }
    });
  }

  const explainWrap = document.getElementById("risk-explanations");
  explainWrap.innerHTML = top
    .slice(0, 3)
    .map((p) => {
      const severity = severityFromScore(p.risk_score);
      return `
        <div class="explain-card ${severity}">
          <div class="explain-head">
            <span class="name">${p.name}</span>
            <span class="score-cell">${p.risk_score}</span>
          </div>
          <div class="factor-chips">
            ${p.factors.map((f) => `<span class="chip">${f}</span>`).join("")}
          </div>
        </div>`;
    })
    .join("");
}

// ---------- Refresh cycle ----------
function updateTimestamp() {
  const now = new Date().toLocaleTimeString();
  document.getElementById("last-updated").textContent = now;
  document.getElementById("footer-updated").textContent = `Last synced ${now}`;
}

async function refreshAll() {
  const projects = await getProjects();
  renderAnomalyTable(projects);
  renderRiskSection(projects);
  updateTimestamp();
}

document.getElementById("refresh-btn").addEventListener("click", refreshAll);

// Initial load, then auto-refresh every 20s to simulate live incoming data
refreshAll();
setInterval(refreshAll, 20000);