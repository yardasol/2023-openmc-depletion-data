# 2023-openmc-depletion-data
This repository holds input files, scripts, and data for one-group transport
independent depletion validation. It is assumed to be located in the same parent
directory as a source installation of OpenMC.

# Cases
- `case1`: OpenMC transport-coupled depletion calculation on a PWR pincell
- `case2`: OpenMC transport-independent depletion calculation on a PWR pincell
- `case3`: OpenMC transport-independent depletion calculation on a PWR pincell that updates the cross-section data at each step.

# Guide on running the simulations
- 1. ``source generate_setup.sh; source submit_setup.sh`` to generate the material, geometry, settings, and microscopic cross sections
- 2. ``source generate_cases.sh; source submit_cases.sh`` to run all cases
- 3. Use the ``compare-results.ipynb`` notebook to analyze results

These simulations were performed on the Bebop machine at ANL using the
official ENDF/B-VII.1 cross section data, so modification may be necessary to reproduce results if ran on a different machine.

# Guide on generating figures
The `plot_barcharts.ipynb` notebook will generate figures used in publication.
The `compare_results.ipynb` notebook has a workflow set up to investigate each
case individually by nuclide.
