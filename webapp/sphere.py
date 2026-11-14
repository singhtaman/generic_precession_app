"""Directions on the unit sphere in the J frame, for the time view's sphere figure.

The frame has z along J (north pole) and the x axis from which the model measures
φ_LJ. Everything is for the generically precessing (GP) model and comes from the
unmodified Generic_precession class on the app's
frequency grid (F_MIN to f_cut, step DELTA_F):

* L(f) = (sin θ_LJ cos φ_LJ, sin θ_LJ sin φ_LJ, cos θ_LJ) with θ_LJ = get_theta_LJ(f) and
  φ_LJ = get_phi_LJ(f).
* N = (0, sin ι_JN, cos ι_JN), with cos/sin ι_JN from precession_angles(). This is the
  direction implied by the model's LdotN(f) = sin θ_LJ sin ι_JN sin φ_LJ + cos θ_LJ cos ι_JN;
  ldotn_error reports max |L(f)·N − LdotN(f)| so the identity is checked on every call.
* t(f) = (1/2π) dΨ/df, the stationary-phase time of the model's orbital phase Ψ(f) (t_c = 0,
  as in time_domain). The derivative is taken numerically on the grid (np.gradient). It
  links a time on the strain plot to a frequency, and so to θ_LJ and φ_LJ.

With nutation θ_LJ oscillates and can be negative (Δθ̃ > θ̃) or exceed π/2, so the page uses the
polar angle of L, arccos(cos θ_LJ), for the bands. The orbital plane is perpendicular to L: at
polar angle α its great circle reaches latitudes ±min(α, π − α) about the equator.
"""
from dataclasses import dataclass

import numpy as np

from generic_precession_no_match import Generic_precession

from .physics import DELTA_F, F_MIN, MODEL_ERRSTATE, build_params


@dataclass
class Sphere:
    f: np.ndarray          # [Hz]
    t: np.ndarray          # stationary-phase time t(f) [s], t_c = 0
    theta_LJ: np.ndarray   # [rad]
    phi_LJ: np.ndarray     # [rad], not wrapped
    N: tuple               # (x, y, z) in the J frame
    ldotn_error: float     # max |L·N − LdotN| over the grid
    t_monotonic: bool      # t(f) strictly increasing, needed to invert it


def directions(*values) -> Sphere:
    """values in CALL_ORDER (the arguments of physics.compute)."""
    with np.errstate(**MODEL_ERRSTATE):
        params_GP = build_params(*values)[2]
        GP = Generic_precession(params_GP)
        f = np.arange(F_MIN, GP.get_f_cut(), DELTA_F)
        if f.size == 0:
            empty = np.empty(0)
            return Sphere(empty, empty, empty, empty, (0.0, 0.0, 1.0), 0.0, True)

        theta = GP.get_theta_LJ(f)
        phi = GP.get_phi_LJ(f)
        cos_i, sin_i = GP.precession_angles()[:2]
        N = (0.0, float(sin_i), float(cos_i))

        L = np.stack([np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)])
        err = float(np.max(np.abs(N[1] * L[1] + N[2] * L[2] - GP.LdotN(f))))

        t = np.gradient(GP.Psi(f), f) / (2 * np.pi) if f.size > 1 else np.zeros(1)

    return Sphere(f, t, theta, phi, N, err, bool(np.all(np.diff(t) > 0)))
