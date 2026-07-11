# Spec: Login and Logout

## Overview
Implements real session-based authentication for Spendly. The `/login` route currently only
renders `login.html` (GET only, no form handling), and `/logout` is a placeholder string. This
step adds the `POST` handler for `/login` that verifies credentials against the `users` table and
starts a session, plus a working `/logout` that clears the session. This reuses the session
pattern established in Step 2 (registration) and is required before Step 4 (profile) and the
expense routes can be gated behind a login check.

## Depends on
- Step 1 — Database setup (`.claude/specs/01-database-setup.md`): requires the `users` table,
  `get_db()`, and `init_db()`.
- Step 2 — Registration (`.claude/specs/02-registration.md`): requires `get_user_by_email()`,
  `app.secret_key`, and the `session["user_id"]` convention already established for `/register`.

## Routes
- `POST /login` — validate email/password against `users`, verify password hash, start session,
  redirect to `/profile` on success, re-render `login.html` with an error on failure — public
- `GET /login` — unchanged, still renders `login.html`
- `GET /logout` — clear the session, redirect to `/` — logged-in (safe to hit while logged out too;
  it just no-ops and redirects)

## Database changes
No schema changes — the `users` table already has `password_hash`.

`database/db.py` needs one new helper function:
- `verify_user(email, password)` — looks up the user by email via `get_user_by_email()`, checks
  the password with `werkzeug.security.check_password_hash`, and returns the `sqlite3.Row` on
  success or `None` on failure (wrong email or wrong password treated identically)

## Templates
- **Create:** none
- **Modify:** `templates/login.html` — repopulate the `email` input `value=` attribute from the
  submitted form on validation failure, same pattern as `register.html`

## Files to change
- `app.py` — implement `POST` handling on `/login` (validation, credential check via
  `verify_user`, session creation, redirect) and implement `/logout` (`session.pop("user_id",
  None)`, redirect to `/`)
- `database/db.py` — add `verify_user()`
- `templates/login.html` — re-populate `email` value on error

## Files to create
- None

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (`generate_password_hash` / `check_password_hash`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate on the server even though inputs have `required`/`type="email"` — don't trust
  client-side validation alone
- Use one generic error message ("Invalid email or password.") for both "no such user" and "wrong
  password" cases — don't leak which one was wrong
- On success, store the user's id in the session (`session["user_id"] = user["id"]`) and redirect
  (`302`) to `/profile` — don't just re-render a template after a POST
- `/logout` must work even if there is no active session (no crash on `session.pop`)

## Definition of done
- [ ] Submitting the login form with a registered user's correct email/password redirects to
      `/profile` and sets a session cookie
- [ ] Submitting with a correct email but wrong password re-renders `login.html` with a generic
      error and does not set a session
- [ ] Submitting with an email that doesn't exist re-renders `login.html` with the same generic
      error and does not set a session
- [ ] Submitting with a missing/empty field re-renders `login.html` with an error and does not hit
      the database
- [ ] Visiting `/logout` while logged in clears the session and redirects to `/`
- [ ] Visiting `/logout` while logged out does not crash and redirects to `/`
- [ ] App starts without errors and existing `GET /login`, `POST /register`, `/` routes are
      unaffected
