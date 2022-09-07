from copy import deepcopy
from pathlib import Path
from os import rename
#
from openmc.deplete import Results
from openmc.deplete.microxs import MicroXS

import case_settings

_case = 'case3'
timedata_list, integrators_list, model, materials, depcase, chain_file, Operator, _, operator_kwargs, integrator_kwargs = case_settings.core(_case, 'full')

i, t = case_settings.parse_arguments()
integratordata = integrators_list[i]
timedata = timedata_list[t]


cwd = Path(__file__).parents[0]

Integrator, integratorcase = integratordata
timesteps, units, timecase = timedata
micro_xs = MicroXS.from_csv(f'micro_xs_{depcase}.csv')
integrator_kwargs['timestep_units'] = units
for i, timestep in enumerate(timesteps):
    operator = Operator(materials,
                        micro_xs,
                        chain_file,
                        **operator_kwargs)

    integrator = Integrator(operator,
                            [timestep],
                            **integrator_kwargs)

    integrator.integrate()
    results = Results(f'depletion_results.h5')
    materials = results.export_to_materials(-1)
    rename(cwd / 'depletion_results.h5', cwd/ _case / integratorcase / f'{depcase}_depletion_results_{timecase}_{i}.h5' )

    model.materials = materials
    micro_xs = MicroXS.from_model(model,
                                  model.materials[0],
                                  chain_file,
                                  init_lib=True)
