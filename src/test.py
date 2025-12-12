from filter_types.filter_arg_types.location import Location, safe_geocode

loc = Location(input())
loc2 = Location(input())

print(loc.are_coords_in_same_smallest_region(loc2.get_coords()))