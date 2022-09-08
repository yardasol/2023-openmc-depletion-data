# 2023-openmc-depletion-data
This repository holds input files and data for the paper "Extension of the OpenMC depletion module for indirect coupling with external transport solvers"

# Cases
- `case1`: OpenMC transport-coupled depletion calculation on a PWR pincell
- `case2`: OpenMC transport-independent depletion calculation on a PWR pincell
- `case3`: OpenMC transport-independent depletion calculation on a PWR pincell that updates the cross-section data at each step.

# Guide on running the simulations
- 1. ``source generate_setup.sh; source submit_setup.sh`` to generate the material, geometry, settings, and microscopic cross sections
- 2. ``source generate_cases.sh; source submit_cases.sh`` to run all cases
- 3. Use the ``compare-results.ipynb`` notebook to analyze results
