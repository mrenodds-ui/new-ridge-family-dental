#!/usr/bin/env python3
"""
SoftDent Export Watcher — New Ridge Family Dental
==================================================
Monitors your SoftDent export folder and automatically runs the converter
when new or updated CSV files appear.

USAGE:
    python softdent-watch.py --watch "C:\softdent\exports" --output ./data

Or run it silently in the background (logs to file):
    python softdent-watch.py --watch "C:\softdent\exports" --output ./data --log watcher.log

WINDOWS TASK SCHEDULER:
    See SOFTDENT_SETUP.md for step-by-step instructions.
"""

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Make sure we can import the converter from the same directory
try:
    from softdent_converter import run as run_converter
except ImportError:
    # Try importing from same directory with underscore name
    import importlib.util
    converter_path = Path(__file__).parent / 'softdent-converter.py'
    if converter_path.exists():
        spec = importlib.util.spec_from_file_location("softdent_converter", converter_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        run_converter = mod.run
    else:
        print("ERROR: softdent-converter.py not found in the same directory.")
        sys.exit(1)


# ================================================================
# FILE WATCHER
# ================================================================

class FileWatcher:
    def __init__(self, watch_dir, patients_pattern, procedures_pattern,
                 output_dir, patient_id, stub_analysis, log_file=None):
        self.watch_dir = Path(watch_dir)
        self.patients_pattern = patients_pattern
        self.procedures_pattern = procedures_pattern
        self.output_dir = output_dir
        self.patient_id = patient_id
        self.stub_analysis = stub_analysis
        self.log_file = log_file

        self._last_hash = None
        self._running = True

    def log(self, msg):
        line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
        print(line)
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(line + '\n')

    def _find_files(self):
        """Find the most recently modified matching files."""
        patients = sorted(
            self.watch_dir.glob(self.patients_pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        procedures = sorted(
            self.watch_dir.glob(self.procedures_pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        return (patients[0] if patients else None,
                procedures[0] if procedures else None)

    def _compute_hash(self, patients_file, procedures_file):
        """Compute a simple hash of file paths + modification times."""
        hasher = hashlib.md5()
        for f in (patients_file, procedures_file):
            if f and f.exists():
                stat = f.stat()
                hasher.update(str(f.resolve()).encode())
                hasher.update(str(stat.st_mtime).encode())
                hasher.update(str(stat.st_size).encode())
        return hasher.hexdigest()

    def _run_conversion(self, patients_file, procedures_file):
        """Execute the converter."""
        self.log("→ Change detected. Running converter…")
        try:
            success = run_converter(
                patients_file=str(patients_file),
                procedures_file=str(procedures_file) if procedures_file else None,
                output_dir=self.output_dir,
                patient_id=self.patient_id,
                stub_analysis=self.stub_analysis
            )
            if success:
                self.log("✓ Conversion complete.")
            else:
                self.log("✗ Conversion failed.")
        except Exception as e:
            self.log(f"✗ Error during conversion: {e}")

    def run_once(self):
        """Run a single check + conversion cycle."""
        if not self.watch_dir.exists():
            self.log(f"⚠ Watch directory does not exist: {self.watch_dir}")
            return False

        patients_file, procedures_file = self._find_files()

        if not patients_file:
            self.log(f"⚠ No patient file matching '{self.patients_pattern}' found in {self.watch_dir}")
            return False

        current_hash = self._compute_hash(patients_file, procedures_file)

        if current_hash != self._last_hash:
            self._last_hash = current_hash
            self._run_conversion(patients_file, procedures_file)
            return True
        return False

    def run_continuous(self, interval_sec=30):
        """Run in a loop, checking for changes every N seconds."""
        self.log("=" * 60)
        self.log("SoftDent Export Watcher started")
        self.log(f"  Watching: {self.watch_dir}")
        self.log(f"  Patient pattern:  {self.patients_pattern}")
        self.log(f"  Procedure pattern: {self.procedures_pattern}")
        self.log(f"  Output: {self.output_dir}")
        self.log(f"  Check interval: {interval_sec}s")
        self.log("=" * 60)

        # Initial run
        self.run_once()

        try:
            while self._running:
                time.sleep(interval_sec)
                self.run_once()
        except KeyboardInterrupt:
            self.log("\nWatcher stopped by user.")

    def stop(self):
        self._running = False


def main():
    parser = argparse.ArgumentParser(description='Watch SoftDent export folder and auto-convert')
    parser.add_argument('--watch', '-w', required=True,
                        help='Directory to watch for SoftDent export files')
    parser.add_argument('--patients-pattern', default='*patient*.csv',
                        help='Glob pattern for patient export files (default: *patient*.csv)')
    parser.add_argument('--procedures-pattern', default='*procedure*.csv',
                        help='Glob pattern for procedure export files (default: *procedure*.csv)')
    parser.add_argument('--output', '-o', default='./data',
                        help='Output directory for JSON files')
    parser.add_argument('--patient-id', default=None,
                        help='Override patient ID for procedure file')
    parser.add_argument('--stub-analysis', action='store_true',
                        help='Generate analysis stubs')
    parser.add_argument('--interval', '-i', type=int, default=30,
                        help='Check interval in seconds (default: 30)')
    parser.add_argument('--once', action='store_true',
                        help='Run once and exit (no continuous watching)')
    parser.add_argument('--log', '-l', default=None,
                        help='Log file path (optional)')
    args = parser.parse_args()

    watcher = FileWatcher(
        watch_dir=args.watch,
        patients_pattern=args.patients_pattern,
        procedures_pattern=args.procedures_pattern,
        output_dir=args.output,
        patient_id=args.patient_id,
        stub_analysis=args.stub_analysis,
        log_file=args.log
    )

    if args.once:
        watcher.run_once()
    else:
        watcher.run_continuous(interval_sec=args.interval)


if __name__ == '__main__':
    main()
