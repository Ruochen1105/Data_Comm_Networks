docker network create mynetwork

cd AS && docker build -t as . && docker run -d --network mynetwork -p 53533:53533/udp --name as as
cd ../FS && docker build -t fs . && docker run -d --network mynetwork -p 9090:9090 --name fs fs
cd ../US && docker build -t us . && docker run -d --network mynetwork -p 8080:8080 --name us us
