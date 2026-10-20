"""Regenerate the model reference outputs used by tests/test_model_golden.py.

Run this ONLY after an intentional change to the scientific model, and commit the
updated model_reference.npz together with the model change:

    python tests/golden/make_golden.py

The reference stores every STRIDE-th sample of each plotted array for a fixed set of
cases, so any unintended change to the model's output fails the test suite.
"""
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from webapp import physics  # noqa: E402
from webapp.params import BY_ID, CALL_ORDER  # noqa: E402

PI = np.pi
STRIDE = 8
DEFAULTS = [BY_ID[k].value for k in CALL_ORDER]

CASES = {
    "defaults": DEFAULTS,
    "nutation_off": DEFAULTS[:10] + [0, 0, 2, 0],
    "face_on": [10, 0.6, 0.3, PI / 4, 0, PI / 4, 0] + DEFAULTS[7:],
    "J_parallel_N_pole": [10, 0.6, 0.3, 0, 0, 0, PI / 2] + DEFAULTS[7:],
    "small_q_large_eta_factor": [8, 0.05, 0.1] + DEFAULTS[3:],
    "max_nutation": DEFAULTS[:10] + [3, 1, 6, 3 * PI / 2],
    "B_NP_vanishes": [10, 0.6, 0.3, 0, 0, PI / 2, PI / 4] + DEFAULTS[7:],
}
FIELDS = ["f", "phi_L_GP", "cos_L_GP", "phi_L_RP", "cos_L_RP", "amp_GP", "amp_RP", "phase_GP", "phase_RP"]


def main():
    arrays, meta = {}, {"cases": {}, "stride": STRIDE}
    for name, args in CASES.items():
        r = physics.compute(*args)
        assert r.f.size, f"{name}: no samples in band"
        for field in FIELDS:
            arrays[f"{name}__{field}"] = np.asarray(getattr(r, field), float)[::STRIDE]
        meta["cases"][name] = {"args": [float(a) for a in args], "f_cut": float(r.f_cut), "n_samples": int(r.f.size)}
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "unknown"
    meta.update(generated=datetime.now(timezone.utc).isoformat(timespec="seconds"), git_commit=commit,
                platform=f"{platform.system()} {platform.machine()}", python=platform.python_version(),
                numpy=np.__version__, scipy=__import__("scipy").__version__)
    np.savez_compressed(os.path.join(HERE, "model_reference.npz"), **arrays)
    with open(os.path.join(HERE, "model_reference.json"), "w") as fh:
        json.dump(meta, fh, indent=2)
    print(f"wrote {len(CASES)} cases ({len(arrays)} arrays) at commit {commit}")


if __name__ == "__main__":
    main()
