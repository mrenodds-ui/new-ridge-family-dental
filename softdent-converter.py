#!/usr/bin/env python3
"""
SoftDent Export Converter — New Ridge Family Dental
====================================================
Converts SoftDent-exported CSV/text files into JSON for the Radiograph Viewer.

SoftDent (classic) can export patient lists and reports to delimited text.
This script reads those exports and produces the JSON format the viewer expects.

USAGE:
    python softdent-converter.py --patients softdent_patients.csv --output ./data

SOFTDENT EXPORT SETUP:
1. In SoftDent, go to Reports → Patient List (or Patient Information)
2. Export to a delimited text file (.CSV or .TXT)
3. Note the column headers — this script auto-detects common SoftDent fields
4. Run this script to convert to JSON

The script will create:
    data/patients/{patientId}.json
    data/radiographs/patient-{patientId}.json
"""

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# ================================================================
# FIELD MAPPINGS — SoftDent column names → our schema
# ================================================================
PATIENT_FIELD_MAP = {
    # Common SoftDent export column names
    'pat num': 'id',
    'patient number': 'id',
    'patient id': 'id',
    'patnum': 'id',
    'account': 'id',
    'account number': 'id',
    'acct': 'id',

    'first name': 'firstName',
    'fname': 'firstName',
    'first': 'firstName',

    'last name': 'lastName',
    'lname': 'lastName',
    'last': 'lastName',

    'birth date': 'dob',
    'birthdate': 'dob',
    'date of birth': 'dob',
    'dob': 'dob',
    'birth': 'dob',

    'home phone': 'phone',
    'phone': 'phone',
    'telephone': 'phone',
    'hm phone': 'phone',

    'email': 'email',
    'e-mail': 'email',
    'email address': 'email',
}

# ================================================================
# HELPERS
# ================================================================

def normalize_header(header):
    """Clean and normalize a CSV header for matching."""
    return header.strip().lower().replace('_', ' ').replace('-', ' ')

