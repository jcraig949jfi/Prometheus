"""
Generate canonical space_groups.json from spglib + pymatgen.
Source: Bilbao Crystallographic Server data via these libraries.

Fields: number, symbol, international_full, schoenflies, hall_symbol,
        point_group, point_group_order, crystal_system, is_symmorphic,
        lattice_type, arithmetic_crystal_class
"""
import json
import os
from spglib import get_spacegroup_type
from pymatgen.symmetry.groups import SpaceGroup

LATTICE_TYPE_MAP = {
    "P": "primitive", "I": "body-centered", "F": "face-centered",
    "A": "base-centered", "B": "base-centered", "C": "base-centered",
    "R": "rhombohedral",
}

def get_lattice_type(symbol):
    first = symbol[0]
    return LATTICE_TYPE_MAP.get(first, "unknown")

def is_symmorphic(hall_symbol):
    """Symmorphic SGs have no glide/screw components — hall symbol has no translations."""
    return not any(c in hall_symbol for c in "abcndu")

# Build ITA number -> hall number lookup (use first/standard setting for each ITA)
ita_to_hall = {}
for h in range(1, 531):
    sg = get_spacegroup_type(h)
    if sg.number not in ita_to_hall:
        ita_to_hall[sg.number] = h

space_groups = []
for num in range(1, 231):
    hall_num = ita_to_hall[num]
    spg = get_spacegroup_type(hall_num)
    pmg = SpaceGroup.from_int_number(num)

    sg_data = {
        "number": num,
        "symbol": pmg.symbol,
        "international_full": spg.international_full,
        "schoenflies": spg.schoenflies,
        "hall_symbol": spg.hall_symbol,
        "point_group": pmg.point_group,
        "point_group_order": pmg.order,
        "crystal_system": pmg.crystal_system,
        "is_symmorphic": is_symmorphic(spg.hall_symbol),
        "lattice_type": get_lattice_type(pmg.symbol),
        "arithmetic_crystal_class": spg.arithmetic_crystal_class_symbol,
    }
    space_groups.append(sg_data)

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "space_groups.json")
with open(out_path, "w") as f:
    json.dump(space_groups, f, indent=2)

print(f"Generated {len(space_groups)} space groups -> {out_path}")
print(f"Sample (SG 225): {json.dumps(space_groups[224], indent=2)}")
