# Spec: Registration

## Overview
Implements real account creation for Spendly. The `/register` route currently only renders
`register.html`; this step adds the `POST` handler that validates the submitted form, creates a
row in the `users` table (with a hashed password), starts a logged-in session, and redirects the
new user into the app. This is the first authentication feature built on top of the Step 1
database layer, and establishes the session pattern that login/logout (Step 3) will reuse.

## Depends on
- Step 1 — Database setup (`.claude/specs/01-database-setup.md`): requires the `users` table,
  `get_db()`, and `init_db()` to already exist and work.

## Routes
- `POST /register` — validate name/email/password, reject duplicate email, insert user with
  hashed password, start session, redirect to `/profile` — public
- `GET /register` — unchanged, still renders `register.html`

## Database changes
No schema changes — the `users` table from Step 1 already has the required columns
(`name`, `email`, `password_hash`).

`database/db.py` needs two new helper functions (no new tables):
- `get_user_by_email(email)` — parameterized `SELECT` returning a `sqlite3.Row` or `None`, used
  to check for duplicate emails before insert
- `create_user(name, email, password)` — hashes the password with
  `werkzeug.security.generate_password_hash` and inserts a row into `users`, returning the new
  `user_id`

## Templates
- **Create:** none
- **Modify:** `templates/register.html` — repopulate `name`/`email` input `value=` attributes
  from the submitted form on validation failure, so the user doesn't retype everything after an
  error

## Files to change
- `app.py` — add `session` import, set `app.secret_key`, implement `POST` handling on
  `/register` (validation, duplicate-email check, session creation, redirect)
- `database/db.py` — add `get_user_by_email()` and `create_user()`
- `templates/register.html` — re-populate form values on error

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
- Validate on the server even though inputs have `required`/`type="email"` — don't trust client-side validation alone
- Reject registration if the email already exists (`get_user_by_email`) and re-render
  `register.html` with an error, not a generic 500
- Set `app.secret_key` (e.g. from `os.environ.get("SECRET_KEY", "dev")`) so `session` works —
  there's no session/secret-key handling anywhere yet
- On success, store the new user's id in the session (e.g. `session["user_id"] = user_id`) and
  redirect (`302`) to `/profile` — don't just re-render a template after a POST

## Definition of done
- [ ] Submitting the register form with a new name/email/password creates a row in `users` with a
      hashed (not plaintext) password
- [ ] Submitting with an email that already exists re-renders `register.html` with an error and
      does not create a duplicate row
- [ ] Submitting with a missing/empty field re-renders `register.html` with an error and does not
      hit the database
- [ ] After a successful registration, the response is a redirect to `/profile` and a session
      cookie is set
- [ ] Refreshing `/profile` after registering keeps the user "logged in" (session persists)
- [ ] App starts without errors and existing `GET /register`, `/login`, `/` routes are unaffected
