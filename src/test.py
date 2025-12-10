from pathlib import Path
from configuration import Configuration

c = Configuration(Path("/home/felix/Documents/Programming/ViSort/test/default_config.toml"))


s_names = [vars(s) for s in c.sorters]

print (f"Sorters:\n {s_names}\n")