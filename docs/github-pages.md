# Generic Precession explorer: browser version on GitHub Pages

Branch `feature/github-pages` (from `feature/vercel-ui`) adds a static browser version of the
explorer in `pages/`, ported from the Regular Precession app's browser build
(`regular_precession_webapp`, branch `feature/github-pages`). Nothing existing was changed:
the model, `webapp/params.py`, `webapp/physics.py`, the Dash app, `vercel.json` and the tests are
untouched; `.gitignore` gained `_site/`.

**Hosting: GitHub Pages** at https://singhtaman.github.io/generic_precession_app/ (decided
14 Nov 2026, when the repository was made public). `.github/workflows/pages.yml` (copied from the
Regular Precession repo) runs `pages/build.sh` and deploys `_site/` on every push to
`feature/github-pages`. The Vercel app is unaffected: it deploys from `feature/vercel-ui`. The
browser build sends `generic_precession_no_match.py` to every visitor (Pyodide runs it in the
browser).

## How it works

- `pages/worker.js` starts Pyodide 0.29.0 in a Web Worker, copies in
  `generic_precession_no_match.py`, `systems_lib.py`, `webapp/params.py` and `webapp/physics.py`
  unchanged (plus the browser-only `webapp/time_domain.py` and `webapp/sphere.py`), and calls them
  through `pages/gp_page.py`.
- `pages/app.js` builds the controls from `webapp/params.py` and mirrors `webapp/callbacks.py`
  (validation, notices, system properties, presets, resets, CSV export in the same format).
- `pages/figures.js` is a JavaScript port of `webapp/figures.py` (GP blue, RP amber dashed);
  keep the two in step when changing a plot.
- `pages/build.sh` assembles `_site/`. Preview: `pages/build.sh && python3 -m http.server -d _site 8000`.

## Time view (browser version only)

A Frequency / Time switch. In the time view the amplitude and phase panels are replaced by:

- **Strain:** h(t) for GP, RP and NP, the inverse FFT of the unmodified
  `Generic_precession.precessing_strain(f)` on the app's grid, Tukey taper α = 0.1, t_c = 0
  (`webapp/time_domain.py`, same method as the RP app). RP is drawn solid here because dashes break
  up on a fast oscillation. Export columns: t_s, h_GP, h_RP, h_NP.
- **Sphere** (GP signal only, shown in both views): unit sphere with J at the north pole (`webapp/sphere.py`).
  L = (sin θ_LJ cos φ_LJ, sin θ_LJ sin φ_LJ, cos θ_LJ) from `get_theta_LJ` / `get_phi_LJ`, which
  include nutation. θ_LJ can be negative (Δθ̃ > θ̃) or exceed π/2 (it reaches 6.5 rad at q = 0.05),
  so the bands use the polar angle α = arccos(cos θ_LJ): blue = [min α, max α]; orange = latitudes
  within ±max min(α, π − α) of the equator, swept by the orbital plane. N̂ = (0, sin ι_JN, cos ι_JN),
  checked against the model's `LdotN` on every call. Time ↔ frequency by t(f) = (1/2π) dΨ/df.
- **Playback:** Play/pause, speed (default ¼×), time slider; L leaves a trail, the strain is traced
  behind a cursor and scrolls when zoomed in.
- **Layout:** frequency view: modulation of L and sphere, then amplitude and phase, then system
  properties. Time view: a 2 × 2 grid of modulation of L | system properties over sphere | strain.
  In the frequency view, hovering the amplitude or phase plot at f places L at t(f), and playback
  traces a cursor and fade across both plots.

## Checks (14 Nov 2026)

- **Agreement with the live Vercel app** (https://genericprecession.vercel.app), CSV export of
  26 inputs (defaults, face-on, maximum nutation, ω̃ = 0, no nutation, a no-signal case, 20 seeded
  random): headers identical; f, φ_L, cos θ_L and amplitudes within 1.2×10⁻¹¹ relative; phases
  within 4.9×10⁻⁶ rad (maximum nutation; `odeint` in SciPy 1.14.1 vs 1.18.1), ~10⁻¹² typically;
  no-signal inputs agree.
- **Model checks** in CPython (NumPy 1.26, SciPy 1.13): L·N − LdotN ≤ 2.2×10⁻¹⁶ and t(f) strictly
  increasing over 45 non-empty parameter sets (defaults, extremes, 40 random); the strain's
  zero-crossing frequency at t(f) is 24.95/40.18/81.76 Hz for f = 25/40/80 Hz.
- **Browser** (headless Chromium and WebKit): frequency view, time view, sphere, hover linking (marker
  within 4×10⁻⁶ of the model's L less than 0.5 ms from the hovered sample), out-of-band times hide the
  marker, overlap key, both CSV exports, no-signal state, playback (play, pause, scrub, click to pause,
  end, slider change during playback, view switch), 390 px phone width without horizontal scroll, no
  console errors.
- **Not checked:** real phones/tablets; the repository's pytest suite (needs Python 3.12; no file it
  tests was changed).

## Vercel (browser version, separate project)

On this branch `vercel.json` describes the static browser build (no framework, no install,
`sh pages/build.sh`, output `_site/`), so a separate Vercel project with production branch
`feature/github-pages` serves the same site as GitHub Pages. The Dash app's Vercel project is
unaffected: it deploys `feature/vercel-ui`, which keeps its own Flask `vercel.json`. Note that the
Dash project also builds preview deployments of this branch, which now show the browser build.
