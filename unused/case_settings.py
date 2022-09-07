import argparse
from copy import deepcopy

from openmc.deplete import CoupledOperator, IndependentOperator
from openmc.deplete import PredictorIntegrator, CECMIntegrator
from openmc.deplete import Results, StepResult
from openmc.deplete.microxs import MicroXS

import openmc

integrator_to_idx = {'predictor': 0,
                     'cecm': 1}
timescale_to_idx = {'minutes': 0,
                    'hours': 1,
                    'days': 2,
                    'months': 3}
casetype_to_idx = {'simple': 0,
                   'full': 1}

def core(_case, case_type):
    timedata_list = [(10 * [360], 's', 'minutes'),
                (10 * [4], 'h', 'hours'),
                (10 * [3], 'd', 'days'),
                (10 * [30], 'd', 'months')]

    integrators_list = [(PredictorIntegrator, 'predictor'),
                        (CECMIntegrator, 'cecm')]

    depletion_cases = [('simple', '../openmc/tests/chain_simple.xml'),
                       ('full', 'chain_endbf71_pwr.xml')]
    depletion_case = depletion_cases[casetype_to_idx[case_type]]
    depcase, chain_file = depletion_case
    operator_kwargs = {'normalization_mode': 'fission-q'}
    integrator_kwargs = {'power': 174} # W/cm

    model = openmc.Model.from_xml()
    original_materials = deepcopy(model.materials)

    if _case == 'case1':
        operator_kwargs['fission_yield_mode'] = 'constant'
        operator_kwargs['reaction_rate_mode'] = 'direct'
        operator_kwargs['chain_file'] = chain_file
        Operator = CoupledOperator
        operator_args = (model,)
    elif _case == 'case2' or _case == 'case3':
        materials = original_materials
        micro_xs = MicroXS.from_csv(f'micro_xs_{depcase}.csv')
        Operator = IndependentOperator
        operator_args = (materials, micro_xs, chain_file)

    return timedata_list, integrators_list, model, original_materials, depcase, chain_file, Operator, operator_args, operator_kwargs, integrator_kwargs

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-integrator', type=str, default='predictor')
    parser.add_argument('-timescale', type=str, default='minutes')
    args = parser.parse_args()
    return(integrator_to_idx[args.integrator], timescale_to_idx[args.timescale])
