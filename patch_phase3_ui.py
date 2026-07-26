#!/usr/bin/env python3
"""Fix duplicate code in pms-adapter.js and add Phase 3 UI to radiographs.html."""

from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# 1. FIX pms-adapter.js — remove duplicate buildTreatmentPlanReport body
# ═══════════════════════════════════════════════════════════════

js_file = Path("C:/Users/mreno/Documents/kimi/workspace/new-ridge-family-dental/js/pms-adapter.js")
lines = js_file.read_text(encoding='utf-8').splitlines(keepends=True)

# Find and remove lines 683-696 (the duplicate, 0-indexed: 682-695)
# The duplicate starts with "  if (!overlays || overlays.length === 0) return [];"
# and ends with "  }));\n}"
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Detect start of duplicate block
    if line.strip() == "if (!overlays || overlays.length === 0) return [];" and i > 600:
        # Skip until we find the closing brace of the duplicate
        j = i
        while j < len(lines) and not (lines[j].strip() == "}" and lines[j-1].strip().startswith("note:")):
            j += 1
        if j < len(lines):
            j += 1  # skip the closing brace line too
        i = j
        continue
    new_lines.append(line)
    i += 1

js_file.write_text(''.join(new_lines), encoding='utf-8')
print("[✓] Fixed duplicate code in pms-adapter.js")

# ═══════════════════════════════════════════════════════════════
# 2. ADD Phase 3 UI widgets to radiographs.html
# ═══════════════════════════════════════════════════════════════

html_file = Path("C:/Users/mreno/Documents/kimi/workspace/new-ridge-family-dental/radiographs.html")
content = html_file.read_text(encoding='utf-8')

# Find the treatment plan section and add insurance + appointment widgets after it
old_treat_plan = '''      <!-- ═══════════════════════════════════════════════════════════
           PHASE 2 — TREATMENT PLAN
           ═══════════════════════════════════════════════════════════ -->
      <div class="rx-sect" id="rxTreatPlanSect" style="display:none;">
        <div class="rx-sect-head"><span class="dot purple"></span>Treatment Plan</div>
        <div id="rxTreatPlan"></div>
      </div>'''

new_treat_plan = '''      <!-- ═══════════════════════════════════════════════════════════
           PHASE 2 — TREATMENT PLAN
           ═══════════════════════════════════════════════════════════ -->
      <div class="rx-sect" id="rxTreatPlanSect" style="display:none;">
        <div class="rx-sect-head"><span class="dot purple"></span>Treatment Plan</div>
        <div id="rxTreatPlan"></div>
      </div>

      <!-- ═══════════════════════════════════════════════════════════
           PHASE 3 — INSURANCE PRE-AUTH CALCULATOR
           ═══════════════════════════════════════════════════════════ -->
      <div class="rx-sect" id="rxInsuranceSect" style="display:none;">
        <div class="rx-sect-head"><span class="dot" style="background:var(--rx-success);box-shadow:0 0 6px var(--rx-success);"></span>Insurance Calculator</div>
        <div id="rxInsurance">
          <div class="rx-ins-card">
            <div class="rx-ins-header">
              <div class="rx-ins-carrier" id="insCarrier">—</div>
              <div class="rx-ins-plan" id="insPlan">—</div>
            </div>
            <div class="rx-ins-meters">
              <div class="rx-ins-meter">
                <div class="rx-ins-meter-label">Deductible</div>
                <div class="rx-ins-meter-bar"><div class="rx-ins-meter-fill" id="insDeductMeter"></div></div>
                <div class="rx-ins-meter-val"><span id="insDeductMet">—</span> / <span id="insDeductTotal">—</span></div>
              </div>
              <div class="rx-ins-meter">
                <div class="rx-ins-meter-label">Annual Maximum</div>
                <div class="rx-ins-meter-bar"><div class="rx-ins-meter-fill" id="insMaxMeter"></div></div>
                <div class="rx-ins-meter-val"><span id="insMaxUsed">—</span> / <span id="insMaxTotal">—</span></div>
              </div>
            </div>
            <div class="rx-ins-estimate" id="insEstimate" style="display:none;">
              <div class="rx-ins-est-head">Estimate for <span id="insEstProc">—</span></div>
              <div class="rx-ins-est-row"><span>Fee</span><span id="insEstFee">—</span></div>
              <div class="rx-ins-est-row"><span>Insurance covers (<span id="insEstPct">—</span>%)</span><span id="insEstCovered">—</span></div>
              <div class="rx-ins-est-row"><span>Patient responsibility</span><span id="insEstPatient" style="color:var(--rx-danger);font-weight:600;">—</span></div>
            </div>
            <div class="rx-ins-procs">
              <select id="insProcSelect" onchange="calculateInsurance()">
                <option value="">Select procedure for estimate…</option>
                <option value="D0330">CBCT (D0330) — $350</option>
                <option value="D2740">Zirconia Crown (D2740) — $1,200</option>
                <option value="D6010">Implant Placement (D6010) — $2,200</option>
                <option value="D7140">Extraction (D7140) — $185</option>
                <option value="D4341">SRP — Quad (D4341) — $280</option>
                <option value="D4910">Perio Maintenance (D4910) — $140</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════════════════
           PHASE 3 — APPOINTMENT BOOKING
           ═══════════════════════════════════════════════════════════ -->
      <div class="rx-sect" id="rxApptSect" style="display:none;">
        <div class="rx-sect-head"><span class="dot" style="background:var(--rx-accent);box-shadow:0 0 6px var(--rx-accent);"></span>Book Appointment</div>
        <div id="rxAppt">
          <div class="rx-appt-grid" id="rxApptGrid"></div>
          <div class="rx-appt-confirm" id="rxApptConfirm" style="display:none;">
            <div class="rx-appt-sel">
              <strong>Selected:</strong> <span id="apptSelDate">—</span> at <span id="apptSelTime">—</span>
            </div>
            <button class="rx-tool-btn primary" style="width:100%;margin-top:10px;" onclick="confirmAppointment()">Confirm Booking</button>
          </div>
        </div>
      </div>'''

