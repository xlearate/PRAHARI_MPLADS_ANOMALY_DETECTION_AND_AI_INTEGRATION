// Mock MP data — shaped for future backend replacement, same pattern as mockProjects.js.
// "years" holds yearly aggregates used for tiering and trend charts.

window.MOCK_MPS = [
  {
    mp_id: "MP-014",
    name: "R. Sharma",
    state: "Bihar",
    constituency: "Bhagalpur",
    years: {
      2023: { completed: 6, ongoing: 3, delayed: 4, utilization_pct: 71, avg_risk: 58, complaints: 5 },
      2024: { completed: 8, ongoing: 4, delayed: 5, utilization_pct: 68, avg_risk: 63, complaints: 7 },
      2025: { completed: 5, ongoing: 6, delayed: 6, utilization_pct: 74, avg_risk: 69, complaints: 9 }
    }
  },
  {
    mp_id: "MP-027",
    name: "A. Verma",
    state: "Uttar Pradesh",
    constituency: "Kanpur Dehat",
    years: {
      2023: { completed: 10, ongoing: 2, delayed: 1, utilization_pct: 88, avg_risk: 34, complaints: 1 },
      2024: { completed: 11, ongoing: 3, delayed: 2, utilization_pct: 91, avg_risk: 30, complaints: 2 },
      2025: { completed: 9, ongoing: 4, delayed: 1, utilization_pct: 93, avg_risk: 27, complaints: 1 }
    }
  },
  {
    mp_id: "MP-039",
    name: "S. Iyer",
    state: "Tamil Nadu",
    constituency: "Madurai",
    years: {
      2023: { completed: 7, ongoing: 5, delayed: 3, utilization_pct: 76, avg_risk: 45, complaints: 3 },
      2024: { completed: 7, ongoing: 6, delayed: 4, utilization_pct: 79, avg_risk: 49, complaints: 4 },
      2025: { completed: 8, ongoing: 5, delayed: 3, utilization_pct: 81, avg_risk: 46, complaints: 2 }
    }
  },
  {
    mp_id: "MP-052",
    name: "K. Nair",
    state: "Kerala",
    constituency: "Kollam",
    years: {
      2023: { completed: 12, ongoing: 1, delayed: 0, utilization_pct: 95, avg_risk: 15, complaints: 0 },
      2024: { completed: 13, ongoing: 2, delayed: 1, utilization_pct: 96, avg_risk: 13, complaints: 0 },
      2025: { completed: 11, ongoing: 3, delayed: 0, utilization_pct: 97, avg_risk: 11, complaints: 1 }
    }
  }
];

// Composite performance score (0-100), higher is better.
// Weighs completion mix, fund utilization, average risk and complaints.
function mpYearScore(y) {
  const totalWorks = y.completed + y.ongoing + y.delayed;
  const completionMix = totalWorks ? (y.completed / totalWorks) * 100 : 0;
  const raw =
    completionMix * 0.35 +
    y.utilization_pct * 0.30 +
    (100 - y.avg_risk) * 0.25 -
    y.complaints * 2;
  return Math.max(0, Math.min(100, Math.round(raw)));
}

function mpTierFromScore(score) {
  if (score >= 70) return "good";
  if (score >= 45) return "moderate";
  return "worse";
}