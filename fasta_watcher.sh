#!/bin/bash

echo "FASTA Watcher running..."

while true; do
    # get strictly the oldest .fasta file from /jobs
    find jobs -type f -name "*.fasta" ! -name "*.fasta.*" -printf "%T@ %p\n" | sort -n | cut -d' ' -f2- | while read -r fasta; do
        echo "Found new FASTA: $fasta"

        # check if args file exists for this fasta
        args_file="${fasta}.args"
        if [ ! -f "$args_file" ]; then
            echo "ERROR: Args file not found for $fasta, skipping..."
            continue
        fi

        read -r model_preset full_dbs models_to_relax enable_gpu_relax max_template_date < "$args_file"
        echo "Args for $fasta:"
        echo "  model_preset      = $model_preset"
        echo "  full_dbs          = $full_dbs"
        echo "  models_to_relax   = $models_to_relax"
        echo "  enable_gpu_relax  = $enable_gpu_relax"
        echo "  max_template_date = ${max_template_date:-None}"
        echo "Running AlphaFold for: $fasta"
        ./runAlphafold.sh "$fasta" "$model_preset" "$full_dbs" "$models_to_relax" "$enable_gpu_relax" "$max_template_date"
        echo "Finished AlphaFold for: $fasta"
    done

    # delete files marked for delection (with .deleteme ending)
    find jobs -name "*.deleteme" | while read -r path; do
        echo "Removing $path"
        rm -rf "$path"
    done

    sleep 10
done
