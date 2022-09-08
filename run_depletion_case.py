import argparse
import os
from copy import deepcopy
from pathlib import Path

import numpy as np

from openmc.deplete import CoupledOperator, IndependentOperator
from openmc.deplete import PredictorIntegrator, CECMIntegrator
from openmc.deplete import Results, StepResult
from openmc.deplete.microxs import MicroXS
from openmc.mpi import comm
import openmc

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c',
                        choices=[1, 2, 3],
                        type=int,
                        default=1,
                        help='depletion case. See README for defintions')
    parser.add_argument('-i',
                        choices=['predictor', 'cecm'],
                        type=str,
                        default='predictor',
                        help='integrator class to use')
    parser.add_argument('-m',
                        choices=['simple', 'full'],
                        type=str,
                        default='simple',
                        help='depletion chain complexity')
    parser.add_argument('-t',
                        choices=['minutes', 'days', 'hours', 'months'],
                        type=str,
                        default='days',
                        help='timestep scale')
    parser.add_argument('-N',
                        type=int,
                        default=2,
                        help='number of nodes to use in \
                        distributed memory runs')
    parser.add_argument('-n',
                        type=int,
                        default=4,
                        help='number of MPI ranks to use')

    args = parser.parse_args()
    return int(args.c), str(args.i), str(args.m), str(args.t), int(args.N), int(args.n)


_case, integratorcase, depcase, timecase, N, n = parse_arguments()

_case = f'case{_case}'

timedata = {'minutes': (10 * [360], 's'),
            'hours': (10 * [4], 'h'),
            'days': (10 * [3], 'd'),
            'months': (10 * [30], 'd')}

integrators = {'predictor': PredictorIntegrator,
               'cecm': CECMIntegrator}

depletion_cases = {'simple': '../../openmc/tests/chain_simple.xml',
                   'full': '../chain_endbf71_pwr.xml'}

timesteps, units = timedata[timecase]
Integrator = integrators[integratorcase]
chain_file = depletion_cases[depcase]

model = openmc.Model.from_xml(geometry='../geometry.xml',
                              materials='../materials.xml',
                              settings=f'../settings-{depcase}.xml')

original_materials = deepcopy(model.materials)
#operator_kwargs = {'normalization_mode': 'source-rate'}
#integrator_kwargs = {'source_rates': 1164719970082145.0}

operator_kwargs = {'normalization_mode': 'fission-q'}
integrator_kwargs = {'power': 174} # W/cm

runtime_dir = f'{_case}_{depcase}_{integratorcase}_{timecase}'
#if comm.rank == 0:
#    if not os.path.exists(runtime_dir):
#        os.mkdir(runtime_dir)
#comm.barrier()
#os.chdir(runtime_dir)

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

cwd = Path().cwd().resolve()

if _case == 'case3':
    materials = original_materials
    materials.export_to_xml()
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
        materials = results.export_to_materials(-1)
        if comm.rank == 0:
            os.rename(cwd / 'depletion_results.h5', cwd/ '..' / _case / integratorcase / f'{depcase}_depletion_results_{timecase}_{i}.h5' )
        comm.barrier()

        model.materials = materials
        print("generating new microxs")
        run_kwargs = {'mpi_args': ['srun', f'-N{N}', f'-n{n}', '--cpu-bind=socket']}
        micro_xs = MicroXS.from_model(model,
                                      model.materials[0],
                                      chain_file,
                                      run_kwargs=run_kwargs)
        #micro_xs.to_csv(f'micro_xs_{depcase}_{i}.csv')
else:
    operator = Operator(*operator_args, **operator_kwargs)
    integrator_kwargs['timestep_units'] = units
    integrator = Integrator(operator, timesteps, **integrator_kwargs)
    integrator.integrate()
    # move file based on metadata
    if comm.rank == 0:
        os.rename(cwd / 'depletion_results.h5', cwd / '..' / _case / integratorcase / f'{depcase}_depletion_results_{timecase}.h5' )
    comm.barrier()
    #if _case == 'case1':
    #    for i, t in enumerate(timesteps):
    #        os.rename(cwd / f'openmc_simulation_n{i}.h5', cwd / _case / integrator_case / f'({depcase}_simulation_n{i}_{timecase}.h5')
