from copy import deepcopy
from pathlib import Path
from os import rename, remove
#
import numpy as np

from openmc.deplete import CoupledOperator, IndependentOperator
from openmc.deplete import PredictorIntegrator, CECMIntegrator
from openmc.deplete import Results, StepResult
from openmc.deplete.microxs import MicroXS
from openmc.mpi import comm
import openmc

_case = 'case3'
timedata = [(10 * [360], 's', 'minutes'),
            (10 * [4], 'h', 'hours'),
            (10 * [3], 'd', 'days'),
            (10 * [30], 'd', 'months')]

integrators = [(PredictorIntegrator, 'predictor'),
               (CECMIntegrator, 'cecm')]


#timedata = [(10 * [360], 's', 'minutes')]
timedata = [(10 * [4], 'h', 'hours')]
#timedata = [(10 * [3], 'd', 'days')]
#timedata = [(10 * [30], 'd', 'months')]

#integrators = [(PredictorIntegrator, 'predictor')]
integrators = [(CECMIntegrator, 'cecm')]




depletion_cases = [('simple', '../../openmc/tests/chain_simple.xml'),
                   ('full', '../chain_endbf71_pwr.xml')]
depletion_case = depletion_cases[1]

model = openmc.Model.from_xml(materials='../materials.xml',
geometry='../geometry.xml', settings='../settings-full.xml')
original_materials = deepcopy(model.materials)
original_materials.export_to_xml()
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
elif _case == 'case2' or _case == 'case3':
    materials = original_materials
    micro_xs = MicroXS.from_csv(f'../micro_xs_{depcase}.csv')
    Operator = IndependentOperator
    operator_args = (materials, micro_xs, chain_file)

cwd = Path(__file__).parents[0]

if _case == 'case3':
    for Integrator, integratorcase in integrators:
        for timesteps, units, timecase in timedata:
            materials = original_materials
            micro_xs = MicroXS.from_csv(f'../micro_xs_{depcase}.csv')
            integrator_kwargs['timestep_units'] = units
            # get i+1th value
            timesteps += [timesteps[-1]]
            for i, timestep in enumerate(timesteps):
                operator = IndependentOperator(materials,
                                               micro_xs,
                                               chain_file,
                                               **operator_kwargs)

                integrator = Integrator(operator,
                                        [timestep],
                                        **integrator_kwargs)

                integrator.integrate()
                results = Results(f'depletion_results.h5')
                if comm.rank == 0:
                    materials = results.export_to_materials(-1)
                    rename(cwd / 'depletion_results.h5', cwd/ '..' / _case / integratorcase / f'{depcase}_depletion_results_{timecase}_{i}.h5' )
                else:
                    materials = None
                materials = comm.bcast(materials, root=0)
                comm.barrier()

                model.materials = materials
                print("generating new microxs")
                run_kwargs = {'mpi_args': ['srun', '-N4', '-n8', '--cpu-bind=socket']}
                micro_xs = MicroXS.from_model(model,
                                              model.materials[0],
                                              chain_file,
                                              run_kwargs=run_kwargs)
                #micro_xs.to_csv(f'micro_xs_{depcase}_{i}.csv')
else:
    for Integrator, integratorcase in integrators:
        for timesteps, units, timecase in timedata:
            operator = Operator(*operator_args, **operator_kwargs)
            integrator_kwargs['timestep_units'] = units
            integrator = Integrator(operator, timesteps, **integrator_kwargs)
            integrator.integrate()
            # move file based on metadata
            if comm.rank == 0:
                cwd = Path(__file__).parents[0]
                rename(cwd / 'depletion_results.h5', cwd / '..' / _case / integratorcase / f'{depcase}_depletion_results_{timecase}.h5' )
            comm.barrier()
            #if _case == 'case1':
            #    for i, t in enumerate(timesteps):
            #        rename(cwd / f'openmc_simulation_n{i}.h5', cwd / _case / integrator_case / f'({depcase}_simulation_n{i}_{timecase}.h5')
