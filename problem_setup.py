import openmc
from openmc.deplete.microxs import MicroXS
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
settings.particles = 1000
settings.inactive = 10
settings.batches = 50
settings.verbosity = 1

model = openmc.Model(geometry, materials, settings)
model.export_to_xml()

#os.system('wget -q -O chain_endbf71_pwr.xml https://anl.box.com/shared/static/os1u896bwsbopurpgas72bi6aij2zzdc.xml')

#chain_file = 'chain_endbf71_pwr.xml'
chain_file = '../openmc/tests/chain_simple.xml'
micro_xs = MicroXS.from_model(model,fuel, chain_file)
#micro_xs.to_csv('micro_xs_full.csv')
micro_xs.to_csv('micro_xs_simple.csv')

