#suppressing a warning - UserWarning: Wswiglal-redir-stdio
import warnings
warnings.filterwarnings("ignore", "Wswiglal-redir-stdio")

import sys
sys.path.insert(0, "../")

from generic_precession import *
from systems_lib import *
from mismatch_n_SNR import *
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams["figure.dpi"] = 200

import math

# Define the default parameters for the system 1
default_precession_params_sys1_GP = redshifted_new_params(0.3, default_precession_params_sys1_GP)
default_precession_params_sys1_RP = redshifted_new_params(0.3, default_precession_params_sys1_RP)
default_precession_params_sys1_NP = redshifted_new_params(0.3, default_precession_params_sys1_NP)

# Define the default parameters for the system 2
default_precession_params_sys2_GP = redshifted_new_params(0.3, default_precession_params_sys2_GP)
default_precession_params_sys2_RP = redshifted_new_params(0.3, default_precession_params_sys2_RP)
default_precession_params_sys2_NP = redshifted_new_params(0.3, default_precession_params_sys2_NP)

# Define the default parameters for the system 3
default_precession_params_sys3_GP = redshifted_new_params(0.3, default_precession_params_sys3_GP)
default_precession_params_sys3_RP = redshifted_new_params(0.3, default_precession_params_sys3_RP)
default_precession_params_sys3_NP = redshifted_new_params(0.3, default_precession_params_sys3_NP)



# Default parameters
default_precession_params_sys2_RP['Omega_tilde'] = 2
default_precession_params_sys2_RP['theta_tilde'] = 5
default_precession_params_sys2_RP['gamma_P'] = 0

default_precession_params_sys2_GP['Omega_tilde'] = 2
default_precession_params_sys2_GP['theta_tilde'] = 5
default_precession_params_sys2_GP['gamma_P'] = 0
default_precession_params_sys2_GP['delta_theta_tilde'] = 1.2
default_precession_params_sys2_GP['delta_Omega_tilde'] = 0.2
default_precession_params_sys2_GP['omega_n_tilde'] = 1.3
default_precession_params_sys2_GP['gamma_N'] = 0

import plotly.graph_objects as go
f_min = 20
delta_f = 0.05
f_cut = Generic_precession(default_precession_params_sys2_GP).get_f_cut()
f_range = np.arange(f_min, f_cut, delta_f)


def plot_cos_L_phi_L(theta_tilde, Omega_tilde, gamma_P, delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N):
    params_GP = default_precession_params_sys2_GP.copy()
    params_GP['theta_tilde'] = theta_tilde
    params_GP['Omega_tilde'] = Omega_tilde
    params_GP['gamma_P'] = gamma_P
    
    params_GP['delta_theta_tilde'] = delta_theta_tilde
    params_GP['delta_Omega_tilde'] = delta_Omega_tilde
    if omega_n_tilde == 0:
        omega_n_tilde = 0.001
    params_GP['omega_n_tilde'] = omega_n_tilde
    params_GP['gamma_N'] = gamma_N
        
    params_RP = default_precession_params_sys2_RP.copy()
    params_RP['theta_tilde'] = theta_tilde
    params_RP['Omega_tilde'] = Omega_tilde
    params_RP['gamma_P'] = gamma_P

    # Create instances
    precession_initial_GP = Generic_precession(params_GP)
    precession_initial_NP = Generic_precession(default_precession_params_sys2_NP)
    precession_initial_RP = Generic_precession(params_RP)

    # Calculating modulation of L around the direction of the total angular momentum
    cos_L_GP = precession_initial_GP.cos_theta_L(f_range)
    cos_L_RP = precession_initial_RP.cos_theta_L(f_range)
    
    phi_L_GP = precession_initial_GP.phi_L(f_range)
    phi_L_RP = precession_initial_RP.phi_L(f_range)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=phi_L_GP, y=cos_L_GP, mode='lines', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=phi_L_RP, y=cos_L_RP, mode='lines', line=dict(color='gray', dash='dash')))
    fig.add_trace(go.Scatter(x=[np.pi/2], y=[0], mode='markers', marker=dict(color='red'), name='J'))
    
    fig.update_xaxes(tickvals=[np.pi/4, 3*np.pi/8, np.pi/2, 5*np.pi/8, 3*np.pi/4], ticktext=['π/4', '3π/8', 'π/2', '5π/8', '3π/4'])
    fig.update_yaxes(range=[-0.8, 0.8])

    fig.update_layout(
    xaxis_title=r'$φ_L$',
    yaxis_title=r'$cos θ_L$',
    title='Modulation of L',
    showlegend=False,  # Suppress the legend
    grid=dict()
    )
    
    return fig

