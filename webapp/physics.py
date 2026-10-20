"""Evaluation layer between the UI and the scientific model.

Every quantity here reproduces scripts/GP_map_all_app.py exactly:

* parameter assembly          -> plot_cos_L_phi_L / plot_amplitude / plot_phase
* modulation, amplitude, phase -> the traces of plot_combined
* derived quantities          -> update_total_mass / update_cos_i_JN

The only structural difference is that each waveform model (GP, RP, NP) is
built once per request instead of once per panel. The model classes in
generic_precession_no_match.py are used unmodified.
"""
from dataclasses import dataclass

import numpy as np
from astropy.cosmology import FlatLambdaCDM

from generic_precession_no_match import Generic_precession
from systems_lib import default_precession_params_sys2_NP, giga_parsec, solar_mass

# The model modules call np.seterr(invalid="raise") at import. NumPy error state is
# per-thread, and web servers run requests in worker threads where that call never ran,
# so invalid operations would silently give NaN instead of raising. compute() restores
# the model's error state explicitly for every evaluation.
MODEL_ERRSTATE = np.geterr()

F_MIN = 20          # Hz, as in the original app
DELTA_F = 0.05      # Hz, as in the original app

_COSMO = FlatLambdaCDM(H0=67.4, Om0=0.315)  # Planck 2018 results


def redshift_to_luminosity_distance(z) -> float:
    """Luminosity distance in Gpc for redshift z (flat ΛCDM, Planck 2018)."""
    return _COSMO.luminosity_distance(z).to('Gpc').value


def redshifted_new_params(z, rp_params) -> dict:
    """Set the distance for z and redshift the chirp mass (mutates and returns rp_params)."""
    rp_params["dist"] = redshift_to_luminosity_distance(z) * giga_parsec
    old_chirp = rp_params["mcz"]
    rp_params["mcz"] = old_chirp * (1 + z)
    return rp_params


def build_params(chirp_mass, mass_ratio, redshift, theta_S, phi_S, theta_J, phi_J,
                 theta_tilde, Omega_tilde, gamma_P,
                 delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N):
    """Return (params_NP, params_RP, params_GP) exactly as the original app assembles them."""
    params_NP = default_precession_params_sys2_NP.copy()
    params_NP['theta_S'] = theta_S
    params_NP['phi_S'] = phi_S
    params_NP['theta_J'] = theta_J
    params_NP['phi_J'] = phi_J
    params_NP['mcz'] = chirp_mass * solar_mass
    params_NP['eta'] = mass_ratio / ((1 + mass_ratio) ** 2)
    params_NP['dist'] = redshift_to_luminosity_distance(redshift) * giga_parsec

    params_NP = redshifted_new_params(redshift, params_NP)

    params_RP = params_NP.copy()
    params_RP['theta_tilde'] = theta_tilde
    params_RP['Omega_tilde'] = Omega_tilde
    params_RP['gamma_P'] = gamma_P

    params_GP = params_RP.copy()
    params_GP['delta_theta_tilde'] = delta_theta_tilde
    params_GP['delta_Omega_tilde'] = delta_Omega_tilde
    if omega_n_tilde == 0:
        omega_n_tilde = 0.001
    params_GP['omega_n_tilde'] = omega_n_tilde
    params_GP['gamma_N'] = gamma_N

    return params_NP, params_RP, params_GP


@dataclass
class Derived:
    total_mass: float           # source frame [M_sun]
    total_mass_redshifted: float
    f_cut: float                # [Hz]
    cos_i_JN: float
    luminosity_distance: float  # [Gpc]


def derived_quantities(chirp_mass, mass_ratio, redshift, theta_S, phi_S, theta_J, phi_J):
    """Readouts shown under the original app's sliders, plus d_L used by the model."""
    total_mass = chirp_mass / ((mass_ratio / (1 + mass_ratio) ** 2) ** (3 / 5))
    total_mass_redshifted = total_mass * (1 + redshift)
    f_cut = 1 / (6 ** (3 / 2) * np.pi * total_mass_redshifted * solar_mass)
    cos_i_JN = (np.sin(theta_J) * np.sin(theta_S) * np.cos(phi_J - phi_S)) + (np.cos(theta_J) * np.cos(theta_S))
    return Derived(total_mass, total_mass_redshifted, f_cut, cos_i_JN,
                   redshift_to_luminosity_distance(redshift))


@dataclass
class Result:
    f: np.ndarray               # frequency grid [Hz]
    phi_L_GP: np.ndarray
    cos_L_GP: np.ndarray
    phi_L_RP: np.ndarray
    cos_L_RP: np.ndarray
    amp_GP: np.ndarray          # B_GP/B_NP - 1
    amp_RP: np.ndarray          # B_RP/B_NP - 1
    phase_GP: np.ndarray        # Φ_GP - Φ_NP, plotted with the original sign convention
    phase_RP: np.ndarray
    f_cut: float                # from the GP model, sets the frequency grid
    J: tuple                    # (phi_J, cos theta_J) marker position


def compute(chirp_mass, mass_ratio, redshift, theta_S, phi_S, theta_J, phi_J,
            theta_tilde, Omega_tilde, gamma_P,
            delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N) -> Result:
    with np.errstate(**MODEL_ERRSTATE):
        return _compute(chirp_mass, mass_ratio, redshift, theta_S, phi_S, theta_J, phi_J,
                        theta_tilde, Omega_tilde, gamma_P,
                        delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N)


def _compute(chirp_mass, mass_ratio, redshift, theta_S, phi_S, theta_J, phi_J,
             theta_tilde, Omega_tilde, gamma_P,
             delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N) -> Result:
    params_NP, params_RP, params_GP = build_params(
        chirp_mass, mass_ratio, redshift, theta_S, phi_S, theta_J, phi_J,
        theta_tilde, Omega_tilde, gamma_P,
        delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N)

    f_cut = Generic_precession(params_GP).get_f_cut()
    f_range = np.arange(F_MIN, f_cut, DELTA_F)

    GP = Generic_precession(params_GP)
    RP = Generic_precession(params_RP)
    NP = Generic_precession(params_NP)

    # Modulation of L around J
    cos_L_GP = GP.cos_theta_L(f_range)
    cos_L_RP = RP.cos_theta_L(f_range)
    phi_L_GP = GP.phi_L(f_range)
    phi_L_RP = RP.phi_L(f_range)

    # Fractional amplitude change
    Amp_GP = GP.amplitude(f_range)
    Amp_NP = NP.amplitude(f_range)
    Amp_RP = RP.amplitude(f_range)

    # Phase difference
    Phase_GP = GP.phase_phi_P(f_range) + 2 * GP.phase_delta_phi(f_range)
    Phase_RP = RP.phase_phi_P(f_range) + 2 * RP.phase_delta_phi(f_range)

    return Result(
        f=f_range,
        phi_L_GP=phi_L_GP, cos_L_GP=cos_L_GP,
        phi_L_RP=phi_L_RP, cos_L_RP=cos_L_RP,
        amp_GP=(Amp_GP / Amp_NP) - 1,
        amp_RP=(Amp_RP / Amp_NP) - 1,
        phase_GP=-Phase_GP,
        phase_RP=-Phase_RP,
        f_cut=f_cut,
        J=(phi_J, np.cos(theta_J)),
    )
