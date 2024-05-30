#!/bin/bash
# ----- NEW VERSION THAT DOES USE AWS PROFILE AS AN ARGUMENT -----
# - Create a ECR repository if one by the given name does NOT already exist. 
# - Get the ECR repository URL and EXPORT it as a Terraform variable.

# Provide 
# AWS Account Number
# ECR repo name
# AWS region
# RUNNING_ON_GITHUB_ACTION Boolean flag whether being run from a github actions workflow
# Example: source sh/create_ecr_repo.sh ecr-repo-name 123456789 aws-profile aws-region false

# ECR repo names 
ECR_REPO_NAME=$1

# AWS Account Number
AWS_ACCOUNT_NUMBER=$2

# AWS Profile, if not given, use "default"
AWS_PROFILE=${3:-"default"}

# AWS Region to create/check resources, if not given, use "us-west-1"
AWS_REGION=${4:-"us-west-1"}
LOCATION_CONSTRAINT=${AWS_REGION}

# Flag to determine whether to export variables to $GITHUB_ENV
RUNNING_ON_GITHUB_ACTION=${5:-"false"}

echo "- ECR_REPO_NAME: $ECR_REPO_NAME"
echo "- AWS_REGION: $AWS_REGION"
echo "- LOCATION_CONSTRAINT: $LOCATION_CONSTRAINT"
echo "- RUNNING_ON_GITHUB_ACTION: $RUNNING_ON_GITHUB_ACTION"

# -----------------------------------------------------------------------------------------------
# ----- Create ECR repository for Lambda Docker images (if does NOT exist) -----
# -----------------------------------------------------------------------------------------------

# check if the ECR repository ALREADY EXISTS
if ! aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" 2>/dev/null; then
    # create the ECR repository if it DOESN'T exist
    aws ecr create-repository --repository-name "$ECR_REPO_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE"
    echo "ECR repository $ECR_REPO_NAME created."
else
    echo "ECR repository $ECR_REPO_NAME already exists."
fi

# Get the ECR repository URL
ECR_REPO_URL=$(aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" --query 'repositories[0].repositoryUri' --output text)

# export ECR repository name and URL as Terraform variables
export TF_VAR_ecr_repo_name="$ECR_REPO_NAME"
echo "Exported ECR repository name as Terraform variable named 'ecr_repo_name': $ECR_REPO_NAME"

export TF_VAR_ecr_repo_url="$ECR_REPO_URL"
echo "Exported ECR repository URL as Terraform variable named 'ecr_repo_url': $ECR_REPO_URL"

# Check if the script is running on GitHub Actions (RUNNING_ON_GITHUB_ACTION=true), if so
# then export the environment variables to $GITHUB_ENV so they are made available to 
# the next steps in the workflow
if [[ "$RUNNING_ON_GITHUB_ACTION" == "true" ]]; then
    # Export the environment variables to $GITHUB_ENV
    echo "TF_VAR_ecr_repo_name=$ECR_REPO_NAME" >> $GITHUB_ENV
    echo "Exported TF_VAR_ecr_repo_name to \$GITHUB_ENV"

    echo "TF_VAR_ecr_repo_url=$ECR_REPO_URL" >> $GITHUB_ENV
    echo "Exported TF_VAR_mros_ecr_repo_url to \$GITHUB_ENV"
fi

# -----------------------------------------------------------------------------------------------
# ----- Build and push Docker image to ECR Repo  -----
# -----------------------------------------------------------------------------------------------

# Determine the current operating system
OS=$(uname -s)

# print the operating system
echo "Operating system: $OS"cd 

# AWS CLI and Docker commands to login, build, tag, and push Docker image
aws ecr get-login-password --region "$AWS_REGION" --profile "$AWS_PROFILE" | docker login --username AWS --password-stdin $AWS_ACCOUNT_NUMBER.dkr.ecr.$AWS_REGION.amazonaws.com

# If the operating system is macOS, update the platform
if [ "$OS" = "Darwin" ]; then
  PLATFORM="linux/amd64"
  
  echo "Building Docker image with --platform $PLATFORM flag"

  # build Docker image
  docker build -t $ECR_REPO_NAME --platform $PLATFORM .
else
  echo "Building Docker image with no --platform flag"
  # For other operating systems, you can set a default platform or handle it as needed
  # Here, we're setting it to the default platform for Linux
  # build Docker image
    docker build -t $ECR_REPO_NAME .
fi

# tag Docker image
docker tag ${ECR_REPO_NAME}:latest $AWS_ACCOUNT_NUMBER.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO_NAME}:latest

# push Docker image to ECR repository
docker push $AWS_ACCOUNT_NUMBER.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO_NAME}:latest

# -----------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------
# ----- NEW VERSION THAT DOES NOT USE AWS PROFILE AS AN ARGUMENT -----
# -----------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------

# # - Create a ECR repository if one by the given name does NOT already exist. 
# # - Get the ECR repository URL and EXPORT it as a Terraform variable.

# # Provide 
# # AWS Account Number
# # ECR repo name
# # AWS region
# # RUNNING_ON_GITHUB_ACTION Boolean flag whether being run from a github actions workflow
# # Example: source sh/create_ecr_repo.sh 123456789 ecr-repo-name aws-region false

# # AWS Account Number
# AWS_ACCOUNT_NUMBER=$1

# # ECR repo names 
# ECR_REPO_NAME=$2

# # AWS Region to create/check resources, if not given, use "us-west-1"
# AWS_REGION=${3:-"us-west-1"}
# LOCATION_CONSTRAINT=${AWS_REGION}

