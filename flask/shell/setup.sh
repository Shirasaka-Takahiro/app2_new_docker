#!/bin/bash
TF_VERSION=1.3.7

cd /usr/local/src/
wget https://releases.hashicorp.com/terraform/"$TF_VERSION"/terraform_"$TF_VERSION"_linux_amd64.zip
unzip terraform_"$TF_VERSION"_linux_amd64.zip -d /usr/local/bin/

##Install aws-cli
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

##下記不要
##Install tfenv
#git clone https://github.com/tfutils/tfenv.git ~/.tfenv
#echo 'export PATH="$HOME/.tfenv/bin:$PATH"' >> ~/.bash_profile

## Reload bash_profile
#source ~/.bash_profile

##Install terraform
#/root/.tfenv/bin/tfenv install "$TF_VERSION"

##Use terraform
#/root/.tfenv/bin/tfenv use "$TF_VERSION"