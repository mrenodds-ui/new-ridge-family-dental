#!/usr/bin/env python3
"""
SoftDent dBase DAT Reader — New Ridge Family Dental
=====================================================
Reads SoftDent's native dBase III/IV .DAT files directly — no CSV export needed.

SoftDent stores patient and appointment data in classic dBase/FoxPro tables:
    C:\softdent\PATIENT.DAT   → Patient demographics
    C:\softdent\APPT.DAT      → Appointments
    C:\softdent\PROC.DAT      → Procedures / treatment history
    C:\softdent\CLAIM.DAT     → Insurance claims

This script reads those binary files and exports JSON for the Radiograph Viewer.

USAGE:
    python softdent-dat-reader.py --datadir "C:\softdent" --output ./data

REQUIRES:
    Python 3.8+ (no external packages — pure standard library)
"""

import argparse
import json
import os
import struct
import sys
from datetime import datetime, date
from pathlib import Path


# ================================================================
# dBase III/IV File Format Parser (pure Python, no deps)
# ================================================================

class DbfReader:
    """Read dBase III/IV/FoxPro .DBF / .DAT files."""

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.header = {}
        self.fields = []
        self._records = []
        self._parse_header()

    def _parse_header(self):
        with open(self.filepath, 'rb') as f:
            # Header (32 bytes)
            header_bytes = f.read(32)
            if len(header_bytes) < 32:
                raise ValueError(f"File too small: {self.filepath}")

            version = header_bytes[0]
            year = header_bytes[1]
            month = header_bytes[2]
            day = header_bytes[3]
            num_records = struct.unpack('<I', header_bytes[4:8])[0]
            header_size = struct.unpack('<H', header_bytes[8:10])[0]
            record_size = struct.unpack('<H', header_bytes[10:12])[0]

            # dBase year is offset from 1900 (or 2000 for some versions)
            full_year = 1900 + year if year < 80 else 2000 + (year - 100) if year >= 100 else 1900 + year

            self.header = {
                'version': version,
                'last_update': date(full_year, month, day).isoformat() if 1 <= month <= 12 and 1 <= day <= 31 else None,
                'num_records': num_records,
                'header_size': header_size,
                'record_size': record_size,
            }

            # Field descriptors (32 bytes each, terminated by 0x0D)
            field_count = (header_size - 33) // 32
            for i in range(field_count):
                field_bytes = f.read(32)
                if len(field_bytes) < 32:
                    break
                if field_bytes[0] == 0x0D:
                    break

                name = field_bytes[0:11].split(b'\x00')[0].decode('latin-1', errors='ignore').strip()
                type_code = chr(field_bytes[11])
                offset = struct.unpack('<H', field_bytes[12:14])[0] if len(field_bytes) >= 14 else 0
                length = field_bytes[16]
                decimal = field_bytes[17]

                self.fields.append({
                    'name': name,
                    'type': type_code,
                    'length': length,
                    'decimal': decimal,
                    'offset': offset,
                })

            # Skip to end of header
            f.seek(header_size)

            # Read records
            for _ in range(num_records):
                record_bytes = f.read(record_size)
                if len(record_bytes) < record_size:
                    break

                # Deleted record marker
                deleted = record_bytes[0] == 0x2A  # '*'
                if deleted:
                    continue

                record = {}
                pos = 1  # Skip deletion flag
                for field in self.fields:
                    raw = record_bytes[pos:pos + field['length']]
                    value = raw.decode('latin-1', errors='ignore').strip()

                    if field['type'] == 'D' and len(value) == 8:
                        # Date: YYYYMMDD
                        try:
                            value = f"{value[0:4]}-{value[4:6]}-{value[6:8]}"
                        except ValueError:
                            pass
                    elif field['type'] == 'N' or field['type'] == 'F':
                        # Numeric/Float
                        if value:
                            try:
                                if field['decimal'] > 0:
                                    value = float(value)
                                else:
                                    value = int(value)
                            except ValueError:
                                pass
                        else:
                            value = None
                    elif field['type'] == 'L':
                        # Logical
                        value = value.upper() in ('Y', 'T', '1')

                    record[field['name']] = value
                    pos += field['length']

                self._records.append(record)

    def __iter__(self):
        return iter(self._records)

    def __len__(self):
        return len(self._records)

    def records(self):
        return self._records


