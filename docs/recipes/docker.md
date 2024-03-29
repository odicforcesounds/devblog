#=====================================================================
Docker Playground
https://www.katacoda.com/courses/docker/playground
Play with Docker
https://labs.play-with-docker.com/
#=====================================================================
/var/lib/docker/volumes/ #docker volumes stored in Docker host filesystem
/var/lib/docker #Docker daemon directory on Linux.
C:\ProgramData\docker #Docker daemon directory on Windows.
#=====================================================================
#debug docker builds
#"RUN set -ex..." in Dockerfile

$ docker build -t temp .
Sending build context to Docker daemon    620kB
Step 1/3 : FROM sonarqube
 ---> a84a2ad61bb7
Step 2/3 : RUN date
 ---> Using cache
 ---> a3acfa4ab179
Step 3/3 : RUN check
 ---> Running in c294d0fc7992
/bin/sh: 1: check: not found

#The last successful step is 2,produced an image a3acfa4ab179,start a container
$ docker run -it a3acfa4ab179 bash 

#=====================================================================
#debug docker builds

Step 3/5 : RUN apt-get update -y &&     apt-get dist-upgrade -y &&     apt-get purge unattended-upgrades &&     apt-get clean all
 ---> Running in 384aeefae02a
Get:1 http://deb.debian.org/debian buster InRelease [122 kB]
Get:2 http://security.debian.org/debian-security buster/updates InRelease [65.4 kB]
Get:3 http://deb.debian.org/debian buster-updates InRelease [51.9 kB]
Get:4 http://deb.debian.org/debian buster/main amd64 Packages [7906 kB]
Get:5 http://security.debian.org/debian-security buster/updates/main amd64 Packages [314 kB]
Get:6 http://deb.debian.org/debian buster-updates/main amd64 Packages [8792 B]
Fetched 8468 kB in 3s (2680 kB/s)
Reading package lists...
Reading package lists...
Building dependency tree...
Reading state information...
Calculating upgrade...
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
Reading package lists...
Building dependency tree...
Reading state information...
Package 'unattended-upgrades' is not installed, so not removed
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
Removing intermediate container 384aeefae02a
 ---> cd5be5aac9ba
Step 4/5 : RUN apt-get update -y &&    apt-get install kmod -y &&    lsmod | grep freevxfs &&    echo $?
 ---> Running in fb78e6bfb823
 
#Removing intermediate container 384aeefae02a 
$ docker run -it 384aeefae02a
Unable to find image '384aeefae02a:latest' locally

  
$ docker run -it  cd5be5aac9ba                                                                                
root@d465dc1da450:/#

$ docker inspect -f '{{.Config.Entrypoint}}' cd5be5aac9ba # find image's entry point 

#debug exit status(exit code) 
$ docker run -it  cd5be5aac9ba /bin/sh -c "apt-get update -y && apt-get install kmod -y"
$ echo $?
$ docker container run busybox /bin/sh -c "exit 13"
$ echo $? #13

#inspect the state of an exited container
$ docker container inspect --format '{{.State.ExitCode}}' \
    $(docker container ls -lq)
$ docker container inspect --format '{{.State.ExitCode}}' containerid
#=====================================================================
#Docker Daemon logs
journalctl -xu docker.service
tail -f /var/log/messages | grep docker

#Send a HUP signal to the daemon to cause it to reload its configuration
kill -SIGHUP $(ps -aux | grep dockerd | grep -v grep | awk '{print $2}')
#f the daemon is unresponsive, force a full stack trace to be logged by sending a SIGUSR1 signal to the daemon
kill -SIGUSR1 $(ps -aux | grep dockerd | grep -v grep | awk '{print $2}')
#=====================================================================
#Run without the default seccomp profile
docker run --rm -it --security-opt seccomp=unconfined debian:jessie \
    unshare --map-root-user --user sh -c whoami
    
# explicitly specifies a policy
docker run --rm \
             -it \
             --security-opt seccomp=/path/to/seccomp/profile.json \
             hello-world    
#=====================================================================
#Check whether Docker is running
service docker status
systemctl is-active docker
docker info
ps -aux | grep dockerd #check in the process list for the dockerd process
#=====================================================================
problem:Got permission denied while trying to connect to the Docker daemon socket
fix:
sudo usermod -aG docker ${USER} #Add current logged in user to the docker group.
su -s ${USER} #log out and log back in so that group membership is re-evaluated 
docker run hello-world #verify to run docker commands without sudo.
#=====================================================================
docker search kali
# number of containers or images and in what state they are running 
#and hardware specifications like total memory allocated, speed of the processor, kernel version, etc
docker info 
#=====================================================================
problem:
debconf: unable to initialize frontend: Readline
fix:
#dockerfile
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections && \
    apt-get install -y kali-tools-top10
#=====================================================================
#ssh into docker container

docker run --name nginx-testing -d nginx 
docker ps #verify container is running
docker inspect -f "{{.NetworkSettings.IPAddress}}" nginx-testing # IP address of the container
docker exec -it nginx-testing /bin/bash #interactive shell to container

#within the running container
root@451c369e0482:/# apt-get update && apt-get -y install openssh-server && echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && /etc/init.d/ssh start && /etc/init.d/ssh status
root@451c369e0482:/# passwd #change password

#without logging to container, with default /bin/sh -c
$ docker exec nginx-testing /bin/sh -c "apt-get update && apt-get -y install openssh-server && echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && /etc/init.d/ssh start && /etc/init.d/ssh status"

ssh root@172.17.0.2

#=====================================================================
#image size
docker container ls -s
docker image ls
docker image history my_image:my_tag #the size of the intermediate images 
docker image inspect my_image:tag #the sizes of each layer
#=====================================================================
docker build --no-cache -t helloapp:v2 -f dockerfiles/Dockerfile context #Once the cache is invalidated, all subsequent Dockerfile commands generate new images and the cache is not used.
docker build --no-cache  #force rebuilding of layers already available,force the execution of each step/instruction in the Dockerfile
#=====================================================================
#The default CPU CFS (Completely Fair Scheduler) period is 100ms, usually --cpu-period should work with --cpu-quota
#By default, a container can use all available CPU resources, which corresponds to a --cpu-quota value of -1
docker run -it --cpu-quota=-1 ubuntu:20.04 /bin/bash
#If there is 1 CPU, this means the container can get 50% CPU worth of run-time every 50ms.
docker run -it --cpu-period=50000 --cpu-quota=25000 ubuntu:20.04 /bin/bash 
#If there is 1 CPU, As the default value of --cpu-period is 100000, setting the value of --cpu-quota to 25000 limits a container to 25% of the CPU resources
docker run -it --cpu-quota=25000 ubuntu:20.04 /bin/bash
#On a 2-CPU system `--cpus 1.5` means the container will take 75% (1.5/2) of the CPU share.
docker run -it --cpus 1.5 ubuntu:20.04 /bin/bash
#=====================================================================
docker create --name container_name image_name:tag #instantiate the container from the image
docker create --name app_redis_1 --expose 6379 redis:3.0.2
#=====================================================================
"docker build -t myimage:1.0 ."
#Run a container from the Alpine version 3.9 image, name the running container “web” and expose port 5000 externally, mapped to port 80 inside the container. 
"docker container run --name web -p 5000:80 alpine:3.9"
"docker container logs --tail 100 web" #Print the last 100  lines of a container’s logs 

