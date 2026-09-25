// ============================================
// PRAHARI — MP Performance page logic
// ============================================

let activeTier = "all";
let selectedYear = "2025";
let trendChart = null;

function computeMpSummary(mp, year) {
  const y = mp.years[year];
  const score = mpYearScore(y);
  const tier = mpTierFromScore(score);
  return { ...mp, year, yearData: y, score, tier };
}

function renderMpGrid() {
  const grid = document.getElementById("mp-grid");
  const summaries = window.MOCK_MPS.map((mp) => computeMpSummary(mp, selectedYear)).sort(
    (a, b) => b.score - a.score
  );
  const filtered = activeTier === "all" ? summaries : summaries.filter((m) => m.tier === activeTier);

  grid.innerHTML = filtered
    .map(
      (m) => `
      <div class="mp-card" data-mpid="${m.mp_id}">
        <div class="mp-card-head">
          <span>
            <span class="name">${m.name}</span>
            <span class="place">${m.constituency}, ${m.state}</span>
          </span>
          <span class="badge ${m.tier}">${m.tier}</span>
        </div>
        <div class="mp-stats">
          <div>Completed: <b>${m.yearData.completed}</b></div>
          <div>Delayed: <b>${m.yearData.delayed}</b></div>
          <div>Utilization: <b>${m.yearData.utilization_pct}%</b></div>
          <div>Complaints: <b>${m.yearData.complaints}</b></div>
        </div>
      </div>`
    )
    .join("");

  grid.querySelectorAll(".mp-card").forEach((card) => {
    card.addEventListener("click", () => openMpDetail(card.dataset.mpid));
  });
}

function openMpDetail(mpId) {
  const mp = window.MOCK_MPS.find((m) => m.mp_id === mpId);
  const years = Object.keys(mp.years).sort();
  const scores = years.map((y) => mpYearScore(mp.years[y]));

  document.getElementById("mp-detail").hidden = false;
  document.getElementById("detail-name").textContent = `${mp.name} — ${mp.constituency}, ${mp.state}`;

  const current = mp.years[selectedYear];
  document.getElementById("detail-stats").innerHTML = `
    <div class="detail-stat"><span>Completed works (${selectedYear})</span><b>${current.completed}</b></div>
    <div class="detail-stat"><span>Ongoing works</span><b>${current.ongoing}</b></div>
    <div class="detail-stat"><span>Delayed works</span><b>${current.delayed}</b></div>
    <div class="detail-stat"><span>Fund utilization</span><b>${current.utilization_pct}%</b></div>
    <div class="detail-stat"><span>Average project risk</span><b>${current.avg_risk}</b></div>
    <div class="detail-stat"><span>Citizen complaints</span><b>${current.complaints}</b></div>
  `;

  const ctx = document.getElementById("mp-trend-chart");
  const data = {
    labels: years,
    datasets: [
      {
        label: "Performance score",
        data: scores,
        borderColor: "#1F5FA8",
        backgroundColor: "rgba(31,95,168,0.15)",
        tension: 0.3,
        fill: true
      }
    ]
  };
  if (trendChart) {
    trendChart.data = data;
    trendChart.update();
  } else {
    trendChart = new Chart(ctx, {
      type: "line",
      data,
      options: { scales: { y: { min: 0, max: 100 } }, plugins: { legend: { display: false } } }
    });
  }

  document.getElementById("mp-detail").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

document.getElementById("detail-close").addEventListener("click", () => {
  document.getElementById("mp-detail").hidden = true;
});

document.getElementById("tier-filters").addEventListener("click", (e) => {
  if (!e.target.matches(".tier-btn")) return;
  document.querySelectorAll(".tier-btn").forEach((b) => b.classList.remove("active"));
  e.target.classList.add("active");
  activeTier = e.target.dataset.tier;
  renderMpGrid();
});

document.getElementById("year-select").addEventListener("change", (e) => {
  selectedYear = e.target.value;
  renderMpGrid();
});

renderMpGrid();