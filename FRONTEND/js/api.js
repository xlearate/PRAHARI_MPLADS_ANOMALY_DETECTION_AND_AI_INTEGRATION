// ============================================
// PRAHARI — data access layer
//
// Every page calls getProjects() and nothing else.
// Right now it resolves mock data with a small simulated
// delay and a bit of jitter (standing in for "newly verified
// data just came in"). Once the real backend exists, replace
// ONLY the inside of this function with:
//
//   const res = await fetch("http://localhost:8000/projects");
//   return await res.json();
//
// Every page/table/chart that calls getProjects() keeps working
// unchanged, because the shape of the returned data doesn't change.
// ============================================

async function getProjects() {
  await new Promise((resolve) => setTimeout(resolve, 250)); // simulated network delay

  // Simulate "continuously updated verified data": jitter each
  // project's risk_score slightly so re-fetching looks live in a demo.
  // Remove this jitter once real data is wired in.
  return window.MOCK_PROJECTS.map((p) => {
    const jitter = Math.round((Math.random() - 0.5) * 6); // +/-3 points
    const newScore = Math.max(0, Math.min(100, p.risk_score + jitter));
    return { ...p, risk_score: newScore };
  });
}

// Shared helper: turn a numeric score into a severity band + CSS class.
// Used by every page so risk always looks the same everywhere.
function severityFromScore(score) {
  if (score >= 70) return "high";
  if (score >= 40) return "moderate";
  return "low";
}