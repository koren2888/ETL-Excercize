import os

from envyaml import EnvYAML

current_folder_path = os.path.dirname(os.path.realpath(__file__))
config = EnvYAML(os.path.join(current_folder_path, 'configuration.yaml'))
