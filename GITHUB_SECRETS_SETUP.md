# GitHub Secrets Configuration

To enable automated deployment via GitHub Actions, add these secrets to your repository:

## Frontend Deployment (Vercel)
Go to: Repository Settings → Secrets and variables → Actions

1. **VERCEL_TOKEN**
   - Get from: https://vercel.com/account/tokens
   - Create a new token for GitHub Actions

2. **VERCEL_ORG_ID** 
   ```
   team_xZwQ0LQg4sJPHGUfOrifWSym
   ```

3. **VERCEL_PROJECT_ID**
   ```
   prj_b6feiZgpRHqqHB9HZgyawhpGCAb7
   ```

## Backend Deployment (Render)

4. **RENDER_DEPLOY_HOOK_URL**
   - Go to your Render service dashboard
   - Navigate to Settings → Deploy Hook  
   - Copy the deploy hook URL

5. **BACKEND_URL** (for health checks)
   ```
   https://gamesai-backend-ninm.onrender.com
   ```

## How to Add Secrets:
1. Go to your GitHub repository
2. Click Settings (top menu)
3. Click "Secrets and variables" → "Actions" (left sidebar)
4. Click "New repository secret"
5. Add name and value
6. Click "Add secret"

## Testing the Workflow:
After adding secrets, push any change to trigger the CI/CD pipeline:
```bash
git add .
git commit -m "test: trigger CI/CD pipeline"
git push origin main
```