if old_treat_plan in content:
    content = content.replace(old_treat_plan, new_treat_plan)
    print("[✓] Added Insurance + Appointment widgets to radiographs.html")
else:
    print("[✗] Treatment plan section not found — widgets not added")

# ═══════════════════════════════════════════════════════════════
# 3. ADD Phase 3 CSS styles
# ═══════════════════════════════════════════════════════════════

phase3_css = '''
  /* ═══════════════════════════════════════════════════════════════
     PHASE 3 — INSURANCE CALCULATOR
     ═══════════════════════════════════════════════════════════════ */
  .rx-ins-card{
    background:var(--rx-elev); border:1px solid var(--rx-border);
    border-radius:var(--radius); padding:14px;
  }
  .rx-ins-header{ margin-bottom:14px; }
  .rx-ins-carrier{ font-size:13px; font-weight:600; color:var(--rx-text); }
  .rx-ins-plan{ font-family:var(--mono); font-size:10px; color:var(--rx-text-dim); margin-top:2px; }
  .rx-ins-meters{ display:flex; flex-direction:column; gap:10px; margin-bottom:14px; }
  .rx-ins-meter{ display:grid; grid-template-columns:100px 1fr auto; gap:8px; align-items:center; }
  .rx-ins-meter-label{ font-family:var(--mono); font-size:9px; color:var(--rx-text-dim); text-transform:uppercase; letter-spacing:.06em; }
  .rx-ins-meter-bar{ height:6px; background:var(--rx-panel); border-radius:3px; overflow:hidden; }
  .rx-ins-meter-fill{ height:100%; border-radius:3px; background:var(--rx-accent); transition:width .5s ease; }
  .rx-ins-meter-fill.warn{ background:var(--rx-warn); }
  .rx-ins-meter-fill.danger{ background:var(--rx-danger); }
  .rx-ins-meter-val{ font-family:var(--mono); font-size:10px; color:var(--rx-text); }
  .rx-ins-estimate{
    background:var(--rx-panel); border:1px solid var(--rx-border-light);
    border-radius:var(--radius-sm); padding:12px; margin-bottom:12px;
    animation:fadeInUp .3s ease;
  }
  .rx-ins-est-head{ font-size:12px; color:var(--rx-text-dim); margin-bottom:8px; }
  .rx-ins-est-head span{ color:var(--rx-accent); font-weight:500; }
  .rx-ins-est-row{ display:flex; justify-content:space-between; font-size:12px; padding:5px 0; border-bottom:1px solid var(--rx-border); }
  .rx-ins-est-row:last-child{ border-bottom:none; }
  .rx-ins-est-row span:first-child{ color:var(--rx-text-dim); }
  .rx-ins-est-row span:last-child{ color:var(--rx-text); font-family:var(--mono); }
  .rx-ins-procs select{
    width:100%; background:var(--rx-panel); border:1px solid var(--rx-border);
    border-radius:var(--radius-sm); color:var(--rx-text); font-family:var(--sans); font-size:12px;
    padding:8px 12px; outline:none; cursor:pointer;
  }
  .rx-ins-procs select:focus{ border-color:var(--rx-accent); }

  /* ═══════════════════════════════════════════════════════════════
     PHASE 3 — APPOINTMENT BOOKING
     ═══════════════════════════════════════════════════════════════ */
  .rx-appt-grid{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }
  .rx-appt-day{
    background:var(--rx-elev); border:1px solid var(--rx-border);
    border-radius:var(--radius-sm); padding:10px;
    transition:all .2s ease;
  }
  .rx-appt-day:hover{ border-color:var(--rx-border-light); }
  .rx-appt-day-label{ font-family:var(--mono); font-size:9px; color:var(--rx-text-dim); text-transform:uppercase; letter-spacing:.08em; margin-bottom:6px; }
  .rx-appt-day-label strong{ color:var(--rx-text); font-size:11px; display:block; }
  .rx-appt-slot{
    font-family:var(--mono); font-size:10px; padding:5px 8px; margin:3px 0;
    border-radius:4px; border:1px solid var(--rx-border);
    color:var(--rx-text-dim); cursor:pointer; text-align:center;
    transition:all .15s ease;
  }
  .rx-appt-slot:hover{ border-color:var(--rx-accent); color:var(--rx-accent); background:var(--rx-accent-glow); }
  .rx-appt-slot.selected{ background:var(--rx-accent); color:var(--rx-bg); border-color:var(--rx-accent); font-weight:600; }
  .rx-appt-confirm{ margin-top:10px; }
  .rx-appt-sel{ font-size:12px; color:var(--rx-text); padding:8px; background:var(--rx-elev); border-radius:var(--radius-sm); }
  .rx-appt-sel span{ color:var(--rx-accent); font-weight:500; }
'''

