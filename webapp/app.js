/* ═══════════════════════════════════════════════════════════════════════
   Attendance Checker — Static Web App Logic (Improved Version)
   All data persisted via localStorage.
   ═══════════════════════════════════════════════════════════════════════ */

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const STORAGE_KEY = "attendance_checker_store_v2"; // New key to avoid conflicts with old format

// ─── Data Layer ────────────────────────────────────────────────────────
function defaultProfile() {
  const tt = {};
  DAYS.forEach(d => tt[d] = []); // Now an array of subjects in order
  return { 
    subjects: [], 
    timetable: tt, 
    semester_end: "", 
    attendance: {},
    extra_today: [] // Temporarily store extra classes for today
  };
}

function defaultStore() {
  return {
    active_profile: "Student 1",
    profiles: { "Student 1": defaultProfile() }
  };
}

function loadStore() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      // Try to migrate from v1 if it exists
      const oldRaw = localStorage.getItem("attendance_checker_store");
      if (oldRaw) {
        const oldData = JSON.parse(oldRaw);
        // Basic migration attempt
        const store = defaultStore();
        for (const [name, oldProf] of Object.entries(oldData.profiles)) {
          const newProf = defaultProfile();
          newProf.subjects = oldProf.subjects || [];
          newProf.semester_end = oldProf.semester_end || "";
          newProf.attendance = oldProf.attendance || {};
          // Attempt to convert old timetable {subj: count} to [subj, subj]
          if (oldProf.timetable) {
            DAYS.forEach(day => {
              const dayData = oldProf.timetable[day] || {};
              for (const [subj, count] of Object.entries(dayData)) {
                for(let i=0; i<count; i++) newProf.timetable[day].push(subj);
              }
            });
          }
          store.profiles[name] = newProf;
        }
        store.active_profile = oldData.active_profile || "Student 1";
        return store;
      }
      return defaultStore();
    }
    const data = JSON.parse(raw);
    return data;
  } catch { return defaultStore(); }
}

function saveStore() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
}

let store = loadStore();
let data = store.profiles[store.active_profile];

// Ensure extra_today exists (for older saves in v2 format)
if (!data.extra_today) data.extra_today = [];

// ─── DOM refs ──────────────────────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// Header
const profileSelect  = $("#profile-select");
const btnAddProfile  = $("#btn-add-profile");
const btnDelProfile  = $("#btn-delete-profile");

// Tabs
const tabButtons     = $$(".tab-btn");
const tabPanels      = $$(".tab-panel");

// Setup
const subjectInput   = $("#subject-input");
const btnAddSubject  = $("#btn-add-subject");
const subjectList    = $("#subject-list");
const btnRemoveSubj  = $("#btn-remove-subject");
const semDay         = $("#sem-day");
const semMonth       = $("#sem-month");
const semYear        = $("#sem-year");
const timetableBuilder = $("#timetable-builder");
const btnSaveSetup   = $("#btn-save-setup");

// Attendance
const todayTitle     = $("#today-title");
const todayClasses   = $("#today-classes");
const todayActions   = $("#today-actions");
const btnLogToday    = $("#btn-log-today");
const rescheduleSubj = $("#reschedule-subject");
const btnAddResch    = $("#btn-add-reschedule");
const manualSubject  = $("#manual-subject");
const manualAttended = $("#manual-attended");
const manualTotal    = $("#manual-total");
const btnManualUpdate= $("#btn-manual-update");
const quickOverview  = $("#quick-overview");

// Dashboard
const statsRow       = $("#stats-row");
const breakdownBody  = $("#breakdown-body");
const insightsContent= $("#insights-content");

// Modal
const modalOverlay   = $("#modal-overlay");
const modalInput     = $("#modal-profile-name");
const modalCancel    = $("#modal-cancel");
const modalCreate    = $("#modal-create");

// Toast
const toastEl        = $("#toast");

// ─── Utils ─────────────────────────────────────────────────────────────
function toast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.remove("hidden");
  toastEl.classList.add("show");
  setTimeout(() => {
    toastEl.classList.remove("show");
    setTimeout(() => toastEl.classList.add("hidden"), 300);
  }, 2200);
}

function remainingWorkingDays() {
  if (!data.semester_end) return null;
  try {
    const end = new Date(data.semester_end + "T00:00:00");
    if (isNaN(end)) return null;
    const today = new Date(); today.setHours(0,0,0,0);
    if (today >= end) return 0;
    let count = 0;
    const cur = new Date(today);
    cur.setDate(cur.getDate() + 1);
    while (cur <= end) {
      if (cur.getDay() >= 1 && cur.getDay() <= 6) count++;
      cur.setDate(cur.getDate() + 1);
    }
    return count;
  } catch { return null; }
}

