#!/bin/bash
version=$1


docker build --no-cache -t convocal:latest .

docker stop convocal 
docker rm convocal_instance 

docker run --rm -dit -p 5000:5000 --name convocal_instance convocal:latest
    # sudo apt-get install jq
