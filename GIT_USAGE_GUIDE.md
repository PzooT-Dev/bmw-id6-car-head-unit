# Git Usage Guide for BMW iD6 Car Head Unit Project

This guide explains how to use Git for version control and rollbacks in your BMW iD6 Car Head Unit project.

## Initial Setup

The repository has already been initialized and configured with:
- `.gitignore` for excluding unnecessary files
- `README.md` with project information
- Initial commit of the project

## Pushing to GitHub

To push your code to GitHub:

1. Run the provided script with your GitHub username:
   ```bash
   ./push_to_github.sh your_github_username
   ```

2. If you encounter authentication issues, ensure your GitHub token is correctly set:
   ```bash
   git config --global url."https://${GITHUB_TOKEN}:@github.com/".insteadOf "https://github.com/"
   ```

## Making Code Changes and Checkpoints

Follow these steps to make changes and create checkpoints:

1. Make changes to your code files
2. Stage the changes:
   ```bash
   git add .
   ```
3. Create a checkpoint (commit):
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to GitHub:
   ```bash
   git push origin main
   ```

## Rollbacks

If you need to roll back to a previous version:

1. View the commit history:
   ```bash
   git log --oneline
   ```

2. Temporarily go back to a specific commit (this doesn't change your repository):
   ```bash
   git checkout commit_hash
   ```

3. To permanently revert to a previous commit (this creates a new commit that undoes changes):
   ```bash
   git revert commit_hash
   ```

4. To force the repository back to an earlier state (USE WITH CAUTION - this rewrites history):
   ```bash
   git reset --hard commit_hash
   git push --force origin main
   ```

## Branching Strategy

For more complex changes, consider using branches:

1. Create a new branch:
   ```bash
   git checkout -b new-feature
   ```

2. Make changes, commit them, and push:
   ```bash
   git push origin new-feature
   ```

3. When ready, merge back to main:
   ```bash
   git checkout main
   git merge new-feature
   ```

## Best Practices

1. Create descriptive commit messages
2. Make small, focused commits
3. Create checkpoints before and after major changes
4. Regularly push to GitHub as backup
5. Use branches for experimental features
6. Don't commit sensitive information or large binary files