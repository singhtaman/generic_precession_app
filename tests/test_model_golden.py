"""The model's output must match the committed reference (tests/golden/model_reference.npz).

test_physics_regression.py compares the new app with the original app, but both import
the same model module, so it cannot notice a change to the model itself. This test can:
any unintended change to generic_precession_no_match.py fails here.

After an intentional model change, regenerate and commit the reference:
    python tests/golden/make_golden.py

Tolerances allow for platform differences (e.g. CI on Linux x86-64 vs a Mac): closed-form
quantities agree to ~1e-14; the ODE-integrated phase to ~1e-6 of its range.
"""
import json
import os

import numpy as np
import pytest

from webapp import physics

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden")
REF = np.load(os.path.join(HERE, "model_reference.npz"))
META = json.load(open(os.path.join(HERE, "model_reference.json")))
STRIDE = META["stride"]

CLOSED_FORM_TOL = 1e-9   # relative to the array's largest magnitude (at least 1)
INTEGRATED_TOL = 1e-5    # phase: odeint's adaptive steps differ slightly across platforms


@pytest.mark.parametrize("name", sorted(META["cases"]))
def test_model_matches_reference(name):
    case = META["cases"][name]
    r = physics.compute(*case["args"])
    assert r.f.size == case["n_samples"], "frequency grid changed"
    assert r.f_cut == pytest.approx(case["f_cut"], rel=1e-12)
    for field in ["f", "phi_L_GP", "cos_L_GP", "phi_L_RP", "cos_L_RP", "amp_GP", "amp_RP", "phase_GP", "phase_RP"]:
        expected = REF[f"{name}__{field}"]
        actual = np.asarray(getattr(r, field), float)[::STRIDE]
        tol = INTEGRATED_TOL if field.startswith("phase") else CLOSED_FORM_TOL
        scale = max(1.0, float(np.max(np.abs(expected))))
        np.testing.assert_allclose(actual, expected, rtol=0, atol=tol * scale,
                                   err_msg=f"{name}: {field} differs from the committed reference. If the model "
                                           "change is intentional, run: python tests/golden/make_golden.py")
