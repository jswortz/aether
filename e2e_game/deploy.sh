#!/bin/bash

# Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="aether-action-shooter"
REGION="us-central1"
IMAGE_TAG="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Starting Deployment for Aether Action Shooter..."

# Build the image using Cloud Build
echo "📦 Building Docker image..."
gcloud builds submit --tag ${IMAGE_TAG} .

# Deploy to Cloud Run
echo "🌍 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_TAG} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --port 8080

echo "✅ Deployment complete!"
gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)'