function remainingClassesForSubject(subj) {
  if (!data.semester_end) return null;
  try {
    const end = new Date(data.semester_end + "T00:00:00");
    if (isNaN(end)) return null;
    const today = new Date(); today.setHours(0,0,0,0);
    if (today >= end) return 0;

    const schedMap = {};
    DAYS.forEach((dayName, i) => {
      const tt = data.timetable[dayName] || [];
      const jsDay = i + 1;
      const c = tt.filter(s => s === subj).length;
      if (c > 0) schedMap[jsDay] = c;
    });

    let count = 0;
    const cur = new Date(today);
    cur.setDate(cur.getDate() + 1);
    while (cur <= end) {
      if (schedMap[cur.getDay()]) count += schedMap[cur.getDay()];
      cur.setDate(cur.getDate() + 1);
    }
    return count;
  } catch { return null; }
}

// ─── Profile Management ───────────────────────────────────────────────
function refreshProfileSelect() {
  profileSelect.innerHTML = "";
  Object.keys(store.profiles).forEach(name => {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    if (name === store.active_profile) opt.selected = true;
    profileSelect.appendChild(opt);
  });
}

profileSelect.addEventListener("change", () => {
  store.active_profile = profileSelect.value;
  data = store.profiles[store.active_profile];
  if (!data.extra_today) data.extra_today = [];
  saveStore();
  reloadAllTabs();
});

btnAddProfile.addEventListener("click", () => {
  modalInput.value = "";
  modalOverlay.classList.remove("hidden");
  modalInput.focus();
});

modalCancel.addEventListener("click", () => modalOverlay.classList.add("hidden"));

function createProfile() {
  const name = modalInput.value.trim();
  if (!name) return;
  if (store.profiles[name]) { toast("⚠️ Profile already exists!"); return; }
  store.profiles[name] = defaultProfile();
  store.active_profile = name;
  data = store.profiles[name];
  saveStore();
  refreshProfileSelect();
  reloadAllTabs();
  modalOverlay.classList.add("hidden");
  toast("✅ Profile created!");
}
modalCreate.addEventListener("click", createProfile);

btnDelProfile.addEventListener("click", () => {
  const keys = Object.keys(store.profiles);
  if (keys.length <= 1) { toast("⚠️ Need at least one profile!"); return; }
  if (!confirm(`Delete profile "${store.active_profile}"?`)) return;
  delete store.profiles[store.active_profile];
  store.active_profile = Object.keys(store.profiles)[0];
  data = store.profiles[store.active_profile];
  saveStore();
  refreshProfileSelect();
  reloadAllTabs();
});

// ─── Tab Switching ────────────────────────────────────────────────────
tabButtons.forEach(btn => {
  btn.addEventListener("click", () => {
    tabButtons.forEach(b => b.classList.remove("active"));
    tabPanels.forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    $(`#tab-${btn.dataset.tab}`).classList.add("active");
    if (btn.dataset.tab === "dashboard") refreshDashboard();
    if (btn.dataset.tab === "attendance") rebuildAttendanceTab();
  });
});

function reloadAllTabs() {
  rebuildSetupTab();
  rebuildAttendanceTab();
  refreshDashboard();
}

// ═══════════════════════════════════════════════════════════════════════
//  TAB 1: SETUP
// ═══════════════════════════════════════════════════════════════════════
let selectedSubjectIndex = -1;

function rebuildSetupTab() {
  populateSubjectList();
  loadSemesterDate();
  rebuildTimetableBuilder();
}

function populateSubjectList() {
  subjectList.innerHTML = "";
  selectedSubjectIndex = -1;
  data.subjects.forEach((s, i) => {
    const li = document.createElement("li");
    li.textContent = s;
    li.addEventListener("click", () => {
      subjectList.querySelectorAll("li").forEach(el => el.classList.remove("selected"));
      li.classList.add("selected");
      selectedSubjectIndex = i;
    });
    subjectList.appendChild(li);
  });
}

function addSubject() {
  const name = subjectInput.value.trim();
  if (!name || data.subjects.includes(name)) return;
  data.subjects.push(name);
  data.attendance[name] = { attended: 0, total: 0 };
  subjectInput.value = "";
  populateSubjectList();
  rebuildTimetableBuilder();
  saveStore();
}
btnAddSubject.addEventListener("click", addSubject);

