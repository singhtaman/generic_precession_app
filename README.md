# generic_precession

### Generic precession waveforms and their distinguishability from non-precessing and regular precessing signals

This repository contains codes supporting the unpublished work on generic precession waveforms.

## Contents

- [Description](#description)
- [Pre-requisites](#pre-requisites)
- [Acknowlegement](#acknowledgement)
- [License](#license)


## Description

We up the ante by extending on our previous work on regular precession by adding nutation to the fold where, along with regular precession parameters, we introduce nutation parameters into the waveforms and follow similar analysis to explore the distinguishability of generic precession.

Stellar binary black holes coalescing in LIGO band can have misaligned spins depending on formation channels of the binary. With misaligned spins, the orbital angular momentum ($\vec{L}$) precesses and nutates about the total angular momentum ($\vec{J}$) leaving behind amplitude and phase modulations in the GW signal. Generic precession is defined when $\vec{L}$ moves around in a cone around $\vec{J}$ with nutation, regular precession becomes a subset in this analysis. Rather than focusing on the special case of regular precession in a vast family of generically precessing sources, we turn our attention to nutation.

We introduce 3 new dimensionless parameters in the PN approximation to the GW waveforms along with 2 previously established in regular precession. The motion of $\vec{L}$ around $\vec{J}$ due to regular precession is defined by precession amplitude $\tilde{\theta}$ and precession frequency $\tilde{\Omega}$. Nutation adds a wobble (perturbation) to this motion which is defined by amplitude of this perturbation: nutation amplitude $\Delta\tilde{\theta}$, frequency of the perturbation: nutation frequency $\tilde{\omega}$, and how this perturbation changes the precession frequency: $\Delta\tilde{\Omega}$. We investigate how these 5 parameters (along with, now two, nuisance parameters: precessional phase and nutational phase) effect the GW amplitude and phase. We will also calculate mismatches between a generically precessing signal, a regularly precessing template bank and/or a non-precessing template bank to establish criterion for distinguishablity of precession along with nutation and probability of observing a precessing + nutating signal with current aLIGO sensitivities. We will explore different spin alignment scenarios and spin magnitudes to find corresponding distributions of precession parameters and Monte Carlo over sky locations & binary orientations at different cosmological redshifts to discuss the fractions of distinguishable precessing+nutating sources for current sensitivities.

In this repository, you will find python scripts and jupyter notebooks that support the data and findings we report in our (soon to be submitted) work.


## Pre-requisites
This project requires the installation of [`lal`](https://pypi.org/project/lalsuite/) and [`PyCBC`](https://pycbc.org). For a guide on how to install, I find Davide Gerosa's [notes](https://davidegerosa.com/installlal/) realy helpful. 

## Acknowledgement

This work was supported by the National Science Foundation Grant No. PHY-2309320. 

We also acknowledge the Texas Advanced Computing Center ([TACC](http://www.tacc.utexas.edu)) at The University of Texas at Austin for providing HPC resources that have contributed to the research results reported within this repository [Stanzione et al](https://doi.org/10.1145/3093338.3093385).


## License

This project is licensed under the [MIT License](LICENSE).
