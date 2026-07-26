/**
 * PMS Adapter — New Ridge Family Dental Radiograph Viewer
 * Unifies data access across mock, JSON file, Open Dental, Dentrix, and generic APIs.
 */

import { PMS_CONFIG } from './pms-config.js';

/* ================================================================
   CACHE
   ================================================================ */
const cache = new Map();

function cacheKey(mode, resource, id) { return `${mode}::${resource}::${id}`; }

function getCached(key) {
  if (!PMS_CONFIG.cache.enabled) return null;
  const entry = cache.get(key);
  if (!entry) return null;
  if (Date.now() - entry.ts > PMS_CONFIG.cache.ttlMinutes * 60 * 1000) {
    cache.delete(key);
    return null;
  }
  return entry.data;
}

function setCached(key, data) {
  if (!PMS_CONFIG.cache.enabled) return;
  cache.set(key, { data, ts: Date.now() });
}

/* ================================================================
   MOCK DATA
   ================================================================ */
const MOCK_PATIENT = {
  id: '78429',
  firstName: 'John',
  lastName: 'Doe',
  dob: '1985-04-12',
  displayDob: '04/12/1985',
  initials: 'JD',
  phone: '(316) 555-0142',
  email: 'john.doe@email.com'
};

const MOCK_RADIOGRAPHS = [
  {
    id: 'RAD-2026-0725-001',
    patientId: '78429',
    type: 'Panoramic',
    date: '2026-07-25',
    displayDate: '07/25/2026',
    imageUrl: '', // SVG rendered inline
    priorIds: ['RAD-2025-0114-001', 'RAD-2022-0603-001'],
    priors: [
      { id: 'RAD-2025-0114-001', date: '01/14/2025', label: 'Prior — 01/14/2025' },
      { id: 'RAD-2022-0603-001', date: '06/03/2022', label: 'Baseline — 06/03/2022' }
    ]
  }
];

const MOCK_ANALYSIS = {
  radiographId: 'RAD-2026-0725-001',
  overview: 'Full-arch panoramic radiograph demonstrates bilateral endosseous implants in the mandibular first-molar positions (#19 and #30) with intact crestal bone levels and no signs of peri-implant radiolucency.',
  findings: [
    {
      rank: 1,
      severity: 'danger',
      tooth: '#25',
      text: 'Periapical radiolucency #25 — possible failed RCT or persistent infection.',
      note: 'Recommend CBCT + endodontic re-evaluation',
      confidence: 0.94
    },
    {
      rank: 2,
      severity: 'warn',
      tooth: '#24',
      text: 'Recurrent caries at mesial margin of #24 crown.',
      note: 'Monitor or replace restoration',
      confidence: 0.89
    },
    {
      rank: 3,
      severity: 'warn',
      tooth: '#14–16',
      text: 'Posterior maxillary bone loss 3–4 mm (#14–16, #2–4).',
      note: 'Continue perio maintenance q3mo',
      confidence: 0.91
    },
    {
      rank: 4,
      severity: 'info',
      tooth: '#19, #30',
      text: 'Implants #19 & #30 — stable, well-osseointegrated.',
      note: 'Annual recall adequate',
      confidence: 0.97
    },
    {
      rank: 5,
      severity: 'info',
      tooth: 'Maxillary sinuses',
      text: 'No signs of maxillary sinus pathology.',
      note: 'Within normal limits',
      confidence: 0.95
    }
  ],
  paragraphs: [
    {
      heading: 'Panoramic overview',
      text: 'Full-arch panoramic radiograph demonstrates bilateral endosseous implants in the mandibular first-molar positions (#19 and #30) with intact crestal bone levels and no signs of peri-implant radiolucency.',
      confidence: null
    },
    {
      heading: 'Periodontal status',
      text: 'Generalized horizontal bone loss of approximately 3–4 mm is present in the posterior maxilla. Anterior regions show preserved interdental septa.',
      confidence: 0.91
    },
    {
      heading: 'Endodontic finding',
      text: 'Tooth #25 exhibits a well-defined periapical radiolucency measuring ~6 × 8 mm. Prior root canal therapy is present on #24 with evidence of recurrent decay at the mesial margin.',
      confidence: 0.87
    }
  ],
  measurements: [
    { label: 'Implant #19 crestal bone', value: '1.2 mm' },
    { label: 'Implant #30 crestal bone', value: '1.4 mm' },
    { label: '#25 periapical lesion', value: '6.1 × 8.3 mm' },
    { label: 'Mandibular canal clearance', value: '4.8 mm' }
  ],
  annotations: [
    { id: 'ann-1', x: 28, y: 30, label: 'Implant #19 — Osseointegrated', severity: 'info', confidence: 0.97 },
    { id: 'ann-2', x: 62, y: 30, label: 'Implant #30 — Osseointegrated', severity: 'info', confidence: 0.96 },
    { id: 'ann-3', x: 44, y: 68, label: 'Root canal #24 — Recurrent decay', severity: 'warn', confidence: 0.89 },
    { id: 'ann-4', x: 52, y: 65, label: '#25 — Periapical radiolucency', severity: 'danger', confidence: 0.94 },
    { id: 'ann-5', x: 36, y: 36, label: '#14 — Bone loss 3-4 mm', severity: 'warn', confidence: 0.91 }
  ],
  report: {
    clinicalImpressions: [
      'Panoramic radiograph dated July 25, 2026, reviewed with AI-assisted analysis. Bilateral endosseous implants are present in the mandibular first-molar positions (#19 and #30). Both implants demonstrate stable crestal bone levels without evidence of peri-implant radiolucency, consistent with successful osseointegration.',
      'Tooth #25 demonstrates a well-circumscribed periapical radiolucency measuring approximately 6 × 8 mm. Given the size and well-defined nature of this lesion, endodontic re-evaluation with cone-beam CT is recommended to assess for persistent infection, cystic change, or vertical root fracture.',
      'Tooth #24 has undergone prior root canal therapy. A radiolucent defect is noted at the mesial margin of the existing crown, suggestive of recurrent caries. Clinical correlation and possible restoration replacement should be considered.',
      'Generalized horizontal bone loss of 3–4 mm is noted in the posterior maxillary sextants. This is consistent with mild chronic periodontitis. Current periodontal maintenance every three months is appropriate and should be continued.'
    ],
    recommendations: [
      'Schedule CBCT imaging of tooth #25 to characterize periapical lesion and rule out vertical root fracture.',
      'Endodontic re-evaluation of #25; consider nonsurgical retreatment or apical surgery depending on CBCT findings.',
      'Evaluate #24 crown margin clinically; replace restoration if recurrent caries is confirmed.',
      'Continue periodontal maintenance every three months with routine radiographic surveillance.',
      'Annual panoramic recall for implant #19 and #30 monitoring.'
    ]
  }
};

