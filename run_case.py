from copy import deepcopy
from pathlib import Path
from os import rename, remove
#
import numpy as np

from openmc.deplete import CoupledOperator, IndependentOperator
from openmc.deplete import PredictorIntegrator, CECMIntegrator
from openmc.deplete import Results, StepResult
from openmc.deplete.microxs import MicroXS
import openmc

_case = 'case2'
timedata = [(6 * [360], 's', 'minutes'),
            (6 * [4], 'h', 'hours'),
            (6 * [3], 'd', 'days'),
            (6 * [30], 'd', 'months')]

#timedata = [(1 * [360], 's', 'minutes')]
#timedata = [(20 * [4], 'h', 'hours')]
#timedata = [(1 * [5], 'd', 'days')]
#timedata = [(1 * [100], 'd', 'months')]



#integrators = [(PredictorIntegrator, 'predictor')]
              # (CECMIntegrator, 'cecm')]
integrators = [(CECMIntegrator, 'cecm')]

depletion_cases = [('simple', '../openmc/tests/chain_simple.xml'),
                   ('full', 'chain_endbf71_pwr.xml')]
depletion_case = depletion_cases[0]

model = openmc.Model.from_xml()
original_materials = deepcopy(model.materials)
#operator_kwargs = {'normalization_mode': 'source-rate'}
#integrator_kwargs = {'source_rates': 1164719970082145.0}

operator_kwargs = {'normalization_mode': 'fission-q'}
integrator_kwargs = {'power': 174} # W/cm
depcase, chain_file = depletion_case

if _case == 'case1':
    operator_kwargs['fission_yield_mode'] = 'constant'
    operator_kwargs['reaction_rate_mode'] = 'direct'
    operator_kwargs['chain_file'] = chain_file
    Operator = CoupledOperator
    operator_args = (model,)
elif _case == 'case2':
    materials = original_materials
    micro_xs = MicroXS.from_csv('micro_xs_simple.csv')
    Operator = IndependentOperator
    operator_args = (materials, micro_xs, chain_file)

cwd = Path(__file__).parents[0]

if _case == 'case3' or _case == 'alt_case3':
    for Integrator, integratorcase in integrators:
        for timesteps, units, timecase in timedata:
            materials = original_materials
            micro_xs = MicroXS.from_csv(f'micro_xs_simple.csv')
            prev_results = None
            integrator_kwargs['timestep_units'] = units
            for i, timestep in enumerate(timesteps):
                operator_kwargs['prev_results'] = prev_results
                operator = IndependentOperator(materials,
                                               micro_xs,
                                               chain_file,
                                               **operator_kwargs)

                integrator = Integrator(operator,
                                        [timestep],
                                        **integrator_kwargs)

                integrator.integrate()
                results = Results(f'depletion_results.h5')
                materials = results.export_to_materials(-1)
                if _case == 'case3':
                    prev_results = results
                else:
                    rename(cwd / 'depletion_results.h5', cwd/ _case / integratorcase / f'{depcase}_depletion_results_{timecase}_{i}.h5' )

                model.materials = materials
                micro_xs = MicroXS.from_model(model,
                                              model.materials[0],
                                              chain_file)
                #micro_xs.to_csv(f'micro_xs_simple_{i}.csv')
                #micro_xs = MicroXS.from_csv(f'micro_xs_simple_{i}.csv')
                ## TODO: Add machinery to update flux
            # move file based on metadata
            if _case == 'case3':
                rename(cwd / 'depletion_results.h5', cwd/ _case / integratorcase / f'{depcase}_depletion_results_{timecase}.h5' )



else:
    for Integrator, integratorcase in integrators:
        for timesteps, units, timecase in timedata:
            operator = Operator(*operator_args, **operator_kwargs)
            integrator_kwargs['timestep_units'] = units
            integrator = Integrator(operator, timesteps, **integrator_kwargs)
            integrator.integrate()
            # move file based on metadata
            cwd = Path(__file__).parents[0]
            rename(cwd / 'depletion_results.h5', cwd / _case / integratorcase / f'{depcase}_depletion_results_{timecase}.h5' )

