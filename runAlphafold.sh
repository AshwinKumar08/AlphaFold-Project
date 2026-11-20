#!/bin/bash
# expand links and move input file
fasta=`readlink -f $1`
inFile=${fasta}.working
mv $fasta $inFile

# Name of the folder for the reults
outDir=${fasta}.results
mkdir $outDir

# Name of the file for AlphaFold logs
logFile=${fasta}.log

# Preloaded databases for AlphaFold
downloadDir=/home/alphafold/lib/download

# Store current directory to restore it after computation
lastDir=`pwd`

# Jump to the folder with the scipts
cd tools

# Get additional arguments
model_preset="$2"
db_preset="$3"
models_to_relax="$4"
enable_gpu_relax="$5"
max_template_date="$6"

# Call AlphaFold
/usr/bin/python3 docker/run_docker.py --fasta_paths=$inFile --max_template_date=${max_template_date:-$(date '+%Y-%m-%d')} --model_preset=$model_preset --models_to_relax=$models_to_relax --data_dir=$downloadDir --use_gpu=True --enable_gpu_relax=$enable_gpu_relax --output_dir=$outDir > $logFile 2>&1

# Jump back to the previous directory
cd $lastDir

# Mark the input file as done.
mv $inFile ${fasta}.done