/* ═══════════════════════════════════════════════════════════════════
   PHASE 2 — COLLABORATION & TREATMENT PLAN MOCK DATA
   ═══════════════════════════════════════════════════════════════════ */

const MOCK_ANNOTATION_THREADS = [
  {
    id: 'thread-1',
    annotationId: 'ann-1',
    tooth: '#19',
    author: { initials: 'MR', name: 'Dr. Reno', role: 'dentist' },
    timestamp: '2026-07-25T14:30:00Z',
    text: 'Implant #19 looks stable. No peri-implantitis signs on this panoramic. Crestal bone level is excellent at 1.2 mm.',
    resolved: false,
    replies: [
      {
        id: 'reply-1',
        author: { initials: 'HS', name: 'Hygienist Smith', role: 'hygienist' },
        timestamp: '2026-07-25T14:35:00Z',
        text: '@Dr. Reno Agreed. Patient reports no discomfort and good oral hygiene. Probing depths were 2-3mm at recall.',
        mentions: ['Dr. Reno']
      }
    ]
  },
  {
    id: 'thread-2',
    annotationId: 'ann-4',
    tooth: '#25',
    author: { initials: 'MR', name: 'Dr. Reno', role: 'dentist' },
    timestamp: '2026-07-25T14:32:00Z',
    text: '#25 periapical radiolucency is concerning. Previous RCT was done 3 years ago. Need CBCT to assess for VRF before making a treatment decision.',
    resolved: false,
    replies: [
      {
        id: 'reply-2',
        author: { initials: 'JE', name: 'Dr. Evans', role: 'endodontist' },
        timestamp: '2026-07-25T15:10:00Z',
        text: '@Dr. Reno I can fit them in tomorrow at 2pm for CBCT and consult. Based on the size, I am leaning toward extraction + implant rather than retreatment.',
        mentions: ['Dr. Reno']
      }
    ]
  },
  {
    id: 'thread-3',
    annotationId: 'ann-3',
    tooth: '#24',
    author: { initials: 'MR', name: 'Dr. Reno', role: 'dentist' },
    timestamp: '2026-07-25T14:40:00Z',
    text: 'Crown margin decay on #24. The existing PFM is 7 years old. I would recommend a zirconia replacement this time for better tissue response.',
    resolved: true,
    replies: []
  }
];