docker container restart nagios

"docker container stop web" #Stop a running container through SIGTERM 
"docker container kill web" #Stop a running container through SIGKILL 

"docker pull myimage:1.0" #Pull an image from a registry  
"docker tag myimage:1.0 myrepo/myimage:2.0" #Retag a local image with a new image name and tag
"docker push myrepo/myimage:2.0" #Push an image to a registry
#=====================================================================
docker build -t ajeetraina:v1 --build-arg version=`uname -r` .
docker run ajeetraina:v1 env #Verify environmental variable

docker build -t nodejs-server-both1 --build-arg PORT_ARG=3090 -f Dockerfile.both .
docker build -t build-args-test --build-arg SECRET=12345 .
docker build . -t my-node-app --build-arg NODE_VERSION=8 --build-arg APP_DIR=/usr/src/app
#=====================================================================
#IF platform == arm64 FROM swiftarm/swift ELSE FROM swift:5.5.2

#! /usr/bin/env bash

platform=$(uname -p)

if [[ $platform == "arm64" ]]; then
    sed -i 's/FROM swift\:5\.5\.2/FROM swiftarm\/swift/' Dockerfile
fi
docker build 
#=====================================================================
docker stats --format "{{.Container}}: {{.CPUPerc}}"
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
docker stats #Verifying Resources Usage
docker run -m 512m --memory-reservation=256m --cpus=2 --cpu-shares=2000 web #container named as web
#=====================================================================
    Option 1: RUN export PYTHONPATH="$PYTHONPATH:/app"
    Option 2: ENV PYTHONPATH="$PYTHONPATH:/app"

docker run image env | grep PATH # see the PATH variables in the container 
docker run image env

docker run -t owasp/zap2docker-stable zap-baseline.py -t https://www.example.com
docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py \
    -t https://www.example.com -g gen.conf -r testreport.html
    
#=====================================================================
Best practices for writing Dockerfiles
https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

Dockerfile reference
https://docs.docker.com/engine/reference/builder/#usage
#=====================================================================

ls -l /usr/share/docker-ce/contrib/ ->  Create images from scratch, custom docker images  scripts
#=====================================================================
docker system df -v -> docker system df -v
                    SHARED SIZE is the amount of space that an image shares with another one (i.e. their common data)
                    UNIQUE SIZE is the amount of space that is only used by a given image
                    SIZE is the virtual size of the image, it is the sum of SHARED SIZE and UNIQUE SIZE


docker system prune #Remove Unused or Dangling Images, Containers, Volumes, and Networks
docker system prune -a #remove any stopped containers and all unused images (not just dangling images)
docker system prune -a -f #force auto confirm
docker system prune --volumes #prune volumes, simply add the --volumes
#=====================================================================		    
remove all untagged images
docker images | grep "none"
docker rmi -f $(docker images | grep "<none>" | awk "{print \$3}")

docker images
docker rmi $(docker images --filter "dangling=true" -q --no-trunc)
docker images -a | grep "pattern" | awk '{print $3}' | xargs docker rmi # find all the images that match a pattern,delete them by using awk to pass the IDs to docker rmi

$ docker image	        #list the most recently created images
docker images -a -> list images
$ docker images -f dangling=true


$ docker rmi $(docker images -q -f dangling=true)

$ docker rmi d65c4d6a3580 				#remove a single image
$ docker rmi 612866ff4869 e19e33310e49 abe0cd4b2ebc	#remove multiple images

docker image prune -a -f #remove all not associated with any container
docker image prune -a --filter "until=12h" -f # remove all images that are created more than 12 hours ago
docker image prune #interactively remove dangling images, Remove unused images

docker image ls -> Remove unused images
docker image rm nginx:xenial -> remove an image



#=====================================================================
#remove docker containers
$ docker rm 0fd99ee0cb61		#remove a single container
$ docker rm 0fd99ee0cb61 0fd99ee0cb61   #remove multiple containers
sudo docker ps -a | grep -v CONTAINER | awk '{print $1}' | xargs --no-run-if-empty sudo docker rm -f

docker ps
docker ps -a
docker rm $(docker ps -qa --no-trunc --filter "status=exited")

#stop and remove all containers
$ docker stop $(docker ps -a -q)	#stop all containers
$ sudo docker ps -a -q | xargs sudo docker stop

$ docker container prune		#interactively remove all stopped containers
$ docker rm $(docker ps -qa)

#remove all exited containers
docker rm $(docker ps -qa --filter "status=exited")
docker rm $(docker ps -a -f status=exited -q)

docker ps -l -> List containers
"docker ps --last 1" 
docker container kill -> Kill one or more running containers
docker container ls -> List containers (default shows just running)
docker container ls -a ->  Show all containers (default shows just running)
docker container ls -a --filter status=exited --filter status=created ->  list of all non-running (stopped) 
docker container ls -aq ->   list of all Docker containers

docker container prune -> Remove all stopped containers
docker container prune --filter "until=12h" -> remove all images that are created more than 12 hours ago
docker container prune --force --filter "until=2017-01-04T13:10:00"
docker container prune --force --filter "until=5m"

docker container stop CONTAINERID -> Stop container
docker container rm CONTAINERID -> Remove one or more containers

docker container stop $(docker container ls -aq) -> stop all running containers
docker container rm $(docker container ls -aq) -> Once all containers are stopped, remove all containers

docker container rename 9328ba729dfb initiator
docker container top CONTAINERID -> Display the running processes of a container
#=====================================================================
delete networks
docker network ls | grep "bridge"  
docker network rm $(docker network ls | grep "bridge" | awk '/ / { print $1 }')

