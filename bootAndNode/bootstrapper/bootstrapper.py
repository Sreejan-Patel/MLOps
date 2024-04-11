import json
import os
import time
import sys

class Subsystem:
    def __init__(self, name, script_path, config=None):
        self.name = name
        self.script_path = script_path
        self.config = config

    def start(self, password):
        print(f"Starting {self.name} subsystem...")
        # os.system(f"gnome-terminal -- bash -c 'cd {self.script_path}; echo {password} | sudo -S bash {self.name}.sh {password}; echo ; exec bash'")

class Bootstrapper:
    def __init__(self, init_file_path):
        self.subsystems = []
        self.load_configuration(init_file_path)

    def load_configuration(self, file_path):
        with open(file_path) as file:
            config = json.load(file)
            for subsystem_config in config['subsystems']:
                self.subsystems.append(Subsystem(**subsystem_config))

    def install_prerequisites(self, password):
        print("Installing prerequisites...")
        # os.system(f"gnome-terminal -- bash -c 'echo {password} | sudo -S bash install.sh {password}; exec bash'")

    def start_subsystems(self, password):
        for subsystem in self.subsystems:
            subsystem.start(password)
            time.sleep(5)  # Adjust the sleep time as needed

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python bootstrapper.py <path_to_init_file> <password>")
        sys.exit(1)

    init_file_path = sys.argv[1]
    password = sys.argv[2]

    bootstrapper = Bootstrapper(init_file_path)
    bootstrapper.install_prerequisites(password)  # Install Docker and GNOME Terminal first
    time.sleep(10)  # Wait for prerequisites installation to complete. Adjust as necessary.
    bootstrapper.start_subsystems(password)
    print("Bootstrapping complete.")