const MOCK_TREATMENT_OVERLAYS = [
  {
    id: 'treat-1',
    type: 'crown',
    tooth: '#24',
    x: 44, y: 68,
    material: 'zirconia',
    status: 'proposed',
    note: 'Replace existing PFM crown with recurrent mesial caries'
  },
  {
    id: 'treat-2',
    type: 'extraction',
    tooth: '#25',
    x: 52, y: 65,
    status: 'proposed',
    note: 'Extraction due to failed RCT + periapical pathology'
  },
  {
    id: 'treat-3',
    type: 'implant',
    tooth: '#25',
    x: 52, y: 65,
    status: 'proposed',
    note: 'Implant placement 3 months post-extraction'
  },
  {
    id: 'treat-4',
    type: 'srp',
    tooth: '#14–16',
    x: 36, y: 36,
    status: 'scheduled',
    note: 'Scaling & root planing — q3mo maintenance'
  }
];

const MOCK_PACS_STATUS = {
  connected: true,
  lastSync: '2026-07-25T14:20:00Z',
  queueSize: 0,
  latency: 45,
  modality: 'Panoramic',
  server: 'PACS-MAIN-01',
  studiesToday: 12,
  autoSync: true
};

/* ================================================================
   MODE: MOCK
   ================================================================ */
async function mockGetPatient(id) {
  await delay(200);
  return id === MOCK_PATIENT.id ? MOCK_PATIENT : null;
}

async function mockGetRadiographs(patientId) {
  await delay(150);
  return MOCK_RADIOGRAPHS.filter(r => r.patientId === patientId);
}

async function mockGetAnalysis(radiographId) {
  await delay(300);
  return MOCK_ANALYSIS.radiographId === radiographId ? MOCK_ANALYSIS : null;
}

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

/* ================================================================
   MODE: JSON FILES
   ================================================================ */
async function jsonGetPatient(id) {
  const cfg = PMS_CONFIG.json;
  const url = `${cfg.patientsPath}${id}${cfg.fileExtension}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Patient JSON not found: ${url}`);
  return res.json();
}

async function jsonGetRadiographs(patientId) {
  const cfg = PMS_CONFIG.json;
  const url = `${cfg.radiographsPath}patient-${patientId}${cfg.fileExtension}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Radiographs JSON not found: ${url}`);
  return res.json();
}

async function jsonGetAnalysis(radiographId) {
  const cfg = PMS_CONFIG.json;
  const url = `${cfg.radiographsPath}${radiographId}-analysis${cfg.fileExtension}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Analysis JSON not found: ${url}`);
  return res.json();
}

/* ================================================================
   MODE: OPEN DENTAL
   ================================================================ */
function buildOpenDentalUrl(path) {
  const cfg = PMS_CONFIG.openDental;
  const base = cfg.directCors ? cfg.baseUrl : (cfg.proxyUrl || cfg.baseUrl);
  return `${base}${path}`;
}

async function openDentalFetch(path, options = {}) {
  const cfg = PMS_CONFIG.openDental;
  const url = buildOpenDentalUrl(path);
  const headers = {
    'Content-Type': 'application/json',
    ...(cfg.directCors ? {
      'Authorization': 'Basic ' + btoa(`${cfg.username}:${cfg.password}`)
    } : {}),
    ...options.headers
  };
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) throw new Error(`Open Dental API error: ${res.status} ${res.statusText}`);
  return res.json();
}

async function odGetPatient(id) {
  const data = await openDentalFetch(`/patients/${id}`);
  return normalizeOpenDentalPatient(data);
}

async function odGetRadiographs(patientId) {
  const data = await openDentalFetch(`/radiographs?PatNum=${patientId}`);
  return (Array.isArray(data) ? data : [data]).map(normalizeOpenDentalRadiograph);
}

async function odGetAnalysis(radiographId) {
  // Open Dental does not have native AI analysis; this would come from your middleware
  return openDentalFetch(`/radiographs/${radiographId}/analysis`);
}

function normalizeOpenDentalPatient(raw) {
  const fname = raw.FName || raw.firstName || '';
  const lname = raw.LName || raw.lastName || '';
  return {
    id: String(raw.PatNum || raw.id || ''),
    firstName: fname,
    lastName: lname,
    initials: `${fname[0] || ''}${lname[0] || ''}`.toUpperCase(),
    dob: raw.Birthdate || raw.dob || '',
    displayDob: formatDate(raw.Birthdate || raw.dob),
    phone: raw.HmPhone || raw.phone || '',
    email: raw.Email || raw.email || ''
  };
}

