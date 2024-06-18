#!/usr/bin/bash



sudo docker rmi betteryjs/checkip
sudo docker build -t 'checkip' .
sudo docker login
sudo docker tag checkip betteryjs/checkip
sudo docker push betteryjs/checkip
sudo docker save checkip > checkip.tar

# docker load < checkip.tar
# docker tag checkip betteryjs/checkip
# sudo docker run -d -p 5000:5000  --restart unless-stopped --name checkip betteryjs/checkip