# Insert Phase 3 CSS before the responsive media query
if '/* responsive */' in content:
    content = content.replace('/* responsive */', phase3_css + '\n  /* responsive */')
    print("[✓] Added Phase 3 CSS styles")
else:
    print("[✗] Could not find insertion point for Phase 3 CSS")

# ═══════════════════════════════════════════════════════════════
# 4. ADD Phase 3 JavaScript functions
# ═══════════════════════════════════════════════════════════════

phase3_js = '''
  /* ═══════════════════════════════════════════════════════════════
     PHASE 3 — INSURANCE CALCULATOR
     ═══════════════════════════════════════════════════════════════ */
  async function loadAndRenderInsurance(patientId) {
    try {
      const insurance = await loadInsurance(patientId);
      document.getElementById('insCarrier').textContent = insurance.carrier;
      document.getElementById('insPlan').textContent = `${insurance.plan} · Member: ${insurance.memberId}`;
      document.getElementById('insDeductMet').textContent = `$${insurance.deductibleMet}`;
      document.getElementById('insDeductTotal').textContent = `$${insurance.deductibleAnnual}`;
      document.getElementById('insMaxUsed').textContent = `$${insurance.annualUsed}`;
      document.getElementById('insMaxTotal').textContent = `$${insurance.annualMax}`;

      const deductPct = (insurance.deductibleMet / insurance.deductibleAnnual) * 100;
      const maxPct = (insurance.annualUsed / insurance.annualMax) * 100;
      document.getElementById('insDeductMeter').style.width = `${deductPct}%`;
      document.getElementById('insMaxMeter').style.width = `${maxPct}%`;
      if (maxPct > 80) document.getElementById('insMaxMeter').classList.add('warn');
      if (maxPct > 95) document.getElementById('insMaxMeter').classList.add('danger');

      document.getElementById('rxInsuranceSect').style.display = 'block';
    } catch (e) { console.error('[Insurance]', e); }
  }

  window.calculateInsurance = function() {
    const select = document.getElementById('insProcSelect');
    const code = select.value;
    if (!code) { document.getElementById('insEstimate').style.display = 'none'; return; }
    const estimate = calculateInsuranceEstimate(code, MOCK_INSURANCE);
    if (!estimate) return;
    document.getElementById('insEstProc').textContent = estimate.name;
    document.getElementById('insEstFee').textContent = `$${estimate.fee.toLocaleString()}`;
    document.getElementById('insEstPct').textContent = estimate.percent;
    document.getElementById('insEstCovered').textContent = `$${Math.round(estimate.covered).toLocaleString()}`;
    document.getElementById('insEstPatient').textContent = `$${Math.round(estimate.patientDue).toLocaleString()}`;
    document.getElementById('insEstimate').style.display = 'block';
  };

  /* ═══════════════════════════════════════════════════════════════
     PHASE 3 — APPOINTMENT BOOKING
     ═══════════════════════════════════════════════════════════════ */
  let selectedAppt = null;

  async function loadAndRenderAppointments() {
    try {
      const slots = await loadAppointmentSlots();
      const grid = document.getElementById('rxApptGrid');
      grid.innerHTML = slots.map(d => `
        <div class="rx-appt-day">
          <div class="rx-appt-day-label"><strong>${d.day}</strong>${d.date}</div>
          ${d.slots.map(s => `<div class="rx-appt-slot" data-date="${d.date}" data-time="${s}" onclick="selectAppt(this)">${s}</div>`).join('')}
        </div>
      `).join('');
      document.getElementById('rxApptSect').style.display = 'block';
    } catch (e) { console.error('[Appt]', e); }
  }

  window.selectAppt = function(el) {
    document.querySelectorAll('.rx-appt-slot').forEach(s => s.classList.remove('selected'));
    el.classList.add('selected');
    selectedAppt = { date: el.dataset.date, time: el.dataset.time };
    document.getElementById('apptSelDate').textContent = selectedAppt.date;
    document.getElementById('apptSelTime').textContent = selectedAppt.time;
    document.getElementById('rxApptConfirm').style.display = 'block';
  };

  window.confirmAppointment = function() {
    if (!selectedAppt) return;
    alert(`Appointment requested:\n${selectedAppt.date} at ${selectedAppt.time}\n\nThe front desk will confirm by phone.`);
    document.getElementById('rxApptConfirm').style.display = 'none';
    document.querySelectorAll('.rx-appt-slot').forEach(s => s.classList.remove('selected'));
    selectedAppt = null;
  };
'''

