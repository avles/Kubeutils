import subprocess
import json
import csv

def get_requested_resources():
    
    cmd = "kubectl get pods --all-namespaces -o=json"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    requested_resources = {}

    for item in data['items']:
        namespace = item['metadata']['namespace']
        pod_name = item['metadata']['name']
        cpu_request = 'N/A'
        mem_request = 'N/A'

        containers = item['spec']['containers']
        for container in containers:
            if 'resources' in container:
                resources = container['resources']
                if 'requests' in resources:
                    cpu_request = resources['requests'].get('cpu', 'N/A')
                    mem_request = resources['requests'].get('memory', 'N/A')

        requested_resources[f"{namespace}/{pod_name}"] = {'cpu_request': cpu_request, 'mem_request': mem_request}
    return requested_resources

def get_actual_resources():
    cmd = "kubectl top pod --all-namespaces --no-headers"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    actual_resources = {}

    for line in lines:
        parts = line.split()
        namespace = parts[0]
        pod_name = parts[1]
        cpu_usage = parts[2]
        mem_usage = parts[3]

        actual_resources[f"{namespace}/{pod_name}"] = {'cpu_usage': cpu_usage, 'mem_usage': mem_usage}
    
    return actual_resources

if __name__ == "__main__":
    
    requested_resources = get_requested_resources()
    
    actual_resources = get_actual_resources()

    with open('pod_resources_report.csv', 'w', newline='') as csvfile:
        fieldnames = ['Namespace', 'Pod', 'CPU_Request', 'Memory_Request', 'CPU_Usage', 'Memory_Usage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for key, value in requested_resources.items():
            namespace, pod_name = key.split('/')
            cpu_request = value['cpu_request']
            mem_request = value['mem_request']

            cpu_usage = 'N/A'
            mem_usage = 'N/A'

            if key in actual_resources:
                cpu_usage = actual_resources[key]['cpu_usage']
                mem_usage = actual_resources[key]['mem_usage']

            writer.writerow({
                'Namespace': namespace,
                'Pod': pod_name,
                'CPU_Request': cpu_request,
                'CPU_Usage': cpu_usage,
                'Memory_Request': mem_request,
                'Memory_Usage': mem_usage,
            })
