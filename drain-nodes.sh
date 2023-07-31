#!/bin/bash

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "kubectl could not be found. Please install it first."
    exit 1
fi

# Check if the file exists
if [ ! -f "$1" ]; then
    echo "Please provide a valid file with kubernetes node names"
    # example: kubectl get nodes -o custom-columns=NAME:.metadata.name --no-headers > nodes.txt
    exit 1
fi

# functions

wait_for_drain() {
    local node="$1"
    while true; do
        # Get pods on the node
        local pods_on_node=$(kubectl get pods -o wide --field-selector spec.nodeName=$node)
        if [[ -z "$pods_on_node" ]]; then
            echo "Draining completed on node: $node"
            break
        else
            echo "Waiting for pods to be drained from node: $node ..."
            sleep 10
        fi
    done
}

node_exists() {
    local node="$1"
    kubectl get node "$node" &>/dev/null
    return $?
}

# Start the draining process

# Get the list of nodes from the text file
nodes=$(cat $1)

# Loop over each node
for node in $nodes; do

  # Check node existence
  if ! node_exists "$node"; then
      echo "Error: Node $node not found. Skipping..."
      continue
  fi

  # Check if the user wants to continue
  echo ""
  echo "Shall we drain the node: $node? (y/n)"
  read -r response

  #if [[ $response != "y" ]]; then
  if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        # Run the kubectl drain command
        echo "kubectl drain \"$node\" --ignore-daemonsets --delete-local-data"
        kubectl drain "$node" --ignore-daemonsets --delete-local-data
        # Wait for the node to be fully drained
        wait_for_drain "$node"
  else
        # Skip this node
        echo "Skipping node: $node"
  fi

done

echo "Draining completed."