# # # AWS Profile, if not given, use "default"
# # AWS_PROFILE=${4:-"default"}

# # Flag to determine whether to export variables to $GITHUB_ENV
# RUNNING_ON_GITHUB_ACTION=${4:-"false"}

# echo "- ECR_REPO_NAME: $ECR_REPO_NAME"
# echo "- AWS_REGION: $AWS_REGION"
# echo "- LOCATION_CONSTRAINT: $LOCATION_CONSTRAINT"
# echo "- RUNNING_ON_GITHUB_ACTION: $RUNNING_ON_GITHUB_ACTION"

# # -----------------------------------------------------------------------------------------------
# # ----- Create ECR repository for Lambda Docker images (if does NOT exist) -----
# # -----------------------------------------------------------------------------------------------

# # check if the ECR repository ALREADY EXISTS
# if ! aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" 2>/dev/null; then
#     # create the ECR repository if it DOESN'T exist
#     aws ecr create-repository --repository-name "$ECR_REPO_NAME" --region "$AWS_REGION"
#     echo "ECR repository $ECR_REPO_NAME created."
# else
#     echo "ECR repository $ECR_REPO_NAME already exists."
# fi

# # Get the ECR repository URL
# ECR_REPO_URL=$(aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" --query 'repositories[0].repositoryUri' --output text)

# # export ECR repository name and URL as Terraform variables
# export TF_VAR_ecr_repo_name="$ECR_REPO_NAME"
# echo "Exported ECR repository name as Terraform variable named 'ecr_repo_name': $ECR_REPO_NAME"

# export TF_VAR_ecr_repo_url="$ECR_REPO_URL"
# echo "Exported ECR repository URL as Terraform variable named 'ecr_repo_url': $ECR_REPO_URL"

# # Check if the script is running on GitHub Actions (RUNNING_ON_GITHUB_ACTION=true), if so
# # then export the environment variables to $GITHUB_ENV so they are made available to 
# # the next steps in the workflow
# if [[ "$RUNNING_ON_GITHUB_ACTION" == "true" ]]; then
#     # Export the environment variables to $GITHUB_ENV
#     echo "TF_VAR_ecr_repo_name=$ECR_REPO_NAME" >> $GITHUB_ENV
#     echo "Exported TF_VAR_ecr_repo_name to \$GITHUB_ENV"

#     echo "TF_VAR_ecr_repo_url=$ECR_REPO_URL" >> $GITHUB_ENV
#     echo "Exported TF_VAR_mros_ecr_repo_url to \$GITHUB_ENV"
# fi

# ----- OLD VERSION THAT TAKES IN AWS PROFILE AS AN ARGUMENT -----

# # - Create a ECR repository if one by the given name does NOT already exist. 
# # - Get the ECR repository URL and EXPORT it as a Terraform variable.

# # Provide 
# # AWS Account Number
# # ECR repo name
# # AWS region
# # AWS profile
# # RUNNING_ON_GITHUB_ACTION Boolean flag whether being run from a github actions workflow
# # Example: source sh/build_static_resources.sh 123456789 ecr-repo-name aws-region aws-profile false

# # AWS Account Number
# AWS_ACCOUNT_NUMBER=$1

# # ECR repo names 
# ECR_REPO_NAME=$2

# # AWS Region to create/check resources, if not given, use "us-west-1"
# AWS_REGION=${3:-"us-west-1"}
# LOCATION_CONSTRAINT=${AWS_REGION}

# # AWS Profile, if not given, use "default"
# AWS_PROFILE=${4:-"default"}

# # Flag to determine whether to export variables to $GITHUB_ENV
# RUNNING_ON_GITHUB_ACTION=${5:-"false"}

# echo "- ECR_REPO_NAME: $ECR_REPO_NAME"
# echo "- AWS_REGION: $AWS_REGION"
# echo "- LOCATION_CONSTRAINT: $LOCATION_CONSTRAINT"
# echo "- AWS_PROFILE: $AWS_PROFILE"
# echo "- RUNNING_ON_GITHUB_ACTION: $RUNNING_ON_GITHUB_ACTION"

# # -----------------------------------------------------------------------------------------------
# # ----- Create ECR repository for Lambda Docker images (if does NOT exist) -----
# # -----------------------------------------------------------------------------------------------

# # check if the ECR repository ALREADY EXISTS
# if ! aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" 2>/dev/null; then
#     # create the ECR repository if it DOESN'T exist
#     aws ecr create-repository --repository-name "$ECR_REPO_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE"
#     echo "ECR repository $ECR_REPO_NAME created."
# else
#     echo "ECR repository $ECR_REPO_NAME already exists."
# fi

# # Get the ECR repository URL
# ECR_REPO_URL=$(aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" --query 'repositories[0].repositoryUri' --output text)

# # export ECR repository URL as Terraform variable
# export TF_VAR_mros_ecr_repo_url="$ECR_REPO_URL"

# echo "ECR repository URL: $ECR_REPO_URL"

# # Check if the script is running on GitHub Actions (RUNNING_ON_GITHUB_ACTION=true), if so
# # then export the environment variables to $GITHUB_ENV so they are made available to 
# # the next steps in the workflow
# if [[ "$RUNNING_ON_GITHUB_ACTION" == "true" ]]; then
#     # Export the environment variables to $GITHUB_ENV
#     echo "TF_VAR_mros_ecr_repo_url=$ECR_REPO_URL" >> $GITHUB_ENV
#     echo "Exported TF_VAR_mros_ecr_repo_url to \$GITHUB_ENV"
# fi