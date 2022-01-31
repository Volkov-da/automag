"""
automag.2_coll.1_run_enumlib
============================

Script which runs enumlib.

.. codeauthor:: Michele Galasso <m.galasso@yandex.com>
"""

from input import *

import os
import subprocess

from pymatgen.core.structure import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

# full path to poscar file
path_to_poscar = '../geometries/' + poscar_file

# create a pymatgen Structure object
structure = Structure.from_file(path_to_poscar)

# find out which atoms are magnetic
for element in structure.composition.elements:
    if 'magnetic_atoms' not in globals():
        element.is_magnetic = element.is_transition_metal
    else:
        if element.name in magnetic_atoms:
            element.is_magnetic = True
        else:
            element.is_magnetic = False

if os.path.exists('enumlib'):
    print('Cannot create a folder named enumlib: an object with the same name already exists.')
    exit()

os.mkdir('enumlib')
os.chdir('enumlib')

with open('struct_enum.in', 'w') as f:
    f.write('generated by Automag\n')
    f.write('bulk\n')

    for lat_vector in structure.lattice.matrix:
        for component in lat_vector:
            f.write(f'{component:14.10f}        ')
        f.write('\n')

    case = 0
    for element in structure.composition.elements:
        if element.is_magnetic:
            case += 2
        else:
            case += 1

    f.write(f'  {case} -nary case\n')
    f.write(f'    {structure.num_sites} # Number of points in the multilattice\n')

    offset = 0
    analyzer = SpacegroupAnalyzer(structure)
    symmetrized_structure = analyzer.get_symmetrized_structure()
    for i, wyckoff in enumerate(symmetrized_structure.equivalent_sites):
        if wyckoff[0].specie.is_magnetic:
            offset += 1

        for atom in wyckoff:
            for component in atom.coords:
                f.write(f'{component:14.10f}        ')
            if atom.specie.is_magnetic:
                f.write(f'{i + offset - 1}/{i + offset}\n')
            else:
                f.write(f'{i + offset}\n')

    f.write(f'    1 {supercell_size}   # Starting and ending cell sizes for search\n')
    f.write('0.10000000E-06 # Epsilon (finite precision parameter)\n')
    f.write('full list of labelings\n')
    f.write('# Concentration restrictions\n')

    for wyckoff in symmetrized_structure.equivalent_sites:
        if wyckoff[0].specie.is_magnetic:
            for _ in range(2):
                f.write(f'{len(wyckoff):4d}')
                f.write(f'{len(wyckoff):4d}')
                f.write(f'{symmetrized_structure.num_sites * 2:4d}\n')
        else:
            f.write(f'{len(wyckoff) * 2:4d}')
            f.write(f'{len(wyckoff) * 2:4d}')
            f.write(f'{symmetrized_structure.num_sites * 2:4d}\n')

process = subprocess.Popen('/home/michele/softs/enumlib/src/enum.x')
try:
    process.wait(timeout=60)
except subprocess.TimeoutExpired:
    process.kill()

os.system('/home/michele/softs/enumlib/aux_src/makeStr.py 1 500')