function normalizeOpenDentalRadiograph(raw) {
  return {
    id: String(raw.DocNum || raw.id || ''),
    patientId: String(raw.PatNum || raw.patientId || ''),
    type: raw.ImgType || raw.type || 'Unknown',
    date: raw.DateCreated || raw.date || '',
    displayDate: formatDate(raw.DateCreated || raw.date),
    imageUrl: raw.rawBase64 ? `data:image/jpeg;base64,${raw.rawBase64}` : (raw.imageUrl || ''),
    priorIds: raw.priorIds || [],
    priors: raw.priors || []
  };
}

/* ================================================================
   MODE: DENTRIX
   ================================================================ */
async function dentrixFetch(path, options = {}) {
  const cfg = PMS_CONFIG.dentrix;
  const url = cfg.proxyUrl ? `${cfg.proxyUrl}${path}` : `${cfg.baseUrl}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    'X-Api-Key': cfg.apiKey,
    ...options.headers
  };
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) throw new Error(`Dentrix API error: ${res.status} ${res.statusText}`);
  return res.json();
}

async function dentrixGetPatient(id) {
  const data = await dentrixFetch(`/patients/${id}`);
  return normalizeDentrixPatient(data);
}

async function dentrixGetRadiographs(patientId) {
  const data = await dentrixFetch(`/patients/${patientId}/radiographs`);
  return (Array.isArray(data) ? data : data.radiographs || []).map(normalizeDentrixRadiograph);
}

async function dentrixGetAnalysis(radiographId) {
  return dentrixFetch(`/radiographs/${radiographId}/analysis`);
}

function normalizeDentrixPatient(raw) {
  const fname = raw.firstName || raw.FirstName || '';
  const lname = raw.lastName || raw.LastName || '';
  return {
    id: String(raw.id || raw.patientId || ''),
    firstName: fname,
    lastName: lname,
    initials: `${fname[0] || ''}${lname[0] || ''}`.toUpperCase(),
    dob: raw.dateOfBirth || raw.dob || '',
    displayDob: formatDate(raw.dateOfBirth || raw.dob),
    phone: raw.phone || raw.homePhone || '',
    email: raw.email || ''
  };
}

function normalizeDentrixRadiograph(raw) {
  return {
    id: String(raw.id || raw.radiographId || ''),
    patientId: String(raw.patientId || ''),
    type: raw.type || raw.imageType || 'Unknown',
    date: raw.date || raw.acquisitionDate || '',
    displayDate: formatDate(raw.date || raw.acquisitionDate),
    imageUrl: raw.imageUrl || raw.url || '',
    priorIds: raw.priorIds || [],
    priors: raw.priors || []
  };
}

/* ================================================================
   MODE: GENERIC REST API
   ================================================================ */
async function genericFetch(path, options = {}) {
  const cfg = PMS_CONFIG.generic;
  const url = `${cfg.baseUrl}${path}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(cfg.apiKey ? { 'Authorization': `Bearer ${cfg.apiKey}` } : {}),
    ...cfg.headers,
    ...options.headers
  };
  const res = await fetch(url, { ...options, headers });
  if (!res.ok) throw new Error(`Generic API error: ${res.status} ${res.statusText}`);
  return res.json();
}

async function genericGetPatient(id) {
  const path = interpolate(PMS_CONFIG.generic.endpoints.patient, { id });
  return genericFetch(path);
}

async function genericGetRadiographs(patientId) {
  const path = interpolate(PMS_CONFIG.generic.endpoints.patientRadiographs, { id: patientId });
  return genericFetch(path);
}

async function genericGetAnalysis(radiographId) {
  const path = interpolate(PMS_CONFIG.generic.endpoints.analysis, { id: radiographId });
  return genericFetch(path);
}

function interpolate(template, vars) {
  return template.replace(/\{(\w+)\}/g, (_, key) => vars[key] ?? '');
}

/* ================================================================
   HELPERS
   ================================================================ */
function formatDate(isoOrString) {
  if (!isoOrString) return '';
  const d = new Date(isoOrString);
  if (isNaN(d)) return isoOrString;
  return `${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}/${d.getFullYear()}`;
}

/* ================================================================
   DISPATCHER
   ================================================================ */
