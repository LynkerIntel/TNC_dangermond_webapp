#!/bin/bash

TF_STATE_S3_BUCKET_NAME=$1

# ECR repo names 
ECR_REPO_NAME=$2

# AWS Account Number
AWS_ACCOUNT_NUMBER=$3

# AWS Profile, if not given, use "default"
AWS_PROFILE=${4:-"default"}

# AWS Region to create/check resources, if not given, use "us-west-1"
AWS_REGION=${5:-"us-west-1"}
LOCATION_CONSTRAINT=${AWS_REGION}

# Flag to determine whether to export variables to $GITHUB_ENV
RUNNING_ON_GITHUB_ACTION=${6:-"false"}

echo "- TF_STATE_S3_BUCKET_NAME: $TF_STATE_S3_BUCKET_NAME"
echo "- AWS_PROFILE: $AWS_PROFILE"
echo "- AWS_REGION: $AWS_REGION"
echo "- LOCATION_CONSTRAINT: $LOCATION_CONSTRAINT"
echo "- RUNNING_ON_GITHUB_ACTION: $RUNNING_ON_GITHUB_ACTION"

# Run the first script
. sh/create_tfstate_bucket.sh $TF_STATE_S3_BUCKET_NAME $AWS_ACCOUNT_NUMBER $AWS_PROFILE $AWS_REGION $RUNNING_ON_GITHUB_ACTION

# Run the second script
. sh/create_ecr_repo.sh $ECR_REPO_NAME $AWS_ACCOUNT_NUMBER $AWS_PROFILE $AWS_REGION $RUNNING_ON_GITHUB_ACTION

# Run the third script
. sh/export_env_vars.sh test-tag $RUNNING_ON_GITHUB_ACTION