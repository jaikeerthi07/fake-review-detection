# Deployment Guide: TrustLens

The best and easiest way to deploy this application is using **Vercel**.
Your project is already configured for it!

## Why Vercel?
1.  **Free Tier**: Generous limits for hobby projects.
2.  **Zero Config**: You already have a `vercel.json` file that correctly routes frontend and backend traffic.
3.  **Serverless**: No need to manage servers.

## Prerequisites
- A **GitHub** account.
- The project pushed to a GitHub repository.

## Steps to Deploy

### 1. Push to GitHub
If you haven't already, push your code to a new GitHub repository.
```bash
git init
git add .
git commit -m "Initial commit, ready for Vercel"
git branch -M main
# Add your remote origin here
# git remote add origin https://github.com/YOUR_USERNAME/fake-review-detection.git
git push -u origin main
```

### 2. Connect to Vercel
1.  Go to [Vercel.com](https://vercel.com) and Sign Up/Login with GitHub.
2.  Click **"Add New..."** -> **"Project"**.
3.  Import your `fake-review-detection` repository.

### 3. Configure Project
Vercel should auto-detect the settings from `vercel.json`.
-   **Framework Preset**: Other (or Vite)
-   **Root Directory**: `./` (Leave as default)
-   **Environment Variables**:
    -   Add `VERCEL=1` (This triggers the ephemeral file system adjustments in `app.py`).
    -   Add `APIFY_TOKEN` (If you have one).
    -   Add `JWT_SECRET_KEY` (Generate a random string).

### 4. Deploy
-   Click **Deploy**.
-   Wait for the build to finish (it might take a minute to install Python dependencies).

## Post-Deployment Checks
-   **Database**: The app uses a temporary SQLite DB in `/tmp`. User data (accounts for login) **will reset** when the server sleeps (inactivity). For a persistent app, consider connecting **Vercel Postgres** or **Supabase**.
-   **ML Models**: The first request (cold start) may take longer (5-10s) as serverless functions spin up and load `svm_pipeline.pkl`. If it hits the timeout limit (10s on free), consider moving the backend to **Render**.

## Alternative: Render (If Vercel Fails)
If the ML models are too large for Vercel (Error: `Serverless Function too large` > 250MB), use **Render**:
1.  Create a **Web Service** on [Render.com](https://render.com).
2.  Connect your repo.
3.  Runtime: **Python**.
4.  Build Command: `./build.sh` (make sure to `chmod +x build.sh`)
5.  Start Command: `gunicorn app:app`
6.  Environment Variables: `PYTHON_VERSION=3.9.0`.
