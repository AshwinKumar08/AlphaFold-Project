# Cron Job Setup

Two options are presented to run the `alfafoldrestserver` cron job: one uses a watcher script that calls [`runAlphafold.sh`](http://runAlphafold.sh) and the other uses SSH to access the host server to run `runAlphafold.sh` directly.

Both options will result in the same file output. Tasks are read from the database periodically. New enabled tasks will be logged and sent to AlphaFold. AlphaFold results and log are stored in a .zip file in the user’s directory in `/results` along with the container’s log.

## Prerequisites

1. AlphaFold is installed with files in`alphafold`.
2. `alfafoldrestserver` and `alphafold` are in the same root directory.

## Fasta Watcher Setup

1. `mkdir jobs`, or **make sure directory is empty.**
2. Set up directories for AlphaFold downloads and AlphaFold in `alfafoldrestserver/runAlphafold.sh`.
    
    ```sql
    # Preloaded databases for AlphaFold
    downloadDir=/home/alphafold/lib/download  # REPLACE IF NEEDED
    
    # Jump to the folder with the scipts
    cd /path/to/alphafold  # REPLACE
    ```
    
3. Use correct filename in `alfafoldrestserver/docker-compose.yml` command.
    
    ```sql
    backend:
    	command: python3 -u /app/backend_with_watcher.py
    ```
    
4. Run `docker compose up -d`.
5. Run `./fasta_watcher.sh`.

## SSH Setup

1. `mkdir jobs`, or **make sure directory is empty.**
2. Set up directories for AlphaFold downloads and AlphaFold in `alfafoldrestserver/runAlphafold.sh`.
    
    ```sql
    # Preloaded databases for AlphaFold
    downloadDir=/home/alphafold/lib/download  # REPLACE IF NEEDED
    
    # Jump to the folder with the scipts
    cd /path/to/alphafold  # REPLACE
    ```
    
3. Generate SSH keys for your user in `/alfafoldrestserver`.
    
    ```sql
    # in /alfafoldrestserver
    ssh-keygen -t ed25519 -f ./docker_host_key -N ""
    cat docker_host_key.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    chmod 644 ./docker_host_key
    ```
    
4. Mount SSH key to `alfafoldrestserver/docker-compose.yml`.
    
    ```sql
    backend:
    	volumes:
    		- ./docker_host_key:/ssh/id_ed25519:ro
    ```
    
5. Use correct filename in `alfafoldrestserver/docker-compose.yml` command.
    
    ```sql
    backend:
    	command: python3 -u /app/backend_with_ssh.py
    ```
    
6. Add user environment variable in `alfafoldrestserver/docker-compose.yml`.
    
    ```sql
    backend:
    	environment:
    		HOST_USER: REPLACE_THIS  # replace with your username if using SSH
    ```
    
7. Run `docker compose up -d`. You do not need to do the initial setup on your account again.