def plot_amplitude(theta_tilde, Omega_tilde, gamma_P, delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N):
    params_GP = default_precession_params_sys2_GP.copy()
    params_GP['theta_tilde'] = theta_tilde
    params_GP['Omega_tilde'] = Omega_tilde
    params_GP['gamma_P'] = gamma_P
    
    params_GP['delta_theta_tilde'] = delta_theta_tilde
    params_GP['delta_Omega_tilde'] = delta_Omega_tilde
    if omega_n_tilde == 0:
        omega_n_tilde = 0.001
    params_GP['omega_n_tilde'] = omega_n_tilde
    params_GP['gamma_N'] = gamma_N
        
    params_RP = default_precession_params_sys2_RP.copy()
    params_RP['theta_tilde'] = theta_tilde
    params_RP['Omega_tilde'] = Omega_tilde
    params_RP['gamma_P'] = gamma_P

    # Create instances
    precession_initial_GP = Generic_precession(params_GP)
    precession_initial_NP = Generic_precession(default_precession_params_sys2_NP)
    precession_initial_RP = Generic_precession(params_RP)

    # Get amplitudes
    Amp_GP = precession_initial_GP.amplitude(f_range)
    Amp_NP = precession_initial_NP.amplitude(f_range)
    Amp_RP = precession_initial_RP.amplitude(f_range)

    frac_t_2_GP = (Amp_GP / Amp_NP) - 1
    frac_t_2_RP = (Amp_RP / Amp_NP) - 1
    frac_t_2_GP_vs_RP = (Amp_GP / Amp_RP) - 1
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=f_range, y=frac_t_2_GP, mode='lines', name='GP', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=f_range, y=frac_t_2_RP, mode='lines', name='RP', line=dict(color='gray', dash='dash')))
    fig.add_hline(y=0, line=dict(color='black', dash='dash'))
    
    fig.update_xaxes(type='log', tickvals=[20, 40, 60, 80, 100, 140], ticktext=['20', '40', '60', '80', '100', '140'])
    fig.update_yaxes(range=[-1.05, 0.95])
    
    fig.update_layout(
        xaxis_title=r'f (Hz)',
        yaxis_title=r'$B_GP/B_NP - 1$',
        title='Amplitude Difference',
        showlegend=True,
        grid=dict()
    )
    
    return fig


def plot_phase(theta_tilde, Omega_tilde, gamma_P, delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N):
    params_GP = default_precession_params_sys2_GP.copy()
    params_GP['theta_tilde'] = theta_tilde
    params_GP['Omega_tilde'] = Omega_tilde
    params_GP['gamma_P'] = gamma_P
    
    params_GP['delta_theta_tilde'] = delta_theta_tilde
    params_GP['delta_Omega_tilde'] = delta_Omega_tilde
    if omega_n_tilde == 0:
        omega_n_tilde = 0.001
    params_GP['omega_n_tilde'] = omega_n_tilde
    params_GP['gamma_N'] = gamma_N
        
    params_RP = default_precession_params_sys2_RP.copy()
    params_RP['theta_tilde'] = theta_tilde
    params_RP['Omega_tilde'] = Omega_tilde
    params_RP['gamma_P'] = gamma_P

    # Create instances
    precession_initial_GP = Generic_precession(params_GP)
    precession_initial_NP = Generic_precession(default_precession_params_sys2_NP)
    precession_initial_RP = Generic_precession(params_RP)

    # Get amplitudes
    Phase_GP = precession_initial_GP.phase_phi_P(f_range) + 2*precession_initial_GP.phase_delta_phi(f_range)
    Phase_RP = precession_initial_RP.phase_phi_P(f_range) + 2*precession_initial_RP.phase_delta_phi(f_range)

    phase_diff_t_2_GP = (Phase_GP)
    phase_diff_t_2_RP = (Phase_RP)
    phase_diff_t_2_GP_vs_RP = (Phase_GP - Phase_RP)
    
    if max(phase_diff_t_2_GP) > 3.25:
        ylim_min = - max(phase_diff_t_2_GP) - 0.5
    else:
        ylim_min = -3.25

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=f_range, y=-phase_diff_t_2_GP, mode='lines', name='GP', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=f_range, y=-phase_diff_t_2_RP, mode='lines', name='RP', line=dict(color='gray', dash='dash')))
    fig.add_hline(y=0, line=dict(color='black', dash='dash'))
    
    fig.update_xaxes(type='log', tickvals=[20, 40, 60, 80, 100, 140], ticktext=['20', '40', '60', '80', '100', '140'])
    fig.update_yaxes(range=[ylim_min, 0.75])
    
    fig.update_layout(
        xaxis_title='f (Hz)',
        yaxis_title=r'$Φ_{GP} - Φ_{NP}$',
        title='Phase Difference',
        showlegend=False,
        grid=dict()
    )
    
    return fig