docker network inspect NETWORK_ID #get container IP
docker network inspect NETWORK_NAME #get container IP
sudo docker network inspect $(sudo docker network ls | grep "kalilinux_cyberrange" | awk '/ / { print $2 }')
docker network inspect $(docker network ls | grep "bridge" | awk '/ / { print $1 }') #get network id of bridge

docker network ls -> List networks
docker network ls --no-trunc #display the full network id
docker network ls --filter driver=bridge
docker network create --driver overlay proxy
docker network ls -f "driver=overlay"
docker network create mynetwork #Run a detached container in a previously created container netwo
docker run --name mywildfly-net -d --net mynetwork \ -p 8080:8080 jboss/wildfly

#=====================================================================
#A none network doesn’t provide any networking capability to the container 
#which means the container is like a black box to the host

[vagrant@vg-centos-01 ~]$ docker run -it --init --net host alpine ash
/ #


#=====================================================================
#In contrast with the bridge network, a host network uses the host’s network, 
#containers are no longer isolated in a private network, do not receive a public IP address
#containers are virtually a service spawned on the host’s network which is why they consume the host’s ports

#the container use the host’s ports, the --publish or -p flag is meaningless

vagrant@vg-centos-01 ~]$ docker run -it --init --net host -p 8000:8000 thatisuday/express-example sh
Digest: sha256:16a130bfd804fa6bb82dd44750012579d2e8f86f4a270b05db33a5ba3b0a5025
Status: Downloaded newer image for thatisuday/express-example:latest
WARNING: Published ports are discarded when using host network mode
/app # hostname -i
127.0.1.1
/app #

[vagrant@vg-centos-01 ~]$ docker run -dit --name alpine1 --net host alpine ash

#=====================================================================
# change default docker0 brdige IP address

/etc/docker/daemon.json
{
  "bip": "192.168.1.1/24"
}

#Add --bip "192.168.1.1/24" at the end of line ExecStart=/usr/bin/dockerd. 
 /lib/systemd/system/docker.service
 
systemctl daemon-reload
systemctl start docker 

#=====================================================================
#the IP address of the gateway between the Docker host and bridge network listed
#Under the Containers key, each connected container is listed, along with information about its IP address
docker network inspect bridge 
ip addr show

#A container in the bridge network is like an isolated machine with its own public IP address 
#that can be used by other containers in the same network and the host for communication.
#All ports of the container remain hidden from the host 
#and the host would need to use http://<container-ip>:<port> URL for HTTP communication
#the host can use the --publish or -p flag to bind a local port with a port of the container 

[vagrant@vg-centos-01 ~]$ docker run -dit --name alpine1 alpine ash
[vagrant@vg-centos-01 ~]$ docker run -dit --name alpine2 alpine ash

[vagrant@vg-centos-01 ~]$ docker container ls
CONTAINER ID   IMAGE     COMMAND   CREATED          STATUS          PORTS     NAMES
869408d9d15d   alpine    "ash"     4 seconds ago    Up 4 seconds              alpine2
3ce781aa7f94   alpine    "ash"     14 seconds ago   Up 13 seconds             alpine1

# this network’s gateway is 192.168.1.1

