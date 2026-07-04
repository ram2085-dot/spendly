# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

The git repository root (`expense-tracker/`, this directory) contains a single Flask project in the
`expense-tracker/` subdirectory — note the nested folder with the same name:

```
expense-tracker/            <- repo root (this file lives here)
  expense-tracker/          <- actual Flask app
    app.py
    database/
    static/
    templates/
    requirements.txt
  prompts.txt                <- log of the prompts used to build this project step by step
  venv/                       <- local virtualenv (gitignored)
```

All app commands below assume you've `cd`'d into the inner `expense-tracker/expense-tracker/` directory.

## Commands

```bash
# activate the existing virtualenv (created at repo root)
source ../../venv/Scripts/activate   # Windows/Git Bash
# or: ..\..\venv\Scripts\activate.ps1   # PowerShell

pip install -r requirements.txt

# run the dev server (binds port 5001, debug mode on)
python app.py

# run tests
pytest
```

There is no build step, linter, or frontend bundler — templates are server-rendered Jinja2, styles are a
single plain CSS file, and `static/js/main.js` is currently empty (page-specific JS lives inline in
`{% block scripts %}` in the templates that need it, e.g. `landing.html`).

## Project context

This is a **teaching project**: it's built incrementally by following prompts recorded in `prompts.txt`,
each ending in a specific `git commit -m "..."` instruction. `app.py` and `database/db.py` contain explicit
`# Placeholder ... students will implement these` / `# Students will write this file in Step N` markers —
routes like `/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete` currently
return plain placeholder strings, and `database/db.py` is an empty stub awaiting `get_db()`, `init_db()`,
and `seed_db()`. Don't "fix" these by prematurely implementing them unless that's the task at hand — they
are intentionally incomplete checkpoints in a step-by-step curriculum.

When asked to continue building the app, check `prompts.txt` first for the established pattern of what a
"step" looks like (route + template + footer/nav link update + a specific commit message), and follow that
same shape.

## Architecture

- **`app.py`** — single-file Flask app, all routes defined directly on the module-level `app` object (no
  blueprints). Real routes (`/`, `/register`, `/login`, `/terms`, `/privacy`) render templates; unimplemented
  feature routes return bare placeholder strings.
- **`templates/base.html`** — the shared layout (nav + footer + font/CSS/JS includes). Every page template
  extends it via `{% extends "base.html" %}` and fills the `title`, `head`, `content`, and `scripts` blocks.
  Nav/footer links use `url_for(...)` against the Flask endpoint names, not hardcoded paths.
- **`static/css/style.css`** — single global stylesheet for the whole site (no per-page CSS files, no
  preprocessor/bundler).
- **`database/db.py`** — intended to be the sole data-access layer (raw `sqlite3`, not an ORM): a
  `get_db()` connection helper, `init_db()` schema setup, and `seed_db()` sample data — currently unwritten.
- No authentication, session handling, or database wiring exists yet; `/login` and `/register` currently
  only render static forms.
