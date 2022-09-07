from pathlib import Path
from os import rename
#

import case_settings

_case = 'case1'
timedata_list, integrators_list, _, _, depcase, _, Operator, operator_args, operator_kwargs, integrator_kwargs = case_settings.core(_case, 'simple')

i, t = case_settings.parse_arguments()
integratordata = integrators_list[i]
timedata = timedata_list[t]

cwd = Path(__file__).parents[0]

Integrator, integratorcase = integratordata
timesteps, units, timecase = timedata
operator = Operator(*operator_args, **operator_kwargs)
integrator_kwargs['timestep_units'] = units
integrator = Integrator(operator, timesteps, **integrator_kwargs)
integrator.integrate()
# move file based on metadata
cwd = Path(__file__).parents[0]
rename(cwd / 'depletion_results.h5', cwd / _case / integratorcase / f'{depcase}_depletion_results_{timecase}.h5' )