# ================================================================
# SoftDent Schema Mapping
# ================================================================

# Common SoftDent field names found in PATIENT.DAT
SOFTDENT_PATIENT_MAP = {
    'PATNUM': 'id',
    'ACCOUNT': 'id',
    'PAT_ID': 'id',
    'FNAME': 'firstName',
    'FIRSTNAME': 'firstName',
    'FIRST_NAME': 'firstName',
    'LNAME': 'lastName',
    'LASTNAME': 'lastName',
    'LAST_NAME': 'lastName',
    'BIRTHDATE': 'dob',
    'DOB': 'dob',
    'BDATE': 'dob',
    'PHONE1': 'phone',
    'PHONE': 'phone',
    'HOMEPHONE': 'phone',
    'EMAIL': 'email',
    'EMAILADDR': 'email',
    'EMAIL_ADDR': 'email',
    'ADDR1': 'address',
    'ADDRESS1': 'address',
    'CITY': 'city',
    'STATE': 'state',
    'ZIP': 'zip',
}

# Common SoftDent procedure fields
SOFTDENT_PROC_MAP = {
    'PATNUM': 'patientId',
    'ACCOUNT': 'patientId',
    'DATE': 'date',
    'PROC_DATE': 'date',
    'SERV_DATE': 'date',
    'ADA_CODE': 'adaCode',
    'CODE': 'adaCode',
    'PROC_CODE': 'adaCode',
    'DESCRIPTION': 'description',
    'DESC': 'description',
    'PROC_DESC': 'description',
    'TOOTH': 'tooth',
    'SURFACE': 'surface',
    'FEE': 'fee',
    'PROVIDER': 'provider',
}


# ================================================================
# HELPERS
# ================================================================

