import json
import paramiko
import threading
from kafka import KafkaConsumer, KafkaProducer

SCRIPT_PATH = '/path/to/bootstrap.sh'
VM_LIST_PATH = '/path/to/vm_list.json'

class VM:
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password
        self.is_active = False

    def activate_vm(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=self.ip, username=self.username, password=self.password)
        sftp_client = ssh_client.open_sftp()
        sftp_client.put(SCRIPT_PATH, '/tmp/bootstrap.sh')
        sftp_client.close()
        ssh_client.exec_command('chmod +x /tmp/bootstrap.sh && nohup /tmp/bootstrap.sh &')
        self.is_active = True
        ssh_client.close()

    def get_health(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=self.ip, username=self.username, password=self.password)
        _, stdout, _ = ssh_client.exec_command('python3 get_health.py')
        output = stdout.read().decode()
        cpu_usage, memory_free = map(float, output.strip().split(','))
        ssh_client.close()
        return cpu_usage, memory_free

class VMManager:
    def __init__(self, vm_list_path, kafka_server='localhost:9092', topic_request='vm_request', topic_response='vm_response'):
        self.vm_list_path = vm_list_path
        self.vms = self.load_vms()
        self.lock = threading.Lock()
        self.producer = KafkaProducer(bootstrap_servers=kafka_server)
        self.consumer = KafkaConsumer(topic_request, bootstrap_servers=kafka_server, auto_offset_reset='earliest')
        self.topic_response = topic_response

    def load_vms(self):
        with open(self.vm_list_path, 'r') as file:
            vm_data = json.load(file)
            return [VM(vm['ip'], vm['username'], vm['password']) for vm in vm_data]

    def handle_vm_requests(self):
        for message in self.consumer:
            data = json.loads(message.value.decode('utf-8'))
            response = self.allocate_vm()
            self.producer.send(self.topic_response, json.dumps(response).encode('utf-8'))

    def allocate_vm(self):
        with self.lock:
            for vm in self.vms:
                if not vm.is_active:
                    vm.activate_vm()
                    return {"msg": "VM allocated", "ip": vm.ip, "username": vm.username, "password": vm.password}
            
            # Assess health of all active VMs
            health_stats = [(vm.get_health(), vm) for vm in self.vms if vm.is_active]
            if health_stats:
                # Select the VM with the lowest CPU usage and most free memory
                best_vm = min(health_stats, key=lambda x: (x[0][0], -x[0][1]))[1]
                return {"msg": "VM allocated", "ip": best_vm.ip, "username": best_vm.username, "password": best_vm.password}

            return {"msg": "No inactive VM available"}

# Usage
if __name__ == '__main__':
    vm_manager = VMManager(VM_LIST_PATH)
    vm_manager.handle_vm_requests()
