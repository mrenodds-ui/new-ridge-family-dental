# Server-Side Authentication Setup for New Ridge Staff Portal

## Overview

This directory now includes **real server-side authentication** for the `forms/` folder. The previous client-side password gate was cosmetic only — anyone could directly download files by guessing URLs. The new setup protects file downloads at the HTTP server level.

**How it works:**
- Staff can browse the staff page and see the document list without logging in
- Downloading any file from `/forms/*` requires HTTP Basic Authentication
- Once authenticated, the browser remembers credentials for the session

---

## Option A: Python Secure Server (Recommended)

Use `secure_server.py` to replace whatever static file server is currently serving the staff page.

### 1. Copy to deployment directory

```powershell
# From this workspace directory
copy secure_server.py C:\new-ridge-staff-page\dental-office-manager\app\dist\
cd C:\new-ridge-staff-page\dental-office-manager\app\dist
```

### 2. Start the server

```powershell
python secure_server.py --port 7119 --root . --password ridge2026
```

Or to change the password:

```powershell
python secure_server.py --port 7119 --root . --password YourNewPassword
```

### 3. Update your startup script

In `new_ridge_startup.py`, replace the staff server launch with:

```python
proc_staff = subprocess.Popen(
    [sys.executable, "secure_server.py", "--port", str(STAFF_PORT), "--root", STAFF_DIR, "--password", "ridge2026"],
    cwd=STAFF_DIR,
    creationflags=subprocess.CREATE_NO_WINDOW,
)
```

### 4. What the server does

- Serves the Vite SPA normally (no auth needed to browse)
- Any request to `/forms/*` returns `401 Unauthorized` unless valid Basic Auth credentials are provided
- The browser will show a native login dialog when staff click a download link
- Supports SPA fallback: unknown routes serve `index.html` (for React Router)

---

## Option B: Apache

If you switch to Apache, copy these two files into the `forms/` directory of your deployment:

```
forms/
  .htaccess       ← copy from workspace/forms/.htaccess
  .htpasswd       ← copy from workspace/forms/.htpasswd
```

**Important:** Edit `.htaccess` to use the correct absolute path to `.htpasswd`:

```apache
AuthUserFile "C:/new-ridge-staff-page/dental-office-manager/app/dist/forms/.htpasswd"
```

**Requirements:**
- `AllowOverride AuthConfig` must be enabled in Apache's main config for the directory
- `mod_auth_basic` and `mod_authn_file` must be loaded

---

## Option C: Nginx

Add this location block to your Nginx server config:

```nginx
server {
    listen 7119;
    root C:/new-ridge-staff-page/dental-office-manager/app/dist;
    index index.html;

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Protect forms with Basic Auth
    location /forms/ {
        auth_basic "New Ridge Staff Portal";
        auth_basic_user_file C:/new-ridge-staff-page/dental-office-manager/app/dist/forms/.htpasswd;
    }
}
```

Generate the `.htpasswd` file with:

```powershell
# If you have Apache's htpasswd tool:
htpasswd -cb .htpasswd staff ridge2026

# Or use the included Python script:
python generate_htpasswd.py ridge2026 > .htpasswd
```

---

## Changing the Password

1. **Python server:** Pass `--password NewPassword` when starting
2. **Apache/Nginx:** Re-run the generator:
   ```powershell
   python generate_htpasswd.py NewPassword > forms/.htpasswd
   ```

---

## What Changed in staff.html

- **Removed:** The fake client-side password gate (hardcoded JavaScript password)
- **Removed:** Hardcoded `ridge2026` from the HTML source
- **Kept:** The HIPAA warning banner and "Internal" badges for UX clarity
- **Result:** Staff click a form → browser shows native auth dialog → file downloads

---

## Files in this package

| File | Purpose |
|------|---------|
| `secure_server.py` | Python static server with Basic Auth for `/forms/*` |
| `generate_htpasswd.py` | Generates Apache-compatible `$apr1$` password hashes |
| `forms/.htaccess` | Apache directory-level auth config |
| `forms/.htpasswd` | Apache password file (staff / ridge2026) |
| `AUTH_SETUP.md` | This document |

---

*Last updated: July 25, 2026*
