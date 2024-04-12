import subprocess
import sys
import json
from kafka import KafkaProducer, KafkaConsumer

class ProcessRunner:
    def __init__(self, kafka_server='localhost:9092'):
        self.kafka_server = kafka_server
        self.producer = KafkaProducer(bootstrap_servers=self.kafka_server)
        self.consumer = KafkaConsumer("node_manager_response",
                                      bootstrap_servers=self.kafka_server,
                                      auto_offset_reset='latest')
        self.consumer.subscribe(["node_manager_response"])

    def send_process_request(self, process_name, process_path):
        process_config = {
            "name": process_name,
            "path": process_path
        }
        # Sending the configuration to the node_manager through Kafka
        self.producer.send("node_manager", json.dumps(process_config).encode('utf-8'))
        print(f"Request sent to node_manager to start {process_name} at {process_path}")

    def wait_for_confirmation(self, process_name):
        print(f"Waiting for confirmation from node_manager for {process_name}...")
        for message in self.consumer:
            if message is not None:
                value = json.loads(message.value.decode('utf-8'))
                if value.get('name') == process_name and value.get('status') == 'started':
                    print(f"Confirmation received: {process_name} has started.")
                    break

    def run_process(self, process_name, process_path):
        self.send_process_request(process_name, process_path)
        self.wait_for_confirmation(process_name)


class Bootstrapper:
    def __init__(self, nfs_path, subnet, password, nfs_server_path,install_path, agent_path, vm_manager_path, node_manager_path):
        self.nfs_path = nfs_path
        self.subnet = subnet
        self.password = password
        self.nfs_server_path = nfs_server_path
        self.install_path = install_path
        self.agent_path = agent_path
        self.vm_manager_path = vm_manager_path
        self.node_manager_path = node_manager_path
        self.process_runner = ProcessRunner()

    def start_nfs_server(self):
        subprocess.run(['bash', self.nfs_server_path, self.subnet, self.nfs_path])

    def run_basic_installation(self):
        subprocess.run(['bash', self.install_path, self.password])

    def start_agent(self):
        subprocess.Popen(['python3', self.agent_path])

    def start_initial_subsystems(self):
        self.process_runner.run_process("VM_Manager", self.vm_manager_path)
        self.process_runner.run_process("Node_Manager", self.node_manager_path)

    def start_subsystems(self, init_file):
        with open(init_file, 'r') as file:
            subsystems = json.load(file)
        for subsystem in subsystems:
            self.process_runner.run_process(subsystem['name'], subsystem['path'])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bootstrapper.py <path_to_init_file>")
        sys.exit(1)

    init_file_path = sys.argv[1]

    bootstrapper = Bootstrapper(
        nfs_path="/home/sreejan/NFS",
        subnet="196.168.100.5/24",
        password="changeme",
        nfs_server_path="/home/sreejan/NFS/system/nfs/nfs_server.sh",
        install_path="/home/sreejan/NFS/system/install.sh",
        agent_path="/home/sreejan/NFS/system/agent/agent.py",
        vm_manager_path="/home/sreejan/NFS/system/vm_manager/vm_manager.py",
        node_manager_path="/home/sreejan/NFS/system/node_manager/node_manager.py"
    )

    bootstrapper.start_nfs_server()
    bootstrapper.run_basic_installation()
    bootstrapper.start_agent()
    bootstrapper.start_initial_subsystems()
    bootstrapper.start_subsystems(init_file_path)