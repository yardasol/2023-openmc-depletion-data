import argparse
import os

import numpy as np

import openmc
from openmc.deplete.microxs import MicroXS
from openmc.mgxs import EnergyGroups
from openmc.deplete import Chain

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', choices=['simple', 'full'],
                        type=str,
                        default='simple',
                        help='depletion chain complexity')
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
    return str(args.m), int(args.N), int(args.n)

fuel = openmc.Material(name="uo2")
fuel.add_element("U", 1, percent_type="ao", enrichment=4.25)
fuel.add_element("O", 2)
fuel.set_density("g/cc", 10.4)

clad = openmc.Material(name="clad")
clad.add_element("Zr", 1)
clad.set_density("g/cc", 6)

water = openmc.Material(name="water")
water.add_element("O", 1)
water.add_element("H", 2)
water.set_density("g/cc", 1.0)
water.add_s_alpha_beta("c_H_in_H2O")

radii = [0.42, 0.45]
fuel.volume = np.pi * radii[0] ** 2

materials = openmc.Materials([fuel, clad, water])

pin_surfaces = [openmc.ZCylinder(r=r) for r in radii]
pin_univ = openmc.model.pin(pin_surfaces, materials)
bound_box = openmc.rectangular_prism(1.24, 1.24, boundary_type="reflective")
root_cell = openmc.Cell(fill=pin_univ, region=bound_box)
geometry = openmc.Geometry([root_cell])

if not os.path.exists('../chain_endbf71_pwr.xml'):
    os.system('wget -q -O ../chain_endbf71_pwr.xml https://anl.box.com/shared/static/os1u896bwsbopurpgas72bi6aij2zzdc.xml')

mode_dict = {'simple': (openmc.Settings(**{'batches': 50,
                                         'inactive': 10,
                                         'particles': 1000}),
                        '../../openmc/tests/chain_simple.xml'),
             'full': (openmc.Settings(**{'batches': 125,
                                       'inactive': 25,
                                       'particles': 100000,
                                       'tallies': False}),
                      '../chain_endbf71_pwr.xml')
            }
mode, N, n = parse_arguments()
settings, chain_file = mode_dict[mode]
settings.export_to_xml(f'../settings-{mode}.xml')
materials.export_to_xml('../materials.xml')
geometry.export_to_xml('../geometry.xml')
                                         
chain = Chain.from_xml(chain_file)
reactions = chain.reactions

groups = EnergyGroups((0,20e6))
reaction_domain=materials[0]

model = openmc.Model(geometry, materials, settings)

#runtime_dir = f'runtime-setup-{mode}'
#if comm.rank == 0:
#    if not os.path.exists(runtime_dir):
#        os.mkdir(runtime_dir)

#os.chdir(runtime_dir)

run_kwargs = {'mpi_args': ['srun', f'-N{N}', f'-n{n}', '--cpu-bind=socket']}
micro_xs = MicroXS.from_model(model, materials[0], chain_file, run_kwargs = run_kwargs)
micro_xs.to_csv(f'../micro_xs_{mode}.csv')

#cwd = Path.cwd().parents[0] / runtime_dir
#os.rename(cwd / 'summary.h5', cwd / '..' / f'{mode}_summary.h5' )
#os.rename(cwd / f'statepoint.{settings.batches}.h5', cwd / '..' / f'statepoint.setup_{mode}.h5')
