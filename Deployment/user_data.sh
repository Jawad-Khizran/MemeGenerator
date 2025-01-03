#!/bin/bash

yum update -y   # For Amazon Linux or CentOS

# Install git and clone files to the Web Server
yum install -y git
cd
mkdir App
mkdir .aws
cd App
git clone https://github.com/Jawad-Khizran/MemeGenerator
cd ..

# Ensure that pip is installed and is the latest version
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip

# Install and run docker
cd App

yum install docker -y
service docker start

docker build -t meme-api .
docker run -p 5000:5000 meme-api