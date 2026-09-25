// Mock data — shaped exactly like the future backend response.
// When the real API is ready, only js/api.js changes, never this shape.

window.MOCK_PROJECTS = [
  {
    project_id: "P-1042",
    name: "Community Health Sub-Centre",
    mp: "R. Sharma",
    district: "Bhagalpur, Bihar",
    sanctioned_amount: 4200000,
    expenditure: 3950000,
    completion_percentage: 62,
    status: "Ongoing",
    risk_score: 88,
    anomaly_type: "Payment without matching progress",
    severity: "high",
    factors: ["94% of funds spent", "Only 62% physical progress", "No site photo update in 5 months"]
  },
  {
    project_id: "P-1017",
    name: "Rural Road Widening — Ward 9",
    mp: "A. Verma",
    district: "Kanpur Dehat, UP",
    sanctioned_amount: 6800000,
    expenditure: 6800000,
    completion_percentage: 40,
    status: "Delayed",
    risk_score: 81,
    anomaly_type: "Cost overrun vs. category baseline",
    severity: "high",
    factors: ["Cost 38% above similar roads", "Completion behind schedule by 7 months"]
  },
  {
    project_id: "P-0988",
    name: "Community Hall Construction",
    mp: "S. Iyer",
    district: "Madurai, TN",
    sanctioned_amount: 2500000,
    expenditure: 900000,
    completion_percentage: 15,
    status: "Ongoing",
    risk_score: 64,
    anomaly_type: "Slow fund utilization",
    severity: "moderate",
    factors: ["Only 36% of funds used", "Nearing installment deadline"]
  },
  {
    project_id: "P-1101",
    name: "Drinking Water Pipeline Ext.",
    mp: "R. Sharma",
    district: "Bhagalpur, Bihar",
    sanctioned_amount: 3100000,
    expenditure: 1550000,
    completion_percentage: 50,
    status: "Ongoing",
    risk_score: 47,
    anomaly_type: "Minor progress-expenditure gap",
    severity: "moderate",
    factors: ["Progress and spend broadly aligned", "One missed monthly report"]
  },
  {
    project_id: "P-0876",
    name: "Solar Street Lighting Phase II",
    mp: "K. Nair",
    district: "Kollam, Kerala",
    sanctioned_amount: 1800000,
    expenditure: 1750000,
    completion_percentage: 96,
    status: "Near completion",
    risk_score: 12,
    anomaly_type: "None detected",
    severity: "low",
    factors: ["Spend and progress consistent", "On schedule"]
  },
  {
    project_id: "P-0912",
    name: "Primary School Renovation",
    mp: "A. Verma",
    district: "Kanpur Dehat, UP",
    sanctioned_amount: 1200000,
    expenditure: 1180000,
    completion_percentage: 100,
    status: "Completed",
    risk_score: 9,
    anomaly_type: "None detected",
    severity: "low",
    factors: ["Completed on budget", "Verified via geotagged photos"]
  },
  {
    project_id: "P-1055",
    name: "Irrigation Canal Repair",
    mp: "S. Iyer",
    district: "Madurai, TN",
    sanctioned_amount: 3900000,
    expenditure: 3900000,
    completion_percentage: 55,
    status: "Ongoing",
    risk_score: 73,
    anomaly_type: "Full disbursement, incomplete work",
    severity: "high",
    factors: ["100% funds released", "Only 55% work completed", "2 citizen complaints filed"]
  }
];