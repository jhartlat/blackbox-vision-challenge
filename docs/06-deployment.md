# 06 · Deployment: same data flow, another computer

**Data lens:** GitHub holds source files. Render checks out that source, installs dependencies, and starts Gunicorn. Python reads `cards.txt` at process startup. Visitors consume HTML/JSON over HTTPS and transport temporary signed progress cookies. No writable database or persistent disk is needed.

## Before deployment

1. Run `python -m pytest -q` locally.
2. Confirm `.env`, real secrets, and local environments are not committed.
3. Review `cards.txt`; malformed content prevents the app from starting.
4. Confirm your Render account/plan. This repository specifies a free plan in its optional blueprint, but availability, limits, and policies can change. Review the current dashboard before creating a service. No deployment or paid resource is created merely by publishing this repository.

## Option A: Render dashboard

1. Create a **Web Service** connected to this repository.
2. Choose Python as the runtime and the branch containing this project.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Set `SECRET_KEY` to a private, cryptographically random value. Generate it locally with `python -c "import secrets; print(secrets.token_hex(32))"`, then enter it in Render's environment settings. Never paste it into GitHub or an issue.
6. Set health check path to `/` if requested.
7. Deploy and wait for a successful build and live service status.

The `.python-version` file selects the latest available Python 3.12 patch release on Render. The application loads through `app:app`: module `app.py`, object `app`. Gunicorn, not Flask's debug server, serves production HTTP.

## Option B: Blueprint

`render.yaml` describes the same web service and requests a generated `SECRET_KEY`. Use Render's Blueprint workflow to review and apply it. Review the selected plan and any terms/costs before confirming. The blueprint is a convenience, not a second architecture.

## The actual address

Render assigns an `onrender.com` URL based on availability. **Do not assume `https://quiz-app.onrender.com` belongs to this project.** The brief uses it as an example. Only add a live link to the README after opening and verifying the exact deployed service URL.

## Verify the deployed system

- Open the service on a phone browser.
- Confirm the first question has four choices and score zero.
- Answer correctly and incorrectly, and check the one-second transition.
- Refresh midway; progress should remain.
- Complete every question; check final score and percentage.
- Inspect deployment logs for import/validation failures.
- Confirm the browser cookie is Secure/HttpOnly on HTTPS and no real secret appears in the repository.

A passed GitHub test workflow does not prove a Render deployment happened. A successful Render build does not prove a whole quiz was tested on a phone. Record each check separately.

## Maintenance and boundaries

Update cards through source control, test, then deploy. Render's configured auto-deploy behavior may rebuild after pushes. A changed deck fingerprint causes old quizzes to start over rather than mismatching indexes. A secret rotation also resets sessions. Free services may have cold-start or other resource limits; check current documentation rather than assuming instant availability.

No scores, accounts, files, or analytics are written by the app. Ordinary platform access logs may still exist; “no analytics feature” does not mean the hosting provider collects no operational data.

## Troubleshooting

| Symptom | Check |
|---|---|
| `Set SECRET_KEY before starting` | Add the environment variable, then restart |
| `Line N: ...` / fewer than four cards | Fix `cards.txt`, test, redeploy |
| Module import/dependency error | Build used `requirements.txt` in the repo root |
| Cannot bind port / unhealthy service | Gunicorn binds `0.0.0.0:$PORT` |
| Quiz unexpectedly restarts | Secret/deck changed, cookie missing, or browser reset |
| Huge custom deck loses progress | Signed-cookie size limit; return to a small deck |

Official references (checked when preparing the repository): [Render Flask guide](https://render.com/docs/deploy-flask), [Render Python versions](https://render.com/docs/python-version), [Flask production deployment](https://flask.palletsprojects.com/en/stable/deploying/), [Flask sessions](https://flask.palletsprojects.com/en/stable/quickstart/#sessions).
