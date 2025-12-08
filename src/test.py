from pathlib import Path
from configuration import Configuration

c = Configuration(Path("/home/felix/Documents/Programming/ViSort/test/default_config.toml"))


fg_info = [f"Name: {fg.name}; Sorter: {fg.sorter}\n Filters:{[vars(f) for f in fg.filters]}\n" for fg in c.filter_groups]
s_names = [s.name for s in c.sorters]



for i in fg_info:
    print(i)
print (f"Sorters:\n {s_names}\n")
