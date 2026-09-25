// ============================================
// PRAHARI — Citizen Feedback page logic
//
// Submissions are stored in localStorage for now (so the list survives
// a reload during a demo). Once the backend exists, replace saveReport()
// and loadReports() with POST/GET calls to the feedback API — the form
// and rendering logic don't need to change.
// ============================================

const STORAGE_KEY = "prahari_feedback_reports";

// ---------- Populate dropdowns from shared mock data ----------
function populateStateDropdown() {
  const states = [...new Set(window.MOCK_MPS.map((mp) => mp.state))].sort();
  const select = document.getElementById("state-select");
  states.forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s;
    select.appendChild(opt);
  });
}

function populateMpDropdown() {
  const select = document.getElementById("mp-select");
  window.MOCK_MPS.forEach((mp) => {
    const opt = document.createElement("option");
    opt.value = mp.mp_id;
    opt.textContent = `${mp.name} — ${mp.constituency}, ${mp.state}`;
    select.appendChild(opt);
  });
}

function populateWorkDropdown() {
  const select = document.getElementById("work-select");
  window.MOCK_PROJECTS.forEach((p) => {
    const opt = document.createElement("option");
    opt.value = p.project_id;
    opt.textContent = `${p.name} (${p.project_id})`;
    select.appendChild(opt);
  });
}

// When an MP is picked, auto-select their state (still editable, just a convenience)
document.getElementById("mp-select").addEventListener("change", (e) => {
  const mp = window.MOCK_MPS.find((m) => m.mp_id === e.target.value);
  if (mp) document.getElementById("state-select").value = mp.state;
});

// ---------- Storage ----------
function loadReports() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}
function saveReport(report) {
  const reports = loadReports();
  reports.unshift(report);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(reports));
}

// ---------- Render submitted reports ----------
function renderReports() {
  const reports = loadReports();
  const list = document.getElementById("reports-list");

  if (reports.length === 0) {
    list.innerHTML = `<p class="report-empty">No reports submitted yet.</p>`;
    return;
  }

  list.innerHTML = reports
    .map((r) => {
      const mp = window.MOCK_MPS.find((m) => m.mp_id === r.mpId);
      const work = window.MOCK_PROJECTS.find((p) => p.project_id === r.workId);
      const when = new Date(r.createdAt).toLocaleString();
      return `
        <div class="report-card">
          <div class="report-head">
            <span>Reported by <b>${r.citizenName}</b></span>
            <span>${r.issueType} · ${when}</span>
          </div>
          <div class="report-head">
            <span>MP: <b>${mp ? mp.name : r.mpId}</b></span>
            <span>State: <b>${r.state}</b></span>
            <span>Work: <b>${work ? work.name : r.workId}</b></span>
          </div>
          <p class="report-desc">${r.description}</p>
        </div>`;
    })
    .join("");
}

// ---------- Form submit ----------
document.getElementById("feedback-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const form = e.target;
  const msg = document.getElementById("form-msg");

  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const report = {
    citizenName: form.citizenName.value.trim(),
    citizenContact: form.citizenContact.value.trim(),
    state: form.state.value,
    mpId: form.mp.value,
    workId: form.work.value,
    issueType: form.issueType.value,
    description: form.description.value.trim(),
    createdAt: new Date().toISOString()
  };

  saveReport(report);
  renderReports();

  form.reset();
  msg.textContent = "Report submitted. It has been added to this project's risk signals.";
  msg.className = "form-msg success";
  msg.hidden = false;
  setTimeout(() => (msg.hidden = true), 4000);
});

// ---------- Init ----------
populateStateDropdown();
populateMpDropdown();
populateWorkDropdown();
renderReports();