btnRemoveSubj.addEventListener("click", () => {
  if (selectedSubjectIndex < 0) return;
  const name = data.subjects[selectedSubjectIndex];
  data.subjects.splice(selectedSubjectIndex, 1);
  delete data.attendance[name];
  DAYS.forEach(d => data.timetable[d] = data.timetable[d].filter(s => s !== name));
  populateSubjectList();
  rebuildTimetableBuilder();
  saveStore();
});

function loadSemesterDate() {
  if (data.semester_end) {
    const d = new Date(data.semester_end + "T00:00:00");
    if (!isNaN(d)) {
      semDay.value = d.getDate();
      semMonth.value = d.getMonth() + 1;
      semYear.value = d.getFullYear();
      return;
    }
  }
}

function rebuildTimetableBuilder() {
  timetableBuilder.innerHTML = "";
  if (data.subjects.length === 0) {
    timetableBuilder.innerHTML = '<p class="period-empty">Add subjects first.</p>';
    return;
  }

  DAYS.forEach(day => {
    const container = document.createElement("div");
    container.className = "day-builder";
    
    // Header with Day name and Add button
    const header = document.createElement("div");
    header.className = "day-builder-header";

    const name = document.createElement("span");
    name.className = "day-name";
    name.textContent = day;

    const select = document.createElement("select");
    data.subjects.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s;
      select.appendChild(opt);
    });

    const addBtn = document.createElement("button");
    addBtn.className = "btn btn-accent btn-sm";
    addBtn.textContent = "+ Period";
    addBtn.onclick = () => {
      data.timetable[day].push(select.value);
      renderPeriods(day, periodList);
    };

    header.appendChild(name);
    header.appendChild(select);
    header.appendChild(addBtn);

    // Period List
    const periodList = document.createElement("div");
    periodList.className = "period-list";
    renderPeriods(day, periodList);

    // Copy Day Logic
    const copyRow = document.createElement("div");
    copyRow.className = "copy-day-row";
    const copyLbl = document.createElement("label");
    copyLbl.textContent = "Copy to:";
    copyRow.appendChild(copyLbl);

    DAYS.filter(d => d !== day).forEach(targetDay => {
      const btn = document.createElement("button");
      btn.className = "btn btn-muted btn-sm";
      btn.textContent = targetDay.substring(0, 3);
      btn.onclick = () => {
        if(confirm(`Copy ${day} schedule to ${targetDay}?`)) {
          data.timetable[targetDay] = [...data.timetable[day]];
          rebuildTimetableBuilder();
        }
      };
      copyRow.appendChild(btn);
    });

    container.appendChild(header);
    container.appendChild(periodList);
    container.appendChild(copyRow);
    timetableBuilder.appendChild(container);
  });
}

function renderPeriods(day, element) {
  element.innerHTML = "";
  if (data.timetable[day].length === 0) {
    element.innerHTML = '<span class="period-empty">No periods scheduled.</span>';
    return;
  }
  data.timetable[day].forEach((subj, idx) => {
    const chip = document.createElement("div");
    chip.className = "period-chip";
    chip.innerHTML = `
      <span class="period-num">${idx + 1}</span>
      <span>${subj}</span>
      <button class="remove-period" title="Remove period">×</button>
    `;
    chip.querySelector(".remove-period").onclick = () => {
      data.timetable[day].splice(idx, 1);
      renderPeriods(day, element);
    };
    element.appendChild(chip);
  });
}

