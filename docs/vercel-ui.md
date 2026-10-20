# Generic Precession explorer: redesigned UI on Vercel

This branch (`feature/vercel-ui`) adds a redesigned version of the interactive
generic-precession app and the configuration to host it on Vercel's free Hobby
plan. It only **adds** files: the Render app (`scripts/GP_map_all_app.py`), the
`Procfile`, `scripts/requirements.txt` and every scientific module are
byte-identical to `main`, so Render and Vercel can run side by side.

| | Render (original) | Vercel (this branch) |
|---|---|---|
| Code | `scripts/GP_map_all_app.py` | `app.py` → `webapp/` |
| Branch | `main` | `feature/vercel-ui` |
| Dependencies | `scripts/requirements.txt` (unpinned) | `requirements.txt` (pinned) |
| Server | gunicorn, long-running | Vercel Function (Python 3.12, Fluid compute) |
| URL | your Render service | https://generic-precession-ui.vercel.app |

## 1. What changed

**Interface** (`webapp/layout.py`, `webapp/assets/style.css`)

- Parameters grouped into Precession, Nutation, Source and Orientation, each with
  symbol, unit and a one-line explanation; collapsible groups, per-group reset,
  "Reset all", and edge-on / face-on presets (systems 2 and 1 in `systems_lib.py`).
- Non-angle sliders have a number box (type a value, press Enter); angle sliders
  show their value as a fraction of π.
- Results in a 2×2 grid: modulation of L | system properties, amplitude | phase.
  Stacks to one column on narrow screens.
- Status line (samples, band, compute time), CSV export of every plotted array at
  full precision, high-resolution PNG export from each plot's toolbar.
- Explicit messages for: invalid input, no frequencies in band (f_cut < 20 Hz),
  a model evaluation error, a divergent amplitude ratio (B_NP ≈ 0),
  and results where GP/RP coincide with the non-precessing signal.

**Display rules** (`webapp/figures.py`): presentation only, computed values are
never altered.

- Each plot opens on the original app's axis window and widens only when data
  would otherwise be off-screen (the original fixed windows hid data for most
  orientations and for f_cut > 150 Hz).
- The amplitude axis is capped at ±20 when B_GP/B_NP − 1 diverges, with a label.
- φ_L wraps at ±π are drawn as gaps; the J marker uses the same (−π, π] convention.
- A stationary L is drawn as a point; the zero line is drawn under the curves.
- Colours: GP blue (solid), RP amber (dashed), J red.

**Defaults**: as in the original app except nutation, which now opens switched on
(Δθ̃ = 1.2, ΔΩ̃ = 0.2, ω̃ = 1.3, matching `scripts/interactive_GP_app.py`).

**Calculation layer** (`webapp/physics.py`): reproduces the original parameter
assembly line for line and calls the unmodified `Generic_precession` class. Two
differences, neither of which changes any value:

1. Each model (GP, RP, NP) is built once per request instead of once per panel.
2. Evaluation runs under the model's own NumPy error state. The model modules call
   `np.seterr(invalid="raise")` at import, but NumPy error state is per-thread and
   web servers handle requests in worker threads, where invalid operations would
   otherwise silently produce NaN (blank plots) instead of raising.

