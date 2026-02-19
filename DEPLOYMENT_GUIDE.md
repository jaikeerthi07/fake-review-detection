# Deployment Guide (Render)

This guide explains how to deploy your **Fake Review Detection** app to Render.com using the "Blueprint" feature. This is the easiest way to get your Backend, Frontend, and Database running together on a single platform.

## Prerequisites
- A **GitHub Account**.
- A **Render.com Account** (Sign up with GitHub).

## Step 1: Push Code to GitHub
Ensure all your latest changes (including `render.yaml` and `requirements.txt`) are pushed to your GitHub repository.

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 2: Create Blueprint on Render
1.  Go to your [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** and select **Blueprint**.
3.  Connect your GitHub repository (`fake-review-detection`).
4.  Render will automatically detect the `render.yaml` file.
5.  **Service Names**: You can leave them as default or rename them.
6.  **Apply**: Click **Apply Blueprint**.

## Step 3: Wait for Deployment
Render will now:
1.  Create a **PostgreSQL Database** (`reviews-db`).
2.  Build and Deploy the **Python Backend** (`fake-review-backend`).
3.  Build and Deploy the **React Frontend** (`fake-review-frontend`).

This process may take **5-10 minutes**.

## Step 4: Access Your Website
Once the deployment is complete:
1.  Find the **Frontend Service** in your Render Dashboard.
2.  Click the URL (e.g., `https://fake-review-frontend-xyz.onrender.com`).
3.  Your app is live!

## Troubleshooting
-   **Build Failures**: Check the "Logs" tab for the specific service that failed.
    -   If Backend fails: Ensure `requirements.txt` is correct and `gunicorn` is installed.
    -   If Frontend fails: Ensure `npm run build` works locally.
-   **Database Issues**: The app is configured to restart if the DB isn't ready, but if you see "Internal Server Error", check the Backend logs for DB connection errors.

## Important Note
-   **Free Tier Limitations**:
    -   The backend will "sleep" after 15 minutes of inactivity. The first request after sleep may take **30-60 seconds**.
    -   File uploads (CSVs) are **temporary** and will be deleted when the server restarts/sleeps.
    -   Database data (User accounts, Reviews) **IS PERSISTENT** and will be safe.