btnSaveSetup.addEventListener("click", () => {
  const d = parseInt(semDay.value), m = parseInt(semMonth.value), y = parseInt(semYear.value);
  if (isNaN(d) || isNaN(m) || isNaN(y)) { toast("❌ Invalid date!"); return; }
  data.semester_end = `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
  saveStore();
  toast("💾 Setup saved! ✓");
  rebuildAttendanceTab();
});

// ═══════════════════════════════════════════════════════════════════════
//  TAB 2: ATTENDANCE
// ═══════════════════════════════════════════════════════════════════════
function rebuildAttendanceTab() {
  rebuildTodayClasses();
  rebuildRescheduleSelect();
  rebuildManualEntry();
  rebuildQuickOverview();
}

let todayClassStates = []; // Array of {subj, type, isExtra} - type: 1=present, 0=absent, -1=cancelled

function rebuildTodayClasses() {
  const now = new Date();
  const jsDay = now.getDay();
  let todayName = jsDay >= 1 && jsDay <= 6 ? DAYS[jsDay - 1] : null;

  todayTitle.textContent = `📆 Today's Classes — ${todayName || "Sunday"}`;
  todayClasses.innerHTML = "";
  todayActions.style.display = "none";

  if (!todayName && data.extra_today.length === 0) {
    todayClasses.innerHTML = '<p class="subtitle">No classes today.</p>';
    return;
  }

  const baseTT = todayName ? data.timetable[todayName] : [];
  todayClassStates = [];

  baseTT.forEach(subj => todayClassStates.push({ subj, type: 1, isExtra: false }));
  data.extra_today.forEach(subj => todayClassStates.push({ subj, type: 1, isExtra: true }));

  if (todayClassStates.length === 0) {
    todayClasses.innerHTML = '<p class="subtitle">No classes today.</p>';
    return;
  }

  todayClassStates.forEach((state, idx) => {
    const row = document.createElement("div");
    row.className = "today-class-row" + (state.isExtra ? " extra" : "");
    
    const label = document.createElement("div");
    label.className = "today-class-label";
    label.innerHTML = `Period ${idx+1}: ${state.subj}${state.isExtra ? ' <span class="extra-badge">Extra</span>' : ''}`;
    
    const btns = document.createElement("div");
    btns.className = "today-btns";

    const createBtn = (text, type, colorClass) => {
      const b = document.createElement("button");
      b.className = `btn btn-sm btn-${colorClass}` + (state.type === type ? " selected" : "");
      b.textContent = text;
      b.onclick = () => {
        state.type = type;
        btns.querySelectorAll("button").forEach(el => el.classList.remove("selected"));
        b.classList.add("selected");
      };
      return b;
    };

    btns.appendChild(createBtn("✓ Present", 1, "green"));
    btns.appendChild(createBtn("✗ Absent", 0, "red"));
    btns.appendChild(createBtn("🚫 Cancelled", -1, "cancel"));

    row.appendChild(label);
    row.appendChild(btns);
    todayClasses.appendChild(row);
  });

  todayActions.style.display = "flex";
}

btnLogToday.addEventListener("click", () => {
  todayClassStates.forEach(state => {
    if (state.type === -1) return; // Cancelled
    if (!data.attendance[state.subj]) data.attendance[state.subj] = { attended: 0, total: 0 };
    data.attendance[state.subj].total += 1;
    if (state.type === 1) data.attendance[state.subj].attended += 1;
  });
  data.extra_today = []; // Clear extra classes after logging
  saveStore();
  toast("📝 Attendance logged! ✓");
  rebuildAttendanceTab();
});

function rebuildRescheduleSelect() {
  rescheduleSubj.innerHTML = "";
  data.subjects.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s;
    rescheduleSubj.appendChild(opt);
  });
}

btnAddResch.addEventListener("click", () => {
  if (!rescheduleSubj.value) return;
  data.extra_today.push(rescheduleSubj.value);
  saveStore();
  rebuildTodayClasses();
  toast("➕ Extra class added!");
});

function rebuildManualEntry() {
  manualSubject.innerHTML = "";
  data.subjects.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s; opt.textContent = s;
    manualSubject.appendChild(opt);
  });
  loadManualValues();
}

function loadManualValues() {
  const subj = manualSubject.value;
  if (subj && data.attendance[subj]) {
    manualAttended.value = data.attendance[subj].attended;
    manualTotal.value = data.attendance[subj].total;
  }
}
manualSubject.addEventListener("change", loadManualValues);

btnManualUpdate.addEventListener("click", () => {
  const subj = manualSubject.value;
  const attended = parseInt(manualAttended.value), total = parseInt(manualTotal.value);
  if (isNaN(attended) || isNaN(total) || attended > total) { toast("❌ Invalid numbers!"); return; }
  data.attendance[subj] = { attended, total };
  saveStore();
  toast("💾 Updated! ✓");
  rebuildQuickOverview();
});

function rebuildQuickOverview() {
  quickOverview.innerHTML = "";
  data.subjects.forEach(subj => {
    const att = data.attendance[subj] || { attended: 0, total: 0 };
    const pct = att.total > 0 ? (att.attended / att.total * 100) : 0;
    const colorClass = pct >= 75 ? "safe" : (pct >= 73 ? "warn" : "danger");

    const row = document.createElement("div");
    row.className = "quick-row";
    row.innerHTML = `
      <span class="quick-subj">${subj}</span>
      <span class="quick-ratio">${att.attended}/${att.total}</span>
      <span class="quick-pct ${colorClass}">${pct.toFixed(1)}%</span>
      <div class="quick-buttons">
        <button class="btn btn-green btn-sm" onclick="quickAdj('${subj}', 1)">✓</button>
        <button class="btn btn-red btn-sm" onclick="quickAdj('${subj}', 0)">✗</button>
      </div>
    `;
    quickOverview.appendChild(row);
  });
}

