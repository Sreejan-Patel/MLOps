import json
import subprocess
import sys
import threading
import uuid
import psutil
from kafka import KafkaProducer, KafkaConsumer

class Process:
    def __init__(self, name, path, command):
        self.name = name
        self.command = command
        self.path = path
        self.process = None
        self.process_id = str(uuid.uuid4())  # Generate unique ID for each process

    def start(self):
        cdCommand = "cd " + self.path
        self.command = cdCommand + " && " + self.command
        self.process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return self.process_id

    def kill(self):
        if self.process:
            self.process.kill()
            self.process = None

    def reset(self):
        if self.process:
            self.kill()
            self.start()

    def status(self):
        if self.process and self.process.poll() is None:
            return "Running"
        else:
            return "Not running or not started"

class Processes:
    def __init__(self):
        self.processes = {}

    def start_process(self, name, path, command):
        new_process = Process(name, path, command)
        process_id = new_process.start()
        self.processes[process_id] = new_process
        return process_id

    def kill_process(self, process_id):
        if process_id in self.processes:
            self.processes[process_id].kill()
            # Remove the process from the list
            del self.processes[process_id]

    def reset_process(self, process_id):
        if process_id in self.processes:
            self.processes[process_id].reset()

    def get_processes(self):
        return {pid: proc.status() for pid, proc in self.processes.items()}

class Agent:
    def __init__(self, node_id):
        self.node_id = node_id
        self.processes = Processes()

    def start_process(self, process_config):
        name = process_config['name']
        command = process_config['command']
        path = process_config['path']
        return {'method': 'start_process', 'process_id': self.processes.start_process(name, path,command)}

    def kill_process(self, process_id):
        self.processes.kill_process(process_id)
        return {'method': 'kill_process', 'process_id': process_id}

    def reset_process(self, process_id):
        self.processes.reset_process(process_id)
        return {'method': 'reset_process', 'process_id': process_id}

    def get_processes(self):
        return {'method': 'get_processes', 'processes': self.processes.get_processes()}

    def get_health(self):
        # Improved health check using psutil
        free_cores = psutil.cpu_count(logical=True)
        free_memory = psutil.virtual_memory().available
        free_memory_gb = round(free_memory / (1024**3), 2)  # Convert bytes to GB

        # Return both CPU and memory info
        return {
            'method': 'get_health',
            'free_cores': free_cores,
            'free_memory_gb': free_memory_gb
        }

if __name__ == "__main__":
    node_id = sys.argv[1]  # get the node_id.

    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    log = {'Process': 'Agent' + node_id, 'message': 'I have been run'}
    producer.send("logs", json.dumps(log).encode('utf-8'))

    agent = Agent(node_id)
    consumer = KafkaConsumer('AgentIn', bootstrap_servers='localhost:9092')
    print("Starting the agent server\n")

    for msg in consumer:
        request = json.loads(msg.value)
        if request['node_id'] == node_id:
            log = {'Process': 'Agent ' + node_id, 'message': 'I have received a message', 'text': request}
            # Handling the request based on method
            if request['method'] == 'start_process':
                result = agent.start_process(request['args']['config'])
            elif request['method'] == 'kill_process':
                result = agent.kill_process(request['args']['process_id'])
            elif request['method'] == 'reset_process':
                result = agent.reset_process(request['args']['process_id'])
            elif request['method'] == 'get_processes':
                result = agent.get_processes()
            elif request['method'] == 'get_health':
                result = agent.get_health()
            else:
                result = {'error': 'Invalid method'}
                print("Invalid method", request['method'])

            # Send output
            response = {"request": request, "result": result}
            producer.send('AgentOut', json.dumps(response).encode('utf-8'))