## 2. Run locally

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python app.py                      # http://127.0.0.1:8050  (PORT, HOST, DASH_DEBUG=1 optional)
gunicorn app:app --threads 4       # production-style WSGI server
```

The original app still runs as before, e.g. `cd scripts && gunicorn GP_map_all_app:server`
with `scripts/requirements.txt`.

## 3. Test

```bash
pytest                                              # ~890 tests, ~1 minute
pip install playwright && playwright install chromium
pytest -m ui                                        # optional browser tests
```

| File | What it checks |
|---|---|
| `test_physics_regression.py` | Every plotted array equals `scripts/GP_map_all_app.py` bit-for-bit (named cases, slider extremes, seeded random sample, special-angle grid); identical exceptions wherever the model raises; J ∥ N (θ_S = θ_J = 0) evaluates; derived readouts; error state in worker threads |
| `test_params.py` | Slider ids, ranges, steps and marks equal the original layout; the three changed defaults are listed explicitly |
| `test_figures.py` | Original windows by default, data never outside the axes, wraps, J marker, stationary L, zero line, off-scale label |
| `test_app.py` | Every endpoint and callback state, reset and presets, export (equals the computation; disabled without data), Vercel payload limit |
| `test_ui.py` | Real browser: 2×2 layout, plots never hidden after error/empty states, Enter commits, presets |

The regression tests import the original app, so they need `matplotlib`
(included in `requirements-dev.txt`).

## 4. Deploy to Vercel

### Option A: Vercel CLI from this machine (how the current deployment was made)

No push to GitHub is needed. Deploy exactly what is committed:

```bash
vercel login                                         # once, as the GitHub user singhtaman
rm -rf /tmp/gp-deploy && mkdir /tmp/gp-deploy
git archive feature/vercel-ui | tar -x -C /tmp/gp-deploy
cd /tmp/gp-deploy
vercel link --yes --project generic-precession-ui
rm -f .env.local                                     # vercel link writes a short-lived token here; not needed
vercel deploy                                        # preview (protected by Vercel Authentication)
vercel deploy --prod                                 # public production URL
```

### Option B: Git integration (deploy on every push)

1. Push the branch: `git push -u origin feature/vercel-ui`.
2. Vercel dashboard → project `generic-precession-ui` → Settings → Git → connect
   `singhtaman/generic_precession_app`.
3. Settings → Git → **Production Branch**: `feature/vercel-ui`.
4. Settings → Git → **Ignored Build Step** → custom command, so pushes to `main`
   (which has no Vercel entry point) don't create failing builds:

   ```bash
   if [ "$VERCEL_GIT_COMMIT_REF" = "feature/vercel-ui" ]; then exit 1; else exit 0; fi
   ```

Render deploys only the branch set in its service settings (`main`), so pushes to
`feature/vercel-ui` don't affect it. Check Render → your service → Settings →
Branch if unsure.

## 5. Vercel settings

`vercel.json` (committed) sets the Flask framework preset and keeps `scripts/`,
the pycbc-dependent modules, tests and docs out of the function bundle.
Without `"framework": "flask"` a project created as "Other" only looks for
`api/` functions and the build fails.

Environment variables (project settings, not in git; values are not secret):

| Name | Value | Environments | Why |
|---|---|---|---|
| `VERCEL_SUPPORT_LARGE_FUNCTIONS` | `1` | Production, Preview, Development | Allows a bundle above the 250 MB standard function size (Large Functions, beta) |
| `VERCEL_PYTHON_DISABLE_RUNTIME_INSTALL` | `1` | Preview (recommended for Production too) | Bundles all dependencies instead of installing dash/plotly/astropy at cold start |

The second variable is read by Vercel's Python builder (`@vercel/python`) but is not
in Vercel's public docs. Measured on fresh deployments of this app:

| Bundling | First request after idle | Warm request |
|---|---|---|
| Default (runtime install) | 6.9 s, of which 3.0 s installs packages | 0.17 s |
| `VERCEL_PYTHON_DISABLE_RUNTIME_INSTALL=1` | 3.2 s | 0.14 s |

If Vercel removes the variable, builds fall back to the default behaviour.

Python version: Vercel's default, 3.12 (tested). No `.python-version` file is
added because Render also reads that file.

## 6. What has been verified

Verified:

- Local: full test suite (896 incl. browser tests); `gunicorn app:app` with threads.
- `vercel build` with Vercel CLI 64.7.0.
- Live deployment (2026-10-20, region iad1): build on Vercel's Linux builders,
  page/assets/callbacks over Vercel routing, 1,272-request parameter sweep (every
  response either plots or explains why not), browser visibility test at three
  widths, CDN caching of assets.
- Live vs local numerics (Linux x86-64 vs macOS arm64, 38 cases): amplitude,
  modulation and frequency grid agree to ~4×10⁻¹⁵ relative; phase to ~1.6×10⁻⁷
  relative. The phase difference comes from `odeint`'s adaptive integration of δφ
  on a different CPU/math library and is within its default tolerance. Same-platform
  comparisons are bit-identical.

Not verified:

- Behaviour under sustained traffic or many concurrent users.
- Long-term monthly usage against the Hobby quotas (estimate below).

## 7. Hobby plan limits that matter here

| Limit | Hobby | This app |
|---|---|---|
| Function duration | 300 s | 10–50 ms per update |
| Memory | 2 GB | ~200 MB |
| Response size | 4.5 MB | ≤ 1.1 MB (widest band, 6,891 samples) |
| Bundle | 500 MB Python; larger with Large Functions | ~296 MB |
| Active CPU | 4 CPU-hours / month | ~0.05 s per update, plus ~3 s per cold start |
| Invocations | 1,000,000 / month | one per slider release, plus page assets (assets are CDN-cached) |
| Runtime logs | 1 hour retention | |

Hobby is for non-commercial, personal use. When a quota is exceeded the feature
pauses until the 30-day window resets; there is no surprise bill.

## 8. Differences from the Render app

- New layout, controls, notices and export (above).
- Axes widen to show data the original fixed windows cut off.
- Model version: `feature/vercel-ui` includes the updated `generic_precession_no_match.py`
  (nutation terms in `integrand_delta_phi`; near-face-on handling in `precession_angles`
  and `beam_pattern_amplitude_and_phase`, so θ_S = θ_J = 0 now evaluates). Render serves
  `main`, which keeps the previous model until that change is merged there; until then
  the two sites show different phase curves when nutation is on.
- Model errors: Render's plot silently stops updating; this app shows the error.
- Nutation defaults differ (section 1).
- Dependencies pinned (Render installs the latest versions on each build).
- Cold starts on Vercel (section 5); Render keeps a process running (or spins it
  down on its own free tier).

## 9. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Build: "The pattern "app.py" defined in `functions` doesn't match any Serverless Functions inside the `api` directory" | Framework preset is "Other". Keep `"framework": "flask"` in `vercel.json` (or set Flask in project settings). |
| Build log: "Bundle size … exceeds the standard size; optimizing dependencies" | Packages will install at cold start (slower first load). Set `VERCEL_PYTHON_DISABLE_RUNTIME_INSTALL=1` and `VERCEL_SUPPORT_LARGE_FUNCTIONS=1`, then redeploy. |
| Preview URL asks for a Vercel login | Previews use Vercel Authentication by default. Use the production URL, `vercel curl <url>`, or turn off Deployment Protection. |
| First page load takes several seconds | Cold start after idle (section 5). |
| All three plots show "No plot for these parameters" | The model raised an error; the message above the plots names it. |
| Amplitude panel shows "Off scale" | B_NP ≈ 0 for this orientation (e.g. edge-on, + polarization not seen by the detector); the ratio diverges. Use the toolbar's autoscale to see the full range. |
| `vercel logs` returns nothing or "outside the available retention" | Hobby keeps runtime logs for one hour; omit `--since`. |
| Regression tests skipped | Install `requirements-dev.txt` (matplotlib is needed to import the original app). |

## 10. Returning to the original app

Nothing on Render changed. The original app is `scripts/GP_map_all_app.py` on
`main`; `git checkout main` restores the repository exactly as before this branch.
To stop the Vercel deployment, delete the `generic-precession-ui` project in the
Vercel dashboard (or `vercel project rm generic-precession-ui`).
