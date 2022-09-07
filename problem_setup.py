import openmc
from openmc.deplete.microxs import MicroXS
from openmc.mgxs import EnergyGroups
from openmc.deplete import Chain
import os
import numpy as np

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

settings = openmc.Settings()
# simple case
#settings.particles = 1000
#settings.inactive = 10
#settings.batches = 50
#chain_file = '../openmc/tests/chain_simple.xml'
#PROCS=2
#THREADS=4
#_case='simple'

# full case
settings.particles = 100000
settings.inactive = 25
settings.batches = 125
settings.output = {'tallies': False}
#os.system('wget -q -O chain_endbf71_pwr.xml https://anl.box.com/shared/static/os1u896bwsbopurpgas72bi6aij2zzdc.xml')
chain_file = 'chain_endbf71_pwr.xml'
PROCS=4
THREADS=8
_case='full'

chain = Chain.from_xml(chain_file)
reactions = chain.reactions

groups = EnergyGroups((0,20e6))
reaction_domain=materials[0]

model = openmc.Model(geometry, materials, settings)

run_kwargs = {'mpi_args': ['srun', '-N', PROCS, '-n', THREADS, '--cpu-bind=socket']}
micro_xs = MicroXS.from_model(model, materials[0], chain_file, run_kwargs = run_kwargs)
micro_xs.to_csv(f'micro_xs_{_case}.csv')

