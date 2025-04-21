#!/bin/bash

# This script helps push your BMW iD6 Car Head Unit code to GitHub
# Replace 'yourusername' with your actual GitHub username

# Check if GitHub username is provided
if [ -z "$1" ]; then
  echo "Usage: ./push_to_github.sh <your_github_username>"
  echo "Example: ./push_to_github.sh johndoe"
  exit 1
fi

# Configure Git with the correct GitHub remote URL
git remote set-url origin "https://github.com/$1/bmw-id6-car-head-unit.git"

# Configure Git credentials helper to use the GitHub token
git config --global credential.helper store

# Push the code to GitHub
echo "Pushing code to GitHub repository: $1/bmw-id6-car-head-unit"
git push -u origin main

echo "Done! Your code is now on GitHub at: https://github.com/$1/bmw-id6-car-head-unit"