from plotly.subplots import make_subplots
from dash import Dash, dcc, html
from dash.dependencies import Input, Output


def plot_combined(theta_tilde, Omega_tilde, gamma_P, delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N):
    label = (
        f'Generic precession from inspiralling binary black holes in an edge-on system, total angular momentum direction specified as (θ_J = π/2, φ_J = π/2), <br>'
        f'that is located at z = 0.3 with sky location (θ_S = π/4, φ_S = 0). The system has a chirp mass of 10 solar masses '
        f'with mass ratio q = 0.6.<br>'
        f'The generic precession parameters are: θ̃ = {theta_tilde:.1f}, Ω̃ = {Omega_tilde:.1f}, γ_P = {gamma_P:.1f}, '
        f'Δθ̃ = {delta_theta_tilde:.1f}, ΔΩ̃ = {delta_Omega_tilde:.1f}, ω̃ = {omega_n_tilde:.1f}, γ_N = {gamma_N:.1f}'
    )
    fig = make_subplots(rows=1, cols=3, subplot_titles=(r"Modulation", "Amplitude", "Phase"))
    
    fig_cos_L = plot_cos_L_phi_L(theta_tilde, Omega_tilde, gamma_P, delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N)
    fig_amp = plot_amplitude(theta_tilde, Omega_tilde, gamma_P, delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N)
    fig_phase = plot_phase(theta_tilde, Omega_tilde, gamma_P, delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N)
    

    # Add traces and update axes for fig_cos_L
    for trace in fig_cos_L['data']:
        fig.add_trace(trace, row=1, col=1)

        fig.update_xaxes(title_text=r'φ_L', row=1, col=1)
        fig.update_layout(showlegend=False)
        fig.update_yaxes(title_text=r'cos θ_L', title_standoff=1, row=1, col=1)
        fig.update_yaxes(range=[-0.8, 0.8], row=1, col=1)
        fig.update_xaxes(range=[np.pi/4, 3*np.pi/4], tickvals=[np.pi/4, 3*np.pi/8, np.pi/2, 5*np.pi/8, 3*np.pi/4], ticktext=['π/4', '3π/8', 'π/2', '5π/8', '3π/4'], row=1, col=1)

    # Add traces and update axes for fig_amp
    for trace in fig_amp['data']:
        fig.add_trace(trace, row=1, col=2)

        fig.update_xaxes(type='log', title_text='f (Hz)', row=1, col=2)
        fig.update_yaxes(title_text=r'B(GP)/B(NP) - 1', title_standoff=1, row=1, col=2)
        fig.update_layout(showlegend=True)
        fig.update_yaxes(range=[-1.05, 0.95], row=1, col=2)
        fig.update_xaxes(range=[math.log10(19), math.log10(150)], tickmode='array', tickvals=[math.log10(20), math.log10(40), math.log10(60), math.log10(80), math.log10(100), math.log10(140)], ticktext=['20', '40', '60', '80', '100', '140'], row=1, col=2)
        
    # Add traces and update axes for fig_phase
    for trace in fig_phase['data']:
        fig.add_trace(trace, row=1, col=3)

        fig.update_xaxes(type='log', title_text='f (Hz)', row=1, col=3)
        fig.update_yaxes(title_text=r'Φ(GP) - Φ(NP)', title_standoff=1, row=1, col=3)
        fig.update_layout(showlegend=False)
        fig.update_yaxes(range=[-3.25, 0.75], row=1, col=3)
        fig.update_xaxes(range=[math.log10(19), math.log10(150)], tickmode='array', tickvals=[math.log10(20), math.log10(40), math.log10(60), math.log10(80), math.log10(100), math.log10(140)], ticktext=['20', '40', '60', '80', '100', '140'], row=1, col=3)
        
    # Update layout
    fig.update_layout(
        title=label,
        margin=dict(t=150),
        legend=dict(title='Legend', itemsizing='constant'),
        width=1350,
        height=575,
        xaxis=dict(tickmode='array', tickvals=[np.pi/4, 3*np.pi/8, np.pi/2, 5*np.pi/8, 3*np.pi/4], ticktext=['π/4', '3π/8', 'π/2', '5π/8', '3π/4']),
        xaxis2=dict(tickmode='array', tickvals=[20, 40, 60, 80, 100, 120, 140], ticktext=['20', '40', '60', '80', '100', '120', '140']),
        xaxis3=dict(tickmode='array', tickvals=[20, 40, 60, 80, 100, 120, 140], ticktext=['20', '40', '60', '80', '100', '120', '140']),
    )
    
    return fig

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='combined-plot'),
    
    html.Div(style={'margin-top': '20px'}),
    
    html.Div([
        html.Label(f'Precession amplitude, θ̃'),
        dcc.Slider(id='theta_tilde-slider', 
                   min=0, max=9, step=0.1, value=5, 
                   marks={i: str(i) for i in range(10)}, 
                   tooltip={"placement": "bottom", "always_visible": False}),
    ], style={'width': '40%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label(f'Precession frequency, Ω̃'),
        dcc.Slider(id='Omega_tilde-slider', 
                   min=0, max=3, step=0.1, value=2, 
                   marks={i: str(i) for i in [0, 0.5, 1, 1.5, 2, 2.5, 3]}, 
                   tooltip={"placement": "bottom", "always_visible": False}),
    ], style={'width': '35%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label(r'Precessional phase, γ_P'),
        dcc.Slider(id='gamma_P-slider', 
                   min=0, max=2*np.pi, step=np.pi/16, value=0, 
                   marks={
                            0: '0',
                            np.pi/2: r'π/2',
                            np.pi: r'π',
                            3*np.pi/2: r'3π/2',
                            2*np.pi: r'2π'
                        }, 
                   tooltip={"placement": "bottom", "always_visible": False}),
    ], style={'width': '25%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label(r'Nutation amplitude, Δθ̃'),
        dcc.Slider(id='delta_theta_tilde-slider', 
                   min=0, max=2.5, step=0.1, value=1.2, 
                   marks={i: str(i) for i in [0, 0.5, 1, 1.5, 2, 2.5]}, 
                   tooltip={"placement": "bottom", "always_visible": False}),
    ], style={'width': '25%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label(r'Change in precession frequency, ΔΩ̃'),
        dcc.Slider(id='delta_Omega_tilde-slider', 
                   min=-1, max=1, step=0.1, value=0.2, 
                   marks={i: str(i) for i in [-1, -0.5, 0, 0.5, 1]}, 
                   tooltip={"placement": "bottom", "always_visible": False}),
    ], style={'width': '25%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label(r'Nutation frequency, ω̃'),
        dcc.Slider(id='omega_n_tilde-slider',
                   min=0, max=6, step=0.1, value=1.3, 
                   marks={i: str(i) for i in range(7)}, 
                   tooltip={"placement": "bottom", "always_visible": False}),
    ], style={'width': '25%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label(r'Nutational phase, γ_N'),
        dcc.Slider(id='gamma_N-slider',
                   min=0, max=2*np.pi, step=np.pi/16, value=0, 
                   marks={
                            0: '0',
                            np.pi/2: r'π/2',
                            np.pi: r'π',
                            3*np.pi/2: r'3π/2',
                            2*np.pi: r'2π'
                        }, 
                   tooltip={"placement": "bottom", "always_visible": False}),
    ], style={'width': '25%', 'display': 'inline-block'}),
])


@app.callback(
    Output('combined-plot', 'figure'),
    Input('theta_tilde-slider', 'value'),
    Input('Omega_tilde-slider', 'value'),
    Input('gamma_P-slider', 'value'),
    Input('delta_theta_tilde-slider', 'value'),
    Input('delta_Omega_tilde-slider', 'value'),
    Input('omega_n_tilde-slider', 'value'),
    Input('gamma_N-slider', 'value')
)

def update_plot(theta_tilde, Omega_tilde, gamma_P, delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N):
    return plot_combined(theta_tilde, Omega_tilde, gamma_P, delta_theta_tilde, delta_Omega_tilde, omega_n_tilde, gamma_N)

if __name__ == '__main__':
    # Run and save the app as a static HTML file
    app.run_server(debug=False)
