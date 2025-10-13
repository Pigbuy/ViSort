from filter_types.filter_types import FilterTypes

class Filter():
    def __init__(self, filter_type_name:str) -> "Filter":

        self.filter_type = FilterTypes[filter_type_name]
        
        return self