const DISPATCH = {
  mock:    { getPatient: mockGetPatient,    getRadiographs: mockGetRadiographs,    getAnalysis: mockGetAnalysis },
  json:    { getPatient: jsonGetPatient,    getRadiographs: jsonGetRadiographs,    getAnalysis: jsonGetAnalysis },
  opendental: { getPatient: odGetPatient,   getRadiographs: odGetRadiographs,      getAnalysis: odGetAnalysis },
  softdent:{ getPatient: jsonGetPatient,    getRadiographs: jsonGetRadiographs,    getAnalysis: jsonGetAnalysis },
  dentrix: { getPatient: dentrixGetPatient, getRadiographs: dentrixGetRadiographs, getAnalysis: dentrixGetAnalysis },
  generic: { getPatient: genericGetPatient, getRadiographs: genericGetRadiographs, getAnalysis: genericGetAnalysis }
};

function getDispatcher() {
  const mode = PMS_CONFIG.mode;
  if (!DISPATCH[mode]) {
    console.warn(`[PMS] Unknown mode "${mode}". Falling back to mock.`);
    return DISPATCH.mock;
  }
  return DISPATCH[mode];
}

/* ================================================================
   PUBLIC API
   ================================================================ */

export async function loadPatient(id) {
  const key = cacheKey(PMS_CONFIG.mode, 'patient', id);
  let data = getCached(key);
  if (data) return data;
  data = await getDispatcher().getPatient(id);
  setCached(key, data);
  return data;
}

export async function loadRadiographs(patientId) {
  const key = cacheKey(PMS_CONFIG.mode, 'radiographs', patientId);
  let data = getCached(key);
  if (data) return data;
  data = await getDispatcher().getRadiographs(patientId);
  setCached(key, data);
  return data;
}

export async function loadAnalysis(radiographId) {
  const key = cacheKey(PMS_CONFIG.mode, 'analysis', radiographId);
  let data = getCached(key);
  if (data) return data;
  data = await getDispatcher().getAnalysis(radiographId);
  setCached(key, data);
  return data;
}

export async function loadPatientRecord(patientId) {
  const patient = await loadPatient(patientId);
  const radiographs = await loadRadiographs(patientId);
  let analysis = null;
  if (radiographs.length > 0) {
    analysis = await loadAnalysis(radiographs[0].id);
  }
  return { patient, radiographs, analysis };
}

export function buildReport(patient, radiograph, analysis) {
  const now = new Date();
  return {
    header: {
      practice: 'New Ridge Family Dental',
      doctor: 'Michael Reno, DDS',
      address: '2135 North Ridge Rd Ste 700, Wichita, KS 67212',
      phone: '(316) 722-6060',
      generated: formatDate(now.toISOString()),
      examType: radiograph?.type || 'Panoramic Radiograph',
      reportId: `RAD-${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}-001`
    },
    patient: {
      name: `${patient.firstName} ${patient.lastName}`,
      dob: patient.displayDob,
      id: patient.id,
      dateOfExam: radiograph?.displayDate || formatDate(now.toISOString()),
      referringDentist: 'Michael Reno, DDS',
      reportId: `RAD-${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}-001`
    },
    image: {
      caption: `Figure 1 — ${radiograph?.type || 'Panoramic'} radiograph, ${patient.firstName} ${patient.lastName}.`,
      url: radiograph?.imageUrl || ''
    },
    impressions: analysis?.report?.clinicalImpressions || analysis?.paragraphs?.map(p => p.text) || [],
    findings: analysis?.findings || [],
    recommendations: analysis?.report?.recommendations || [],
    measurements: analysis?.measurements || []
  };
}

export function exportRecord(record, filename = 'patient-record.json') {
  const blob = new Blob([JSON.stringify(record, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

/* ================================================================
   PHASE 2 — COLLABORATION & TREATMENT PLAN API
   ═══════════════════════════════════════════════════════════════ */

let inMemoryThreads = [...MOCK_ANNOTATION_THREADS];

export async function loadAnnotationThreads(radiographId) {
  await delay(100);
  return inMemoryThreads.filter(t => {
    const ann = MOCK_ANALYSIS.annotations.find(a => a.id === t.annotationId);
    return ann != null;
  });
}

export async function saveAnnotationThread(thread) {
  await delay(100);
  const existing = inMemoryThreads.findIndex(t => t.id === thread.id);
  if (existing >= 0) inMemoryThreads[existing] = thread;
  else inMemoryThreads.push({ ...thread, id: thread.id || `thread-${Date.now()}` });
  return thread;
}

export async function loadTreatmentOverlays(radiographId) {
  await delay(100);
  return MOCK_TREATMENT_OVERLAYS;
}

export async function loadPacsStatus() {
  await delay(80);
  const status = { ...MOCK_PACS_STATUS };
  status.latency = Math.max(20, status.latency + Math.floor(Math.random() * 20 - 10));
  status.lastSync = new Date().toISOString();
  return status;
}

export function buildTreatmentPlanReport(overlays) {