[vagrant@vg-centos-01 ~]$ docker network inspect bridge
[
    {
        "Name": "bridge",
        "Id": "b1a455473413fe512aafd7c316e08e907cbcce70a02f78dfc0aead720c948f77",
        "Created": "2023-01-18T07:33:00.608553178Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": null,
            "Config": [
                {
                    "Subnet": "192.168.1.0/24",
                    "Gateway": "192.168.1.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {
            "3ce781aa7f94abb4d75c0de654813af6489ed430dc97b60987031a830c1b425f": {
                "Name": "alpine1",
                "EndpointID": "cb89da4ce280c7d56a6e98e9cc9c4e5cbce5108d2d619be5ed54838b3ab32531",
                "MacAddress": "02:42:c0:a8:01:02",
                "IPv4Address": "192.168.1.2/24",
                "IPv6Address": ""
            },
            "869408d9d15d2bf10d6b193fe3b650f8d8ba6bdedd457a331d4880cb9ad6d70b": {
                "Name": "alpine2",
                "EndpointID": "c80050944113845ab986bb82cc348358df659f5b119c39d7b0b74728170b0066",
                "MacAddress": "02:42:c0:a8:01:03",
                "IPv4Address": "192.168.1.3/24",
                "IPv6Address": ""
            }
        },
        "Options": {
            "com.docker.network.bridge.default_bridge": "true",
            "com.docker.network.bridge.enable_icc": "true",
            "com.docker.network.bridge.enable_ip_masquerade": "true",
            "com.docker.network.bridge.host_binding_ipv4": "0.0.0.0",
            "com.docker.network.bridge.name": "docker0",
            "com.docker.network.driver.mtu": "1500"
        },
        "Labels": {}
    }
]


#The first interface is the loopback device
#the second interface has the IP address 192.168.1.2

[vagrant@vg-centos-01 ~]$ docker attach alpine1
/ # ip addr show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
36: eth0@if37: <BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue state UP
    link/ether 02:42:c0:a8:01:02 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.2/24 brd 192.168.1.255 scope global eth0
       valid_lft forever preferred_lft forever

# make sure you can connect to the internet by pinging google.com

/ # ping -c 2 google.com
PING google.com (142.250.201.46): 56 data bytes
64 bytes from 142.250.201.46: seq=0 ttl=110 time=60.617 ms
64 bytes from 142.250.201.46: seq=1 ttl=110 time=60.809 ms

--- google.com ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 60.617/60.713/60.809 ms

#ping the second container

/ # ping -c 2 192.168.1.3
PING 192.168.1.3 (192.168.1.3): 56 data bytes
64 bytes from 192.168.1.3: seq=0 ttl=64 time=0.081 ms
64 bytes from 192.168.1.3: seq=1 ttl=64 time=0.116 ms

--- 192.168.1.3 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.081/0.098/0.116 ms

#kill -9 <PID>

[vagrant@vg-centos-01 ~]$ ps -ef | grep attach
vagrant    45981   39204  0 12:09 pts/0    00:00:00 docker container attach alpine1

#Docker containers have an interactive mode that lets you attach your terminal’s input and output streams to 
#the container’s process. Pressing Ctrl-C will usually terminate that process, causing the container to stop
#detach from a session without stopping the container.
#You’ll be dropped back into your shell but the previously attached process will remain alive, keeping your container runnin
#Pressing Ctrl-C or running the exit command will usually kill the container’s foreground process

#gracefully detach from a container
Press Ctrl-P, followed by Ctrl-Q

#Docker accepts detachKeys overrides on a per-container and per-attachment basis
#use Ctrl-d, followed by an underscore, to detach
docker attach my-container --detach-keys="Ctrl-d,_"

#=====================================================================
#user-defined bridge networks


[vagrant@vg-centos-01 ~]$ docker network create --driver bridge alpine-net
[vagrant@vg-centos-01 ~]$ docker network ls
NETWORK ID     NAME         DRIVER    SCOPE
e622785e3e33   alpine-net   bridge    local
b1a455473413   bridge       bridge    local

#start two alpine containers(alpine1,alpine2), but attach them to a user-defined network called alpine-net
#attach them to a user-defined network called alpine-net
#These containers(alpine1,alpine2) are not connected to the default bridge

 docker run -dit --name alpine1 --network alpine-net alpine ash
 docker run -dit --name alpine2 --network alpine-net alpine ash

#start a third alpine container(alpine3) which is connected to the bridge network but not connected to alpine-net
 
 docker run -dit --name alpine3 alpine ash

#start fourth alpine container(alpine4) which is connected to both networks

docker run -dit --name alpine4 --network alpine-net alpine ash
docker network connect bridge alpine4
 
#the default bridge network's gateway is 192.168.1.1
#Containers alpine3 and alpine4 are connected to the bridge network.

[vagrant@vg-centos-01 ~]$ docker network inspect bridge
[
    {
        "Name": "bridge",
        "Id": "b1a455473413fe512aafd7c316e08e907cbcce70a02f78dfc0aead720c948f77",
        "Created": "2023-01-18T07:33:00.608553178Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": null,
            "Config": [
                {
                    "Subnet": "192.168.1.0/24",
                    "Gateway": "192.168.1.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {
            "13fb7116c07da7128e7eb9420072c8488d4ca68648a9a534115158775a589a91": {
                "Name": "alpine4",
                "EndpointID": "c09ff7043a5fcd424d2c9eebb8388ab13bd3e8f5344829815976edbe85c2f770",
                "MacAddress": "02:42:c0:a8:01:02",
                "IPv4Address": "192.168.1.2/24",
                "IPv6Address": ""
            },
            "3de68e861590f12a422ec7eac1986dc52b3c5b583784b9d4b300442e03a462bb": {
                "Name": "alpine3",
                "EndpointID": "389b72ddad633b0816cc6d72f16ba43722235151acb4afbb002c1fdea65a5620",
                "MacAddress": "02:42:c0:a8:01:04",
                "IPv4Address": "192.168.1.4/24",
                "IPv6Address": ""
            }
        },
        "Options": {
            "com.docker.network.bridge.default_bridge": "true",
            "com.docker.network.bridge.enable_icc": "true",
            "com.docker.network.bridge.enable_ip_masquerade": "true",
            "com.docker.network.bridge.host_binding_ipv4": "0.0.0.0",
            "com.docker.network.bridge.name": "docker0",
            "com.docker.network.driver.mtu": "1500"
        },
        "Labels": {}
    }
]



#this network’s gateway is 172.18.0.1
#Containers alpine1, alpine2, and alpine4 are connected to the alpine-net network.

[vagrant@vg-centos-01 ~]$ docker network inspect alpine-net
[
    {
        "Name": "alpine-net",
        "Id": "e622785e3e33957ceae514d6785c8d2bad90aaa50e0e821b46eee278e68847c5",
        "Created": "2023-01-19T12:14:06.99702Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": {},
            "Config": [
                {
                    "Subnet": "172.18.0.0/16",
                    "Gateway": "172.18.0.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {
            "13fb7116c07da7128e7eb9420072c8488d4ca68648a9a534115158775a589a91": {
                "Name": "alpine4",
                "EndpointID": "7d1157c610d49892815e7cf70369fdd2478844511f5712ec23494a1bd32a4a78",
                "MacAddress": "02:42:ac:12:00:02",
                "IPv4Address": "172.18.0.2/16",
                "IPv6Address": ""
            },
            "7f4d7d1edf785a9c788fda95a6b92d0b13671c3c51e81dbc36fadf2efdb6fc92": {
                "Name": "alpine1",
                "EndpointID": "c83835550c33f30058bfe86aec3438460ba06fbca9f38dbb8c09a3f8dacb5ae8",
                "MacAddress": "02:42:ac:12:00:03",
                "IPv4Address": "172.18.0.3/16",
                "IPv6Address": ""
            },
            "e73dd2ac79d2ad68b3a078d605fb07988d92b3616b05f0d22a87cf0482cbed6b": {
                "Name": "alpine2",
                "EndpointID": "92244539b17e65c1d7a9332176c64feb86e6192666c777e4718175c38e088398",
                "MacAddress": "02:42:ac:12:00:04",
                "IPv4Address": "172.18.0.4/16",
                "IPv6Address": ""
            }
        },
        "Options": {},
        "Labels": {}
    }
]

#On user-defined networks like alpine-net, containers can also resolve a container name to an IP address
#This capability is called automatic service discovery

[vagrant@vg-centos-01 ~]$ docker container attach alpine1
/ # ping -c 2 alpine2
PING alpine2 (172.18.0.4): 56 data bytes
64 bytes from 172.18.0.4: seq=0 ttl=64 time=0.133 ms
64 bytes from 172.18.0.4: seq=1 ttl=64 time=0.129 ms

--- alpine2 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.129/0.131/0.133 ms

#From alpine1, you should not be able to connect to alpine3 at all, since it is not on the alpine-net network.

/ # ping -c 2 alpine3
ping: bad address 'alpine3'

#find alpine3’s IP address: 192.168.1.4 Try to ping it

/ # ping -c 2 192.168.1.4
PING 192.168.1.4 (192.168.1.4): 56 data bytes

--- 192.168.1.4 ping statistics ---
2 packets transmitted, 0 packets received, 100% packet loss

#alpine4 is connected to both the default bridge network and alpine-net, should be able to reach all of the other containers
#need to address alpine3 by its IP address

[vagrant@vg-centos-01 ~]$ docker container attach alpine4
/ # ping -c 2 alpine1
PING alpine1 (172.18.0.3): 56 data bytes
64 bytes from 172.18.0.3: seq=0 ttl=64 time=0.111 ms
64 bytes from 172.18.0.3: seq=1 ttl=64 time=0.145 ms

--- alpine1 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.111/0.128/0.145 ms
/ # ping -c 2 alpine2
PING alpine2 (172.18.0.4): 56 data bytes
64 bytes from 172.18.0.4: seq=0 ttl=64 time=0.125 ms
64 bytes from 172.18.0.4: seq=1 ttl=64 time=0.075 ms

--- alpine2 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.075/0.100/0.125 ms

#need to address alpine3 by its IP address

/ # ping -c 2 alpine3
ping: bad address 'alpine3'
/ # ping -c 2 192.168.1.4
PING 192.168.1.4 (192.168.1.4): 56 data bytes
64 bytes from 192.168.1.4: seq=0 ttl=64 time=0.117 ms
64 bytes from 192.168.1.4: seq=1 ttl=64 time=0.173 ms

--- 192.168.1.4 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.117/0.145/0.173 ms


/ # ping -c 2 alpine4
PING alpine4 (172.18.0.2): 56 data bytes
64 bytes from 172.18.0.2: seq=0 ttl=64 time=0.029 ms
64 bytes from 172.18.0.2: seq=1 ttl=64 time=0.129 ms

--- alpine4 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.029/0.079/0.129 ms
/ #

#make sure your containers can all connect to the internet by pinging google.com

/ # ping -c 2 google.com
PING google.com (142.250.201.46): 56 data bytes
64 bytes from 142.250.201.46: seq=0 ttl=110 time=61.115 ms
64 bytes from 142.250.201.46: seq=1 ttl=110 time=61.880 ms

--- google.com ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 61.115/61.497/61.880 ms
/ #

#Stop and remove all containers and the alpine-net network

[vagrant@vg-centos-01 ~]$ docker container stop alpine1 alpine2 alpine3 alpine4
alpine1
alpine2
alpine3
alpine4
[vagrant@vg-centos-01 ~]$ docker container rm alpine1 alpine2 alpine3 alpine4
alpine1
alpine2
alpine3
alpine4
[vagrant@vg-centos-01 ~]$ docker network rm alpine-net
alpine-net

#=====================================================================
#delete volumes
$ docker volume ls
$ docker volume rm volume_ID 	           #remove a single volume 
$ docker volume rm volume_ID1 volume_ID2   #remove multiple volumes

#remove dangling volumes
docker volume rm $(docker volume ls  -q --filter dangling=true)
docker volume rm $(docker volume ls -qf dangling=true)
docker volume ls -qf dangling=true | xargs -r docker volume rm
#remove all unused local volumes
docker volume prune	
#=====================================================================
docker version -> check version
docker load -> Load an image from a tar archive or STDIN
docker load -i xenial.tar ->  Read from tar archive file, instead of STDIN
sudo docker tag de915e2c17db dockerfuhrer/ubuntu-ansible:1.0
#=====================================================================
# first decide if you want to run the container in the background in a “detached” mode, -d=true or -d option
# or in the default foreground mode
# input/output with a detached container use network connections or shared volumes
# container is no longer listening to the command line where docker run was run

#Attach local terminal’s standard input, output, and error (or any combination of the three streams 
#to a running container’s ID or name.view its ongoing output or to control it interactively, 
#as though the commands were running directly in your terminal
docker run -d --name topdemo ubuntu /usr/bin/top -b
docker attach topdemo
echo $?
docker ps -a | grep topdemo

docker run -it -d --name testdebian5 debian
docker attach testdebian5
root@f7af9c6515d5:/# exit 13
$ echo $? #exitcode 13
#=====================================================================

# fails the detached container paradigm
# root process (service nginx start) returns and the detached container stops as designed
# the nginx service is started but could not be used
docker run -d -p 80:80 my_image service nginx start
docker run -d --name apache2-container -e TZ=UTC -p 8080:80 ubuntu/apache2:2.4-21.10_beta #http://localhost:8080

docker network create somenetwork #Create user defined network
docker run -d --name elasticsearch --net somenetwork -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:tag
#=====================================================================

# foreground mode
# the default when -d is not specified

# when running in detached mode (the most common -d option), designed to shut down immediately after the initial entry point command
# start the process in the container
# attach the console to the process’s standard input, output, and standard error
# pretend to be a TTY , stands for TeleTYpewriter.
docker run
CMD tail -f /dev/null


# keep container running in detached mode, run something in the foreground
# tail the /dev/null device as the CMD or ENTRYPOINT command of Docker image


sudo docker run --net=host --device=/dev/infiniband/uverbs0 --device=/dev/infiniband/rdma_cm  -t -i centos /bin/bash
sudo docker run -it --cap-add=IPC_LOCK --device=/dev/infiniband/uverbs1 --name=mnlx-verbs-nonprvlg mellanox/mofed421_docker:latest bash
    -i Keep STDIN open even if not attached.
    -t Allocate a pseudo-TTY.
    the default entrypoint /bin/sh -c, running /bin/bash
    exit immediately in daemon mode (-d). 
    If you want this container to run an interactive shell, use -it instead of -d.
docker run -it -d ubuntu:18.04 bin/bash

#-i” option, binding the standard input of the host to the standard input of the process running inside the container
docker exec -it CONTAINER_ID /bin/bash
docker exec -it CONTAINER_NAME bash
docker exec -it -u 0 CONTAINER_NAME whoami # run as root user
docker exec -ti container_name "command.sh" #run a command inside the container namespace
#Docker Exec Multiple Commands
sudo docker exec -it parrotsec-privacy nmap 192.168.35.10; ls
sudo docker exec parrotsec-privacy nmap 192.168.35.10; ls&&whoami
docker exec -w /var/log parrotsec-privacy cat lastlog  #execute a command within a specific directory inside the container
docker exec -e UID='root' parrotsec-privacy printenv UID #specify the environment variable name

# Ctrl+P+Q command to exit out of the container.
# the container still exists even after we exit from the container
sudo docker run –it centos /bin/bash

docker run -it --rm ubuntu:16.04 /bin/bash -> destroyed afterwards (use --rm )
docker run --rm -p 80:80 nginx:1.10 ->specific Nginx version

#privileged mode
sudo docker run -it --privileged --name=mnlx-verbs-prvlg mellanox/mofed421_docker:latest bash
#non privileged mode
docker run -it --cap-add=IPC_LOCK --device=/dev/infiniband/uverbs1 --name=my-verbs-nonprvlg myofed421image bash
#=====================================================================

#run locally container from existing image in non privileged mode
sudo docker run -i -t --cap-add=IPC_LOCK --device=/dev/infiniband/uverbs1 --device=/dev/zd0 --name=target-nonprvlg-zd0 myofed4212ubuntu16:1.0 /bin/bash
#=====================================================================

#Moving Images from Host to Host
docker ps -a -> Find the ID of the container that you would like to move
docker commit 02b0710b7f6b mynewimage -> Commit your changes and save the container to an image called mynewimage
docker save mynewimage > /tmp/mynewimage.tar -> Save the mynewimage image to a tar file
docker load < /tmp/mynewimage.tar -> Copy the mynewimage.tar file to your new Docker instance and load image tar

docker commit -m "commit message" -a "author" container_id username/imagename:tag #Modify the container from the inside and then commit the changes to the image

docker export -> saves a container’s running or paused instance to a file
docker save -> saves a non-running container image to a file

#docker save - Save is used to persist an image (not a container)
docker pull python:2.7.17-alpine3.9
docker save python:2.7.17-alpine3.9 > /path/to/save/my-python-container.tar
du -h my-python-container.tar 
docker load < my-python-container.tar #the target machine,load the image into the local registry
docker image list

docker save -o /home/sammy/your_image.tar your_image_name
ls -lah /home/sammy/your_image.tar
rsync -avz /home/sammy/your_image.tar username@remote_server_ip_address:destination_directory
docker load -i your_image.tar
docker images

tar xvf images.tar.gz -O | docker load

docker save imageID > /media/sf_docker_vm/archiveName.tar
docker load < /media/sf_docker_vm/archiveName.tar

docker save app:1.0 | gzip | DOCKER_HOST=ssh://user@remotehost docker load

docker save <docker image name> | gzip > <docker image name>.tar.gz
zcat <docker image name>.tar.gz | docker load

docker save -o docker-images.tar app-web
docker-machine scp ./docker-images.tar remote-machine:/home/ubuntu
docker-machine ssh remote-machine sudo docker load -i docker-images.tar

docker $(docker-machine config <mach1>) save <image> | pv | docker $(docker-machine config <mach2>) load #copy images between machines mach1 and mach2

docker save <image> | bzip2 | pv | ssh user@host 'bunzip2 | docker load' #Transferring a Docker image via SSH, bzipping the content on the fly
     
docker save <image> | (eval $(minikube docker-env) && docker load) #transfer images from local Docker to minikube VM

#docker export - Export is used to persist a container (not an image)
#The docker export command will not export the content of the volume, which is attached to the container.
#need to run an additional command to backup, restore or migrate the existing volume
docker pull alpine
docker run -it --detach --name alpine-t alpine #run the instance in detach mode so that the container doesn’t get destroyed when it exits
docker ps #get the container ID and name
docker export 35f34fabfa84 > alpine-t.tar #can use the container name as well; in our case, it is alpine-t
docker export --output="alpine-t.tar" 35f34fabfa84 #Alternatively
tar -c alpine-t.tar | docker import - alpine-t #Importing Docker Container
docker run --rm -it --name alpine-test alpine-t:[TAG]  #verify

docker export CONTAINER_ID > my_container.tar
"cat my_container.tar | docker import -"

sshfs user@ip:/<remote-path> <local-mount-path>

#==========================================bulk save/load===========================

#!/bin/bash
#save script

mkdir Docker_images
cd Docker_images
directory=`pwd`
c=0
#save the image names in 'list.txt'
doc= docker images | awk '{print $1}' > list.txt
printf "START \n"
input="$directory/list.txt"

while IFS= read -r line
do
     one=`echo $line | awk '{print $1}'`
     two=`echo $line | awk '{print $1}' | cut -c 1-3`
     if [ "$one" != "<none>" ]; then
             c=$((c+1))
             printf "\n $one \n $two \n"
             docker save -o $two$c'.tar' $one
             printf "docker image number $c successfully converted:   $two$c \n \n"
     fi
done < "$input"

#!/bin/bash
#load script

cd Docker_images/
directory=`pwd`
ls | grep tar > files.txt
c=0
printf "START \n"
input="$directory/files.txt"
while IFS= read -r line
do
     c=$((c+1))
     printf "$c) $line \n"
     docker load -i $line
     printf "$c) Successfully created docker image $line  \n \n"
done < "$input"

#=====================================================================
docker build -t imiell/bad-dockerfile --build-arg CURL_OPTIONS="..." ./ #via proxy
docker build -t imiell/bad-dockerfile ./ # no proxy
#=====================================================================

"sudo docker build -t ubuntu-ansible ."
"sudo docker build -t myofed4212ubuntu16:1.0 ." ->build image locally with a preferred tag name  from Dockerfile
docker build -t nginx:xenial /vagrant/dockerfiles/nginx -> build docker image based on Dockerfile (/vagrant/dockerfiles/nginx/Dockerfile)
"docker build -t nginx1:xenial --file Dockerfilenginx10 ." -> Different file name from Dockerfile

docker run -i -t xenial  /bin/bash -> run the image and install your application manually to figure out what is needed in the docker file
                                      Install,configure and test. When you are done build your dockerfile.

docker run trusty:latest cat /etc/lsb-release -> test docker image
docker run -p 80:80 --name nginx1.0 -d nginx:xenial -> container runs as a daemon in the background
#=====================================================================
docker events --since '2017-01-05' -> filter the output by an absolute timestamp or relative time on the host machine 
docker events --filter 'image=alpine' -> get real-time events from the server
#=====================================================================
docker history trusty:latest
#https://docs.docker.com/engine/reference/commandline/history/ CLI Format the output
docker history --human --format "{{.CreatedBy}}: {{.Size}}" devopscube/node-app-single:1.0
docker history --human --format "{{.ID}} {{.CreatedBy}}: {{.Size}}" devopscube/node-app-single:1.0

docker diff CONTAINERID ->Inspect changes to files or directories on a container’s filesystem

docker logs CONTAINERID -> Fetch the logs of a container
docker logs -f mywildfly #Follow the logs of a specific container

docker stats CONTAINERID -> Display a live stream of container(s) resource usage statistics

docker top nagios # processes of container nagios

docker port nagios # show all mapped ports of container nagi
#=====================================================================
docker run -it --rm quay.io/gluster/gluster-fedora
#=====================================================================
#registry dry-test
docker pull alpine
docker tag alpine localhost:5000/alpine
docker push localhost:5000/alpine
ls -1 docker/registry/v2/repositories/alpine/

#  private repositories
sudo docker run –d –p 5000:5000 –-name registry registry:2
# inspect command , section of "ExposedPorts" 
#=====================================================================
sudo docker pull jenkins
# The left-hand side of the port number mapping is the Docker host port to map to 
# and the right-hand side is the Docker container port number.
sudo docker run -p 8080:8080 -p 50000:50000 jenkins
#=====================================================================
docker tag go-demo localhost:5000/go-demo:1.0
docker push localhost:5000/go-demo:1.0

#=====================================================================
docker-machine create -d virtualbox go-demo -> outputs environment variables required for the local engine to find the server
docker-machine env go-demo -> the remote engine is inside the VM
docker-machine ls
eval $(docker-machine env node-1) -->set environment variables so that the local Docker Engine is pointing to the node-1
docker swarm init --advertise-addr $(docker-machine ip node-1) -->  --advertise-addr is the address that this node will expose to other nodes for internal communication

#setup swarm cluster
for i in 1 2 3; do
docker-machine create -d virtualbox --virtualbox-memory "1024" --virtualbox-disk-size "20000" --virtualbox-cpu-count "1" monnode-$i
done
eval $(docker-machine env monnode-1)
docker info
docker swarm init --advertise-addr $(docker-machine ip monnode-1)
TOKEN=$(docker swarm join-token -q worker)
for i in 2 3; do
eval $(docker-machine env monnode-$i)
docker swarm join --token $TOKEN --advertise-addr $(docker-machine ip monnode-$i) $(docker-machine ip monnode-1):2377
done
eval $(docker-machine env monnode-1)
docker node ls

#tokens
docker swarm join-token -q manager
docker swarm join-token -q worker

docker network create --driver overlay go-demo
docker network ls
docker service create --name go-demo-db --network go-demo mongo:3.2.10
docker service rm go-demo-db
docker service inspect go-demo-db
docker service inspect --pretty go-demo-db
docker service scale go-demo=5

#failover test
docker-machine rm -f node-3
docker service ps go-demo

docker service ls
docker-machine rm -f node-1 node-2

docker service create --name go-demo -e DB=go-demo-db --network go-demo --network proxy vfarcic/go-demo:1.0
docker service create --name util --network go-demo --mode global alpine sleep 1000000000
docker service ps util

#=====================================================================
#execute an interactive bash shell on the container

ID=$(docker ps -q --filter label=com.docker.swarm.service.name=util)
docker exec -it $ID apk add --update drill
docker exec -it $ID drill go-demo-db


#-i flag keeps input open to the container
#-t flag creates a pseudo-terminal that the shell can attach to.
docker exec -it container-name sh
docker exec -it $CONTAINERID bash

#=====================================================================
#execute non-interactive Command on the container.

docker exec container-name tail /var/log/date.log
docker exec -d $CONTAINERID touch test.txt
docker exec kib01 /bin/bash -c "curl http://localhost:5601"
#=====================================================================
docker build --no-cache --rm  -t kali:netsec . --file dockerfiles/Dockerfile.kalilinux  #name the container
docker run --name toolkali kali:netsec hping3 -v # run hping3 cmd via container name
docker run -p 127.0.0.1:8080:8080 -p 127.0.0.1:9090:9090 -e TZ=Europe/Amsterdam webgoat/goatandwolf
docker run --name container-name -it tleemcjr/metasploitable2:latest sh -c "/bin/services.sh && bash"
docker run --rm -ti --network host -v $PWD/work:/work parrotsec/core:lts-amd64 #Launch a container
docker run --rm -ti parrotsec/core #Start a container and automatically remove it on exit
on terminal 1 -> docker run --name pentest1 -ti parrotsec/security 
on terminal 2 -> docker run --name pentest2 -ti parrotsec/security 
on terminal 3 -> docker run --name msf-listener -ti parrotsec/tools-metasploit
#the first port is the port that will be opened on your host, and the second one is the container port to bind to.
docker run --rm -p 8080:80 -ti parrotsec/core 

docker run --rm -ti -v $PWD/work:/work parrotsec/core #Use Volumes to share files with the host
#Use Volumes to share files across multiple containers
on terminal 1 -> docker run --name pentest -ti -v $PWD/work:/work parrotsec/security 
on terminal 2 -> docker run --rm --network host -v $PWD/work:/work -ti parrotsec/security 
on terminal 3 -> docker run --rm -v $PWD/work:/work -ti parrotsec/tools-metasploit

docker run --name swaf -d --restart always pentest #Always restart the container if it stops
docker run -d --restart unless-stopped redis #Similar to always, except that when the container is stopped (manually or otherwise), it is not restarted even after Docker daemon restarts
#=====================================================================
#Mounting a Host Directory, contents can be accessible from both the host and from inside the container.

docker run -it --name <WHATEVER> -p <LOCAL_PORT>:<CONTAINER_PORT> -v <LOCAL_PATH>:<CONTAINER_PATH> -d <IMAGE>:<TAG>
docker run -t -i -v /root:/opt/root debian /bin/bash #mounts the host's /root directory into the Docker container at /opt/root
docker run -d --name some-container -v ${PWD}/folder:/var/folder ubuntu #mount a folder in current directory
#=====================================================================
#the -v vs --mount flag
#Bind mounts have limited functionality compared to volumes, a file or directory on the host machine is mounted into a container.
#Bind mounts are very performant, but they rely on the host machine’s filesystem having a specific directory structure available
#The file or directory is referenced by its absolute path on the host machine

#when you use a volume, a new directory is created within Docker’s storage directory on the host machine,Docker manages that directory’s contents.

#a case where you have a directory source and that when you build the source code, the artifacts are saved into another directory, 
#source/target/. You want the artifacts to be available to the container at /app/, and you want the container to get access
#to a new build each time you build the source on your development host. Use the following command to bind-mount the target/ 
#directory into your container at /app/. Run the command from within the source directory. 

#bind version, same result
docker run -d \
  -it \
  --name devtest \
  --mount type=bind,source="$(pwd)"/target,target=/app \
  nginx:latest

#volume version, same result
docker run -d \
  -it \
  --name broken-container \
  -v /tmp:/usr \
  nginx:latest

docker: Error response from daemon: oci runtime error: container_linux.go:262:
starting container process caused "exec: \"nginx\": executable file not found in $PATH".

docker inspect devtest #verify that the bind mount was created correctly. Look for the Mounts section

#read-only bind mount
docker run -d \
  -it \
  --name devtest \
  --mount type=bind,source="$(pwd)"/target,target=/app,readonly \
  nginx:latest

#read-only volume
docker run -d \
  -it \
  --name devtest \
  -v "$(pwd)"/target:/app:ro \
  nginx:latest
#=====================================================================
#run mysql script
docker exec -i mysql80 mysql -u root -pmypassword <mysql80.sql #password:mypassword, container:mysql80 
#=====================================================================
#foreground job
$ sudo docker build -t myhtop . --file=/vagrant/dockerfiles/DockerFile-htop
sudo docker run -it --rm --pid=host myhtop
sudo docker images
sudo docker ps
#=====================================================================
#background job
$ sudo docker build -t myhtop . --file=/vagrant/dockerfiles/DockerFile-htop
sudo docker run -it --pid=host myhtop
sudo docker images
sudo docker ps
#=====================================================================
#docker cp command
SRC_PATH does not end with /. (that is: slash followed by dot)
			the source directory is copied into this directory
		SRC_PATH does end with /. (that is: slash followed by dot)
			the content of the source directory is copied into this directory
# mycontainer is a container ID, not an image ID
docker cp foo.txt mycontainer:/foo.txt
docker cp mycontainer:/foo.txt foo.txt
- sudo docker cp "${PWD}/." "$(cat ${container_id})":/etc/ansible/roles/${role_name}
#=====================================================================	
#docker run is actually a sequence of two commands: "create" and "start".
#-i, --interactive=false Keep STDIN open even if not attached
#-t, --tty=false Allocate a pseudo-TTY
docker run -it debian:stable bash
#you can start it again
docker start 1329c99a831b
docker attach 1329c99a831b
#=====================================================================  
#Install from Docker hub
$ sudo docker pull centos
$ sudo docker run -i -t centos /bin/bash
# yum update
# yum install infiniband-diags

#=====================================================================
#Dockerfile
FROM ubuntu:16.04
RUN apt-get -yq update
RUN apt-get install -yq dnsutils curl netcat

#Usage
docker run -it --rm utils curl -I google.com
docker run -it --rm utils dig +short  google.com
docker run -it --rm utils nc -v google.com 80
#=====================================================================
# To disable setuid rights, add the following to the Dockerfile of your image
 RUN find / -perm +6000 -type f -exec chmod a-s {} \;\||true
 
 # add/remove capabilities with docker run/create 
 docker run --cap-drop=ALL --cap-add=CAP_NET_ADMIN
 # No capabilities
 docker run --user
 # Restricted capabilities with root
 docker run --cap-drop ALL --cap-add $CAP
#=====================================================================
$ docker --version
Docker version 19.03.2, build 6a30dfc
#=====================================================================
#Find the IP address of docker container
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' iperf-srv
$ docker inspect --format='{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq) | sed 's/ \// /'
/hello_world_web_1 - 172.17.0.3
/hello_world_redis_1 - 172.17.0.2
$ docker inspect 9db33d0960bc | grep IPAddress | grep -v null| cut -d '"' -f 4 | head -1
172.17.0.3
$ docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$@" hello_world_web_1
172.17.0.3
$ docker inspect hello_world_web_1 | grep IPAddress
$ docker inspect --format "{{ .NetworkSettings.IPAddress }}" 9db33d0960bc
172.17.0.3
$ docker inspect --format "{{ .NetworkSettings.IPAddress }}" hello_world_web_1
172.17.0.3
$ docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' hello_world_web_1
172.17.0.3

#find ENTRYPOINT & CMD on an image
docker inspect image_name/image_id # "Cmd": [ entries
docker inspect -f '{{.Config.Entrypoint}}' image_name/image_id
#=====================================================================
WINDOWS
#=====================================================================
docker run -it mcr.microsoft.com/windows/nanoserver:ltsc2022 cmd.exe # interactive session from the nanoserver
docker run -it mcr.microsoft.com/powershell

#run PowerShell in a container 
docker container exec -it <container-name/id> powershell
kubectl exec -it <pod-name> -n <namespace> -- powershell
kubectl exec -it k8s-xm-cm-pod -n sitecore powershell
#=====================================================================
#docker install script
$ hostnamectl
  Operating System: CentOS Linux 8
       CPE OS Name: cpe:/o:centos:centos:8
            Kernel: Linux 4.18.0-348.7.1.el8_5.x86_64
      Architecture: x86-64


$ cat docker.sh
#!/usr/bin/env bash

set -o errexit
# set -o pipefail #Illegal option -o pipefail
set -o nounset
set -o xtrace
# set -euo pipefail

yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine

# # Set up the repository
yum install -y yum-utils
yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# # Install Docker Engine
yum update -y
yum install \
    docker-ce \
    docker-ce-cli \
    containerd.io -y

systemctl start docker
systemctl is-active docker
# Configure Docker to start on boot
systemctl enable docker.service
systemctl enable containerd.service

docker --version
#both Client: Docker Engine and Server: Docker Engine
docker version

# Verify that you can run docker commands without sudo
docker run hello-world

reate the docker group
#groupadd: group 'docker' already exists
#groupadd docker

# Add your user to the docker group
usermod -aG docker $USER # by default run by root
id $USER
#=====================================================================
#docker install script

$ hostnamectl status
  Operating System: Ubuntu 16.04.7 LTS
            Kernel: Linux 4.4.0-210-generic
      Architecture: x86-64
      
vagrant@vg-ubuntu-04:~$ whoami
vagrant

vagrant@vg-ubuntu-04:~$ cat dockerinstall.sh
#!/bin/bash

#https://docs.docker.com/engine/install/ubuntu/

#Uninstall old versions
apt-get remove docker docker-engine docker.io containerd runc -qy

apt-get update -qy

#Set up the repository
apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

#Add Docker’s official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -qy


apt-get install docker-ce docker-ce-cli containerd.io -y

docker run hello-world

usermod -aG docker vagrant # by default run by root
id vagrant
#=====================================================================
#troubleshooting docker ubuntu image

problem:bash: ip: command not found
fix:apt-get update -y && apt-get install iproute2 -y

bash: vi: command not found
apt-get update -y && apt-get install vim -y
apt-get update -y && apt-get install nano -y
#=====================================================================
#copy files from docker container to host

docker cp [OPTIONS] CONTAINER:SRC_PATH DEST_PATH

docker create --name dummy IMAGE_NAME
docker cp dummy:/path/to/file /dest/to/file

docker cp containerId:/sourceFilePath/someFile.txt C:/localMachineDestinationFolder
#=====================================================================
#copy files from local host to docker container

docker cp [OPTIONS] SRC_PATH CONTAINER:DEST_PATH
docker cp C:/localMachineSourceFolder/someFile.txt containerId:/containerDestinationFolder
#=====================================================================