def parse_softdent_date(value):
    """Parse various SoftDent date formats."""
    if not value:
        return ''
    if isinstance(value, str):
        # ISO format
        if len(value) == 10 and value[4] == '-' and value[7] == '-':
            return value
        # M/D/Y or MM/DD/YYYY
        for fmt in ['%m/%d/%Y', '%m/%d/%y', '%Y%m%d', '%d/%m/%Y']:
            try:
                return datetime.strptime(value, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
    return str(value)


def format_display_date(iso_date):
    """Convert ISO date to MM/DD/YYYY."""
    if not iso_date:
        return ''
    try:
        return datetime.strptime(iso_date, '%Y-%m-%d').strftime('%m/%d/%Y')
    except ValueError:
        return iso_date


def make_initials(first, last):
    f = str(first or '').strip()
    l = str(last or '').strip()
    return f'{f[0] if f else ""}{l[0] if l else ""}'.upper()


# ================================================================
# CONVERTERS
# ================================================================

def convert_patient_dat(dat_path, out_dir):
    """Read SoftDent PATIENT.DAT and write individual JSON files."""
    print(f"[1/3] Reading patient data from: {dat_path}")
    dbf = DbfReader(dat_path)
    print(f"      Found {len(dbf)} records, {len(dbf.fields)} fields")

    patients_dir = Path(out_dir) / 'patients'
    patients_dir.mkdir(parents=True, exist_ok=True)

    # Show available fields for debugging
    field_names = [f['name'] for f in dbf.fields]
    print(f"      Fields: {', '.join(field_names[:8])}{'...' if len(field_names) > 8 else ''}")

    count = 0
    for row in dbf:
        data = {}
        for src, dest in SOFTDENT_PATIENT_MAP.items():
            if src in row and row[src]:
                data[dest] = row[src]

        patient_id = data.get('id', '')
        if not patient_id:
            continue

        # Normalize DOB
        if 'dob' in data:
            data['dob'] = parse_softdent_date(data['dob'])
            data['displayDob'] = format_display_date(data['dob'])

        data['initials'] = make_initials(data.get('firstName', ''), data.get('lastName', ''))

        out_path = patients_dir / f"{patient_id}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        count += 1

    print(f"  ✓ Wrote {count} patient files to {patients_dir}")
    return count


def convert_procedure_dat(dat_path, out_dir):
    """Read SoftDent PROC.DAT and write radiograph JSON files."""
    print(f"[2/3] Reading procedure data from: {dat_path}")
    dbf = DbfReader(dat_path)
    print(f"      Found {len(dbf)} records, {len(dbf.fields)} fields")

    field_names = [f['name'] for f in dbf.fields]
    print(f"      Fields: {', '.join(field_names[:8])}{'...' if len(field_names) > 8 else ''}")

    # ADA imaging codes
    IMAGING_CODES = {
        '0210', '0220', '0230', '0240', '0250', '0260', '0270', '0272',
        '0273', '0274', '0277', '0330', '0340',
        'D0210', 'D0220', 'D0230', 'D0240', 'D0250', 'D0260', 'D0270',
        'D0272', 'D0273', 'D0274', 'D0277', 'D0330', 'D0340',
    }

    radiographs_by_patient = {}

    for row in dbf:
        code = str(row.get('ADA_CODE', row.get('CODE', row.get('PROC_CODE', '')))).strip().upper()
        if code.startswith('D'):
            code = code[1:]
        code_clean = ''.join(c for c in code if c.isdigit())

        if code_clean not in IMAGING_CODES and code not in IMAGING_CODES:
            continue

        pid = str(row.get('PATNUM', row.get('ACCOUNT', ''))).strip()
        if not pid:
            continue

        raw_date = str(row.get('DATE', row.get('PROC_DATE', row.get('SERV_DATE', '')))).strip()
        iso_date = parse_softdent_date(raw_date)
        display_date = format_display_date(iso_date)
        desc = str(row.get('DESCRIPTION', row.get('DESC', row.get('PROC_DESC', '')))).strip()
        tooth = str(row.get('TOOTH', '')).strip()

        # Determine radiograph type
        rtype = 'Radiograph'
        if code_clean in {'0272', '0273', '0274', '0277'}:
            rtype = 'Panoramic'
        elif code_clean in {'0270'}:
            rtype = 'Extraoral'
        elif desc and 'pano' in desc.lower():
            rtype = 'Panoramic'
        elif desc and 'cbct' in desc.lower():
            rtype = 'CBCT'
        elif desc and 'ceph' in desc.lower():
            rtype = 'Cephalometric'

        rad_id = f"RAD-{iso_date.replace('-', '') if iso_date else 'unknown'}-{pid}"

        entry = {
            'id': rad_id,
            'patientId': pid,
            'type': rtype,
            'date': iso_date,
            'displayDate': display_date,
            'adaCode': code,
            'description': desc,
            'tooth': tooth,
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
        rx_list.sort(key=lambda x: x['date'] or '', reverse=True)
        for i, rx in enumerate(rx_list):
            rx['id'] = f"RAD-{rx['date'].replace('-', '') if rx['date'] else 'unknown'}-{pid}-{(i+1):03d}"
            priors = rx_list[i+1:i+4]
            rx['priorIds'] = [p['id'] for p in priors]
            rx['priors'] = [{'id': p['id'], 'date': p['displayDate'], 'label': f"Prior — {p['displayDate']}"} for p in priors]

        out_path = rx_dir / f"patient-{pid}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(rx_list, f, indent=2, ensure_ascii=False)
        count += 1

    print(f"  ✓ Wrote radiograph lists for {count} patients to {rx_dir}")
    return count


def generate_analysis_stubs(out_dir):
    """Generate placeholder analysis JSONs for each radiograph."""
    print(f"[3/3] Generating analysis stubs...")
    rx_dir = Path(out_dir) / 'radiographs'
    if not rx_dir.exists():
        print("  No radiograph files found — skipping stubs.")
        return 0

    count = 0
    for rx_file in rx_dir.glob('patient-*.json'):
        with open(rx_file, 'r', encoding='utf-8') as f:
            rx_list = json.load(f)
        for rx in rx_list:
            stub = {
                "radiographId": rx['id'],
                "overview": "Analysis pending — run through AI pipeline for findings.",
                "findings": [],
                "paragraphs": [
                    {"heading": "Overview", "text": "Analysis pending. Replace with Qwen3-VL output.", "confidence": None}
                ],
                "measurements": [],
                "annotations": [],
                "report": {
                    "clinicalImpressions": ["Pending AI review."],
                    "recommendations": ["Complete AI analysis before generating patient report."]
                }
            }
            out_path = rx_dir / f"{rx['id']}-analysis.json"
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(stub, f, indent=2, ensure_ascii=False)
            count += 1

    print(f"  ✓ Wrote {count} analysis stubs.")
    return count


def run(data_dir, output_dir='./data', stub_analysis=False):
    """Run the full conversion from .DAT files."""
    data_path = Path(data_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("SoftDent dBase DAT Reader")
    print(f"  Data directory: {data_path}")
    print(f"  Output directory: {out_path}")
    print("=" * 60)

    # Find .DAT files (case-insensitive)
    dat_files = list(data_path.glob('*.DAT')) + list(data_path.glob('*.dat'))
    if not dat_files:
        print(f"ERROR: No .DAT files found in {data_path}")
        print(f"       Looking for: PATIENT.DAT, PROC.DAT, APPT.DAT")
        return False

    print(f"\nFound {len(dat_files)} .DAT file(s):")
    for f in dat_files:
        print(f"  - {f.name}")

    # Find patient file
    patient_file = None
    for name in ['PATIENT.DAT', 'patient.dat', 'PATIENT.dbf', 'patient.dbf']:
        candidate = data_path / name
        if candidate.exists():
            patient_file = candidate
            break

    # Find procedure file
    proc_file = None
    for name in ['PROC.DAT', 'proc.dat', 'PROCEDUR.DAT', 'procedur.dat', 'TREAT.DAT', 'treat.dat']:
        candidate = data_path / name
        if candidate.exists():
            proc_file = candidate
            break

    patient_count = 0
    if patient_file:
        patient_count = convert_patient_dat(patient_file, output_dir)
    else:
        print("\n  ⚠ No PATIENT.DAT found — skipping patient conversion.")
        print("      Expected: C:\\softdent\\PATIENT.DAT")

    rx_count = 0
    if proc_file:
        rx_count = convert_procedure_dat(proc_file, output_dir)
    else:
        print("\n  ⚠ No PROC.DAT found — skipping procedure conversion.")
        print("      Expected: C:\\softdent\\PROC.DAT")

    stub_count = 0
    if stub_analysis:
        stub_count = generate_analysis_stubs(output_dir)

    print("\n" + "=" * 60)
    print("Done!")
    print(f"  {patient_count} patients converted")
    print(f"  {rx_count} patient radiograph lists created")
    if stub_analysis:
        print(f"  {stub_count} analysis stubs generated")
    print(f"\nNext steps:")
    print(f"  1. Set mode: 'json' in js/pms-config.js")
    print(f"  2. Open radiographs.html — data loads from {out_path}")
    print(f"  3. Replace analysis stubs with real AI output when ready.")
    print("=" * 60)
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Read SoftDent dBase .DAT files directly and convert to JSON'
    )
    parser.add_argument('--datadir', '-d', required=True,
                        help='Directory containing SoftDent .DAT files (e.g., C:\\softdent)')
    parser.add_argument('--output', '-o', default='./data',
                        help='Output directory for JSON files (default: ./data)')
    parser.add_argument('--stub-analysis', action='store_true',
                        help='Generate empty analysis stubs for each radiograph')
    args = parser.parse_args()

    run(data_dir=args.datadir, output_dir=args.output, stub_analysis=args.stub_analysis)


if __name__ == '__main__':
    main()
