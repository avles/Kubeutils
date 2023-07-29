#!/bin/bash

# Check if the file exists
if [ ! -f "$1" ]; then
    echo "Please provide a valid file with node names"
    exit 1
fi

# Loop through each node in the file and run the kubectl drain command
while read -r node; do
    if [ ! -z "$node" ]; then  # Check if the node name is not empty
        echo "Draining node: $node"
        kubectl drain "$node" --ignore-daemonsets --delete-local-data
    fi
done < "$1"