def detect_dialect(filepath):
    """Auto-detect CSV delimiter and formatting."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        sample = f.read(8192)
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(sample, delimiters=',\t;|')
        return dialect
    except csv.Error:
        # Fallback to comma
        return csv.excel

def parse_date(value):
    """Try multiple date formats common in SoftDent exports."""
    if not value or not value.strip():
        return ''
    value = value.strip()
    formats = [
        '%m/%d/%Y', '%m/%d/%y',
        '%Y-%m-%d',
        '%d/%m/%Y', '%d/%m/%y',
        '%m-%d-%Y', '%m-%d-%y',
        '%Y%m%d',
        '%m/%d/%Y %H:%M:%S',
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    # If all fail, return as-is
    return value

def format_display_date(iso_date):
    """Convert ISO date to MM/DD/YYYY display format."""
    if not iso_date:
        return ''
    try:
        dt = datetime.strptime(iso_date, '%Y-%m-%d')
        return dt.strftime('%m/%d/%Y')
    except ValueError:
        return iso_date

def make_initials(first, last):
    """Generate patient initials."""
    f = (first or '').strip()
    l = (last or '').strip()
    return f'{f[0] if f else ""}{l[0] if l else ""}'.upper()

# ================================================================
# CONVERTERS
# ================================================================

def convert_patients(csv_path, out_dir):
    """Convert SoftDent patient export CSV to individual patient JSON files."""
    dialect = detect_dialect(csv_path)

    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f, dialect=dialect)
        raw_headers = reader.fieldnames or []
        # Build normalized header → original header map
        header_map = {normalize_header(h): h for h in raw_headers}

        patients_dir = Path(out_dir) / 'patients'
        patients_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for row in reader:
            # Extract mapped fields
            data = {}
            for norm, target in PATIENT_FIELD_MAP.items():
                if norm in header_map:
                    val = row.get(header_map[norm], '').strip()
                    if val:
                        data[target] = val

            patient_id = data.get('id', '')
            if not patient_id:
                # Try to find any column that looks like an ID
                for h in raw_headers:
                    if 'id' in h.lower() or 'num' in h.lower() or 'account' in h.lower():
                        val = row.get(h, '').strip()
                        if val and val not in data.values():
                            patient_id = val
                            data['id'] = val
                            break

            if not patient_id:
                print(f"  ⚠ Skipping row with no patient ID: {row}")
                continue

            # Normalize DOB
            if 'dob' in data:
                data['dob'] = parse_date(data['dob'])
                data['displayDob'] = format_display_date(data['dob'])

            data['initials'] = make_initials(data.get('firstName', ''), data.get('lastName', ''))

            out_path = patients_dir / f"{patient_id}.json"
            with open(out_path, 'w', encoding='utf-8') as out:
                json.dump(data, out, indent=2, ensure_ascii=False)
            count += 1

    print(f"  ✓ Wrote {count} patient files to {patients_dir}")
    return count

def convert_radiographs(csv_path, out_dir, patient_id=None):
    """
    Convert SoftDent procedure/treatment export to radiograph JSON.
    SoftDent exports procedures with ADA codes — we map imaging codes to radiographs.
    """
    dialect = detect_dialect(csv_path)

    # ADA codes that indicate radiographs/imaging
    IMAGING_CODES = {
        '0210', '0220', '0230', '0240',   # Intraoral
        '0250', '0260', '0270', '0272',   # Extraoral
        '0273', '0274', '0277',            # Panoramic / CBCT
        '0330', '0340',                     # Additional films
        'D0210', 'D0220', 'D0230', 'D0240',
        'D0250', 'D0260', 'D0270', 'D0272',
        'D0273', 'D0274', 'D0277',
        'D0330', 'D0340',
    }

    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f, dialect=dialect)
        raw_headers = reader.fieldnames or []
        header_map = {normalize_header(h): h for h in raw_headers}

        # Try to find key columns
        code_col = None
        for key in ['ada code', 'code', 'procedure code', 'proc code', 'cdt code']:
            if key in header_map:
                code_col = header_map[key]
                break

        date_col = None
        for key in ['date', 'procedure date', 'service date', 'visit date', 'trans date']:
            if key in header_map:
                date_col = header_map[key]
                break

        pat_col = None
        for key in ['pat num', 'patient number', 'patient id', 'patnum', 'account']:
            if key in header_map:
                pat_col = header_map[key]
                break

        desc_col = None
        for key in ['description', 'proc desc', 'procedure', 'procedure description', 'service']:
            if key in header_map:
                desc_col = header_map[key]
                break

        if not code_col:
            print("  ⚠ Could not find procedure code column. Available columns:")
            print(f"     {raw_headers}")
            return 0

        radiographs_by_patient = {}

        for row in reader:
            code = row.get(code_col or '', '').strip().upper()
            if code.startswith('D'):
                code = code[1:]  # Strip D prefix for comparison
            code_stripped = re.sub(r'[^0-9]', '', code)

            if code_stripped not in IMAGING_CODES and code not in IMAGING_CODES:
                continue

            pid = patient_id or row.get(pat_col or '', '').strip()
            if not pid:
                continue

            raw_date = row.get(date_col or '', '').strip()
            iso_date = parse_date(raw_date)
            display_date = format_display_date(iso_date)
            desc = row.get(desc_col or '', '').strip()

            # Determine radiograph type from code
            rtype = 'Radiograph'
            if code_stripped in {'0272', '0273', '0274', '0277'} or code in {'D0272', 'D0273', 'D0274', 'D0277'}:
                rtype = 'Panoramic'
            elif code_stripped in {'0270'} or code in {'D0270'}:
                rtype = 'Extraoral'
            elif desc and 'pano' in desc.lower():
                rtype = 'Panoramic'
            elif desc and 'cbct' in desc.lower():
                rtype = 'CBCT'
            elif desc and 'ceph' in desc.lower():
                rtype = 'Cephalometric'

            rad_id = f"RAD-{iso_date.replace('-', '')}-{pid}-{(len(radiographs_by_patient.get(pid, [])) + 1):03d}" if iso_date else f"RAD-{pid}-{(len(radiographs_by_patient.get(pid, [])) + 1):03d}"

            entry = {
                'id': rad_id,
                'patientId': pid,
                'type': rtype,
                'date': iso_date,
                'displayDate': display_date,
                'adaCode': code,
                'description': desc,
                'imageUrl': '',
                'priorIds': [],
                'priors': []
            }

            radiographs_by_patient.setdefault(pid, []).append(entry)

    # Write out
    rx_dir = Path(out_dir) / 'radiographs'
    rx_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for pid, rx_list in radiographs_by_patient.items():
        # Sort by date descending (newest first)
        rx_list.sort(key=lambda x: x['date'] or '', reverse=True)

        # Link priors
        for i, rx in enumerate(rx_list):
            priors = rx_list[i+1:i+4]  # Up to 3 prior exams
            rx['priorIds'] = [p['id'] for p in priors]
            rx['priors'] = [{'id': p['id'], 'date': p['displayDate'], 'label': f"Prior — {p['displayDate']}"} for p in priors]

        out_path = rx_dir / f"patient-{pid}.json"
        with open(out_path, 'w', encoding='utf-8') as out:
            json.dump(rx_list, out, indent=2, ensure_ascii=False)
        count += 1

    print(f"  ✓ Wrote radiograph lists for {count} patients to {rx_dir}")
    return count

def generate_analysis_stub(patient_id, radiograph_id, out_dir):
    """Generate a placeholder analysis JSON for a radiograph.
    In production, this would come from your AI pipeline (Qwen3-VL).
    """
    rx_dir = Path(out_dir) / 'radiographs'
    rx_dir.mkdir(parents=True, exist_ok=True)

    stub = {
        "radiographId": radiograph_id,
        "overview": "Analysis pending — run through AI pipeline for findings.",
        "findings": [],
        "paragraphs": [
            {"heading": "Overview", "text": "Analysis pending.", "confidence": None}
        ],
        "measurements": [],
        "annotations": [],
        "report": {
            "clinicalImpressions": ["Pending AI review."],
            "recommendations": ["Complete AI analysis before generating patient report."]
        }
    }

    out_path = rx_dir / f"{radiograph_id}-analysis.json"
    with open(out_path, 'w', encoding='utf-8') as out:
        json.dump(stub, out, indent=2, ensure_ascii=False)
    print(f"  ✓ Wrote analysis stub: {out_path}")

def main():
    parser = argparse.ArgumentParser(
        description='Convert SoftDent exports to Radiograph Viewer JSON'
    )
    parser.add_argument('--patients', '-p', required=True,
                        help='Path to SoftDent patient export CSV')
    parser.add_argument('--procedures', '-r', default=None,
                        help='Path to SoftDent procedure/treatment export CSV (optional)')
    parser.add_argument('--output', '-o', default='./data',
                        help='Output directory for JSON files (default: ./data)')
    parser.add_argument('--patient-id', default=None,
                        help='Override patient ID for procedure file (if it lacks patient column)')
    parser.add_argument('--stub-analysis', action='store_true',
                        help='Generate empty analysis stubs for each radiograph')
    args = parser.parse_args()

    print("=" * 60)
    print("SoftDent Export Converter")
    print("=" * 60)

    if not os.path.exists(args.patients):
        print(f"ERROR: Patient file not found: {args.patients}")
        sys.exit(1)

    out_path = Path(args.output)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Convert patients
    print(f"\n[1/3] Converting patients from: {args.patients}")
    patient_count = convert_patients(args.patients, args.output)

    # 2. Convert procedures → radiographs
    rx_count = 0
    if args.procedures:
        if not os.path.exists(args.procedures):
            print(f"WARNING: Procedure file not found: {args.procedures}")
        else:
            print(f"\n[2/3] Converting procedures from: {args.procedures}")
            rx_count = convert_radiographs(args.procedures, args.output, args.patient_id)

    # 3. Generate analysis stubs if requested
    if args.stub_analysis:
        print(f"\n[3/3] Generating analysis stubs...")
        rx_dir = Path(args.output) / 'radiographs'
        if rx_dir.exists():
            for rx_file in rx_dir.glob('patient-*.json'):
                with open(rx_file, 'r', encoding='utf-8') as f:
                    rx_list = json.load(f)
                for rx in rx_list:
                    generate_analysis_stub(rx['patientId'], rx['id'], args.output)
        else:
            print("  No radiograph files found — skipping stubs.")

    print("\n" + "=" * 60)
    print(f"Done! {patient_count} patients converted.")
    if rx_count:
        print(f"       {rx_count} patient radiograph lists created.")
    print(f"\nNext steps:")
    print(f"  1. Set mode: 'json' in js/pms-config.js")
    print(f"  2. Open radiographs.html — data will load from {out_path}")
    print(f"  3. Replace analysis stubs with real AI output when ready.")
    print("=" * 60)

if __name__ == '__main__':
    main()
