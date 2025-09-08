# AWS App Runner Deployment Guide

## Quick Deployment Steps

### 1. Pre-requisites
- AWS Account with proper permissions
- GitHub repository access
- Frontend deployed at: https://beerathon.streamlit.app/

### 2. Environment Variables to Set in App Runner

**Required Variables:**
```
AWS_REGION=us-east-1
CLANKER_ENVIRONMENT=production
CLANKER_DEBUG=false
CLANKER_HOST=0.0.0.0
CLANKER_PORT=8000
```

**AWS Credentials (if needed for services):**
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

**Optional Service Keys:**
```
OMDB_API_KEY=your_omdb_key
S3_BUCKET_NAME=your_bucket_name
S3_CSV_KEY=your_csv_key
```

### 3. Deploy to App Runner

1. **Go to AWS Console → App Runner**
2. **Create Service:**
   - Source: "Source code repository"
   - Repository: VedJoshi/AgenticBeerathon
   - Branch: mvp
   - Deployment trigger: Automatic

3. **Build Configuration:**
   - Configuration source: "Use configuration file"
   - Configuration file: apprunner.yaml

4. **Add Environment Variables** (from list above)

5. **Deploy** - Takes ~5-10 minutes

### 4. Update Frontend

After deployment, you'll get a URL like:
`https://your-service-name.us-east-1.awsapprunner.com`

**Update your Streamlit frontend** to use this URL instead of localhost:

```python
# Replace in your frontend code:
API_BASE_URL = "https://your-service-name.us-east-1.awsapprunner.com"

# API call example:
response = requests.post(
    f"{API_BASE_URL}/recommend-drink/",
    json={"movie_data": movie_data},
    headers={"Content-Type": "application/json"}
)
```

### 5. Test the Connection

Test endpoints:
- Health: `https://your-service-name.us-east-1.awsapprunner.com/health`
- API: `https://your-service-name.us-east-1.awsapprunner.com/recommend-drink/`

## Troubleshooting

- Check App Runner logs in AWS Console
- Verify environment variables are set correctly
- Ensure CORS is working (check browser console)
- Test API independently before connecting frontend

## Security Notes

- CORS is configured for your Streamlit domain
- Production mode disables debug endpoints
- Non-root user in Docker for security
