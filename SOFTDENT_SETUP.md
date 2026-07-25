# SoftDent Integration Setup — New Ridge Family Dental

This guide walks you through connecting your **SoftDent** practice management system to the radiograph viewer.

---

## What You Need

- **SoftDent** installed on your practice computer
- **Python 3.8+** installed (get it from [python.org](https://python.org))
- The files in this folder:
  - `softdent-converter.py` — converts SoftDent CSV exports to JSON
  - `softdent-watch.py` — watches your export folder and auto-converts
  - `softdent-autorun.bat` — Windows batch script for Task Scheduler
  - `js/pms-config.js` — viewer configuration

---

## Step 1 — Export from SoftDent

### Export Patient List

1. Open **SoftDent**
2. Go to **Reports → Patient List** (or **Patient Information**)
3. Set your filter (e.g., all active patients, or today's patients)
4. Click **Export** and choose **Delimited Text (.CSV)**
5. Save to: `C:\softdent\exports\patients_2026-07-25.csv`

### Export Procedure History

1. Go to **Reports → Treatment/Procedure History**
2. Filter by date range (e.g., last 30 days)
3. Click **Export** → **Delimited Text (.CSV)**
4. Save to: `C:\softdent\exports\procedures_2026-07-25.csv`

> **Tip:** Create the folder `C:\softdent\exports\` first. Use the same folder every time so the watcher finds the files.

---

## Step 2 — Configure Paths

Open `softdent-autorun.bat` in Notepad and edit these lines:

```batch
set "EXPORT_DIR=C:\softdent\exports"
set "PROJECT_DIR=%~dp0"
set "PYTHON=python"
```

- `EXPORT_DIR` = Where SoftDent saves its CSV files
- `PROJECT_DIR` = This folder (auto-detected, usually correct)
- `PYTHON` = Path to Python if not in your system PATH

---

## Step 3 — Test Manual Run

Double-click `softdent-autorun.bat`.

You should see:
```
Found patient file: C:\softdent\exports\patients_2026-07-25.csv
Found procedure file: C:\softdent\exports\procedures_2026-07-25.csv
Running converter...
Done! 47 patients converted.
       47 patient radiograph lists created.
```

Check that `data/patients/` and `data/radiographs/` now contain `.json` files.

---

## Step 4 — Set Viewer to SoftDent Mode

Open `js/pms-config.js` and change:

```js
mode: 'softdent'
```

Save the file.

---

## Step 5 — Schedule Automatic Runs (Windows Task Scheduler)

### Option A: Run on a Schedule (e.g., every night at 6 PM)

1. Press **Win + R**, type `taskschd.msc`, press Enter
2. In the right panel, click **Create Basic Task…**
3. **Name:** `SoftDent Radiograph Export`
4. **Trigger:** Choose **Daily** → set time to **6:00:00 PM**
5. **Action:** Choose **Start a program**
6. **Program/script:** Browse to `softdent-autorun.bat` in this folder
7. **Finish**

### Option B: Real-Time Watcher (runs continuously)

Instead of the batch script, use the Python watcher:

```bash
cd "C:\path\to\new-ridge-family-dental"
python softdent-watch.py --watch "C:\softdent\exports" --output ./data
```

This runs forever, checking every 30 seconds for new export files.

To run it in the background, create a scheduled task that starts at login:

1. **Task Scheduler → Create Basic Task**
2. **Name:** `SoftDent Watcher`
3. **Trigger:** **When I log on**
4. **Action:** **Start a program**
5. **Program:** `python`
6. **Add arguments:** `softdent-watch.py --watch "C:\softdent\exports" --output ./data`
7. **Start in:** `C:\path\to\new-ridge-family-dental`
8. **Finish**

---

## Step 6 — Auto-Push to GitHub (Optional)

If you want the live website to update automatically when SoftDent exports run:

1. Uncomment these lines in `softdent-autorun.bat`:

```batch
git add data/
git commit -m "Auto-update: SoftDent export %date% %time%"
git push origin HEAD
```

2. Make sure **Git** is installed and your GitHub credentials are cached:
   ```bash
   git config --global credential.helper manager
   ```

3. Run the batch script once manually so it prompts for credentials — Windows will remember them.

Now every scheduled export run will also update your live website.

---

## File Reference

| File | Purpose |
|---|---|
| `softdent-converter.py` | One-time conversion from CSV → JSON |
| `softdent-watch.py` | Continuous file watcher + auto-converter |
| `softdent-autorun.bat` | Windows batch script for Task Scheduler |
| `js/pms-config.js` | Viewer mode selector (`mock` / `softdent` / etc.) |
| `js/pms-adapter.js` | Data engine that loads JSON into the viewer |
| `data/patients/*.json` | Converted patient records |
| `data/radiographs/*.json` | Converted radiograph lists & analysis |

---

## Troubleshooting

**"No patient file found"**
→ Check that `EXPORT_DIR` in `softdent-autorun.bat` matches your actual export folder.

**"Converter failed"**
→ Make sure Python is installed. Run `python --version` in Command Prompt.

**Viewer still shows mock data**
→ Make sure `js/pms-config.js` has `mode: 'softdent'` and you refreshed the browser.

**Git push fails**
→ Make sure you're in the git repo folder and credentials are saved. Run `git push` manually once.

---

## One-Line Summary

> Export from SoftDent → save to `C:\softdent\exports\` → run `softdent-autorun.bat` → viewer loads live data.