# Insert Phase 3 JS before the global functions section
if 'window.loadPatientFromInput = async function()' in content:
    content = content.replace(
        '  window.loadPatientFromInput = async function() {',
        phase3_js + '\n  window.loadPatientFromInput = async function() {'
    )
    print("[✓] Added Phase 3 JavaScript functions")
else:
    print("[✗] Could not find insertion point for Phase 3 JS")

# ═══════════════════════════════════════════════════════════════
# 5. Wire up loadAndRender to call insurance + appointments
# ═══════════════════════════════════════════════════════════════

old_load = '''        // Phase 2: load threads & overlays
        currentThreads = await loadAnnotationThreads(currentRadiograph?.id);
        renderThreads(currentThreads);
        currentOverlays = await loadTreatmentOverlays(currentRadiograph?.id);
        renderTreatmentOverlays(currentOverlays);
        renderTreatmentList(currentOverlays);'''

new_load = '''        // Phase 2: load threads & overlays
        currentThreads = await loadAnnotationThreads(currentRadiograph?.id);
        renderThreads(currentThreads);
        currentOverlays = await loadTreatmentOverlays(currentRadiograph?.id);
        renderTreatmentOverlays(currentOverlays);
        renderTreatmentList(currentOverlays);

        // Phase 3: load insurance & appointments
        await loadAndRenderInsurance(currentPatient.id);
        await loadAndRenderAppointments();'''

if old_load in content:
    content = content.replace(old_load, new_load)
    print("[✓] Wired up insurance + appointment loaders")
else:
    print("[✗] Could not find loadAndRender section to wire up")

# Write back
html_file.write_text(content, encoding='utf-8')
print("\n[✓] radiographs.html fully updated for Phase 3")
