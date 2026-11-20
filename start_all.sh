#!/bin/bash

echo "Starting Docker container..."
docker compose up -d

echo "Starting FASTA watcher..."
./fasta_watcher.sh
