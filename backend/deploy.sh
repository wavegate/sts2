#!/bin/bash
cd ~/myapp
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart myapp
echo "Deployed successfully"