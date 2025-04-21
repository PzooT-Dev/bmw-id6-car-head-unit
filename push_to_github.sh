#!/bin/bash

# This script helps push your BMW iD6 Car Head Unit code to GitHub
# Username PzooT-Dev is already configured

# Configure Git with the correct GitHub remote URL
git remote set-url origin "https://github.com/PzooT-Dev/bmw-id6-car-head-unit.git"

# Configure Git credentials helper to use the GitHub token
git config --global credential.helper store

# Push the code to GitHub
echo "Pushing code to GitHub repository: PzooT-Dev/bmw-id6-car-head-unit"
git push -u origin main

echo "Done! Your code is now on GitHub at: https://github.com/PzooT-Dev/bmw-id6-car-head-unit"