window.quickAdj = (subj, type) => {
  if (!data.attendance[subj]) data.attendance[subj] = { attended: 0, total: 0 };
  data.attendance[subj].total += 1;
  if (type === 1) data.attendance[subj].attended += 1;
  saveStore();
  rebuildAttendanceTab();
};

// ═══════════════════════════════════════════════════════════════════════
//  TAB 3: DASHBOARD
// ═══════════════════════════════════════════════════════════════════════
function refreshDashboard() {
  let totalAtt = 0, totalCls = 0;
  Object.values(data.attendance).forEach(a => {
    totalAtt += a.attended; totalCls += a.total;
  });
  const overallPct = totalCls > 0 ? (totalAtt / totalCls * 100) : 0;
  const remDays = remainingWorkingDays();

  statsRow.innerHTML = "";
  const stats = [
    { value: `${overallPct.toFixed(1)}%`, label: "Overall %", sub: "All combined" },
    { value: `${totalAtt}/${totalCls}`, label: "Attended", sub: "Total classes" },
    { value: remDays !== null ? remDays : "—", label: "Days Left", sub: "Working days" },
    { value: data.subjects.length, label: "Subjects", sub: "Enrolled" },
  ];
  stats.forEach(s => {
    const card = document.createElement("div");
    card.className = "stat-card";
    card.innerHTML = `<div class="stat-value">${s.value}</div><div class="stat-label">${s.label}</div><div class="stat-sub">${s.sub}</div>`;
    statsRow.appendChild(card);
  });

  breakdownBody.innerHTML = "";
  data.subjects.forEach(subj => {
    const att = data.attendance[subj] || { attended: 0, total: 0 };
    const attended = att.attended, total = att.total;
    const pct = total > 0 ? (attended / total * 100) : 0;
    const canSkip = pct >= 75 && total > 0 ? Math.floor(attended / 0.75) - total : 0;
    let must = pct < 75 && total > 0 ? Math.ceil((0.75 * total - attended) / 0.25) : 0;
    if (must < 0) must = 0;
    const remClasses = remainingClassesForSubject(subj);
    const rowClass = pct >= 75 ? "row-safe" : (pct >= 73 ? "row-warn" : "row-danger");

    const tr = document.createElement("tr");
    tr.className = rowClass;
    tr.innerHTML = `<td>${subj}</td><td>${attended}</td><td>${total}</td><td>${pct.toFixed(1)}%</td><td>${canSkip > 0 ? canSkip : "—"}</td><td>${must > 0 ? must : "✓"}</td><td>${remClasses !== null ? remClasses : "—"}</td>`;
    breakdownBody.appendChild(tr);
  });

  insightsContent.innerHTML = "";
  const safe = [], danger = [];
  data.subjects.forEach(subj => {
    const att = data.attendance[subj] || { attended: 0, total: 0 };
    if (att.total === 0) return;
    const pct = att.attended / att.total * 100;
    if (pct >= 75) {
      safe.push({ subj, pct, skip: Math.floor(att.attended / 0.75) - att.total });
    } else {
      let must = Math.ceil((0.75 * att.total - att.attended) / 0.25);
      danger.push({ subj, pct, must: Math.max(0, must) });
    }
  });

  if (danger.length) {
    const h = document.createElement("div"); h.className = "insight-heading danger"; h.textContent = "⚠️ Below 75%:";
    insightsContent.appendChild(h);
    danger.forEach(d => {
      const p = document.createElement("div"); p.className = "insight-item danger";
      p.textContent = `• ${d.subj}: ${d.pct.toFixed(1)}% — attend ${d.must} more`;
      insightsContent.appendChild(p);
    });
  }
  if (safe.length) {
    const h = document.createElement("div"); h.className = "insight-heading safe"; h.textContent = "✅ Safe Subjects:";
    insightsContent.appendChild(h);
    safe.forEach(s => {
      const p = document.createElement("div"); p.className = "insight-item safe";
      p.textContent = `• ${s.subj}: ${s.pct.toFixed(1)}% — can skip ${s.skip}`;
      insightsContent.appendChild(p);
    });
  }
}

// ─── Init ──────────────────────────────────────────────────────────────
refreshProfileSelect();
reloadAllTabs();
