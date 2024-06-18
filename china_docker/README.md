
# 创建Docker Images
```shell

sudo docker rmi betteryjs/checkip
sudo docker build -t 'checkip' .
sudo docker login
sudo docker tag checkip betteryjs/checkip
sudo docker push betteryjs/checkip
sudo docker save checkip > checkip.tar


```

# 在服务器上导入Docker Images
```shell
docker load < checkip.tar
docker tag checkip betteryjs/checkip



```

# 在服务器上运行Docker Images

```shell

sudo docker run -d -p 5000:5000  --restart unless-stopped --name checkip betteryjs/checkip

```





