# CodeBuild Webhook Setup Guide

This guide explains how to configure CodeBuild to be triggered directly by GitHub webhooks, eliminating the need for AWS credentials in GitHub Actions.

## Prerequisites

- AWS CodeBuild project: `wise-trader-delpoyement`
- GitHub repository access
- AWS Console access

## Step 1: Configure CodeBuild Source

1. Go to **AWS CodeBuild Console** → Your project (`wise-trader-delpoyement`)
2. Click **Edit** → **Source**
3. Select **Source provider**: `GitHub`
4. Choose one of the following authentication methods:

### Option A: GitHub OAuth (Recommended)
   - Click **Connect to GitHub**
   - Authorize AWS CodeBuild to access your GitHub account
   - Select your repository: `johnbekele/wise-trade-pulumi-deployment`
   - Select **Reference type**: `Branch`
   - Select **Branch**: `main` (or `master`)

### Option B: GitHub Personal Access Token
   - Create a GitHub Personal Access Token with `repo` scope
   - Store it in AWS Secrets Manager
   - Reference it in CodeBuild source configuration

## Step 2: Enable Webhook Triggers

1. In the CodeBuild project settings, go to **Edit** → **Source**
2. Under **Webhook**, check **Rebuild every time a code change is pushed to this repository**
3. Select the events that should trigger builds:
   - ✅ **PUSH** (triggers on push to branch)
   - ✅ **PULL_REQUEST** (optional, if you want PR builds)
4. For **Branch filter**, enter: `^main$|^master$` (or your branch pattern)
5. Save the configuration

## Step 3: Verify Webhook Configuration

1. After saving, AWS will create a webhook in your GitHub repository
2. Go to your GitHub repository → **Settings** → **Webhooks**
3. You should see a webhook pointing to CodeBuild
4. Test by pushing a commit to the `main` branch

## Step 4: Remove AWS Credentials from GitHub Secrets

Once the webhook is working, you can remove these secrets from GitHub:
- `AWS_ACCESS_KEY_ID` (no longer needed)
- `AWS_SECRET_ACCESS_KEY` (no longer needed)

**Keep these secrets** (still needed for other purposes if used):
- `AWS_ACCOUNT_ID` (if used elsewhere)
- `PULUMI_ACCESS_TOKEN`
- `DOCKER_HUB_TOKEN`
- `MONGO_URI`

## How It Works

1. **GitHub Push Event** → GitHub sends webhook to CodeBuild
2. **CodeBuild Receives Webhook** → Automatically starts build
3. **CodeBuild Environment Variables** (automatically available):
   - `CODEBUILD_SOURCE_VERSION` - Commit SHA
   - `CODEBUILD_SOURCE_REPO_URL` - Repository URL
   - `CODEBUILD_WEBHOOK_HEAD_REF` - Branch name
   - `CODEBUILD_WEBHOOK_EVENT` - Event type (PUSH, PULL_REQUEST, etc.)

## Troubleshooting

### Webhook not triggering builds
- Check GitHub webhook delivery logs in **Settings** → **Webhooks**
- Verify branch filter pattern matches your branch name
- Ensure webhook is enabled in CodeBuild project settings

### Build fails with authentication errors
- Verify GitHub connection in CodeBuild source settings
- If using PAT, ensure token has `repo` scope and is valid
- Check CodeBuild service role has necessary permissions

### Missing environment variables
- CodeBuild automatically provides GitHub context variables
- The `buildspec.yml` has been updated to use these variables
- Check build logs to see which variables are available

## Benefits

✅ **No AWS credentials in GitHub** - More secure  
✅ **Automatic triggering** - No GitHub Actions needed  
✅ **Built-in GitHub context** - CodeBuild provides commit/branch info  
✅ **Simpler setup** - One less moving part


