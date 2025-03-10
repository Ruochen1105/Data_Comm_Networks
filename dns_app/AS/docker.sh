docker build -t as .
docker run -it -p 53533:53533/udp --name as as
