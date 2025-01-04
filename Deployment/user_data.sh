#!/bin/bash

yum update -y   # For Amazon Linux or CentOS

# Ensure that pip is installed and is the latest version
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip

# Install git and clone files to the Web Server
yum install -y git
cd
git clone https://github.com/Jawad-Khizran/MemeGenerator

# Install and run Docker
yum install docker -y
yum install docker-compose-plugin -y
service docker start

cd MemeGenerator/App

docker-compose up