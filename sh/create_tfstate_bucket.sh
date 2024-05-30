# !/bin/bash
# ----- NEW VERSION THAT DOES USE AWS PROFILE AS AN ARGUMENT -----
# - Create a Terraform state S3 bucket if one by the given name does NOT already exist.

# Provide following as arguments to script: 
# Terraform state S3 bucket name
# AWS Account Number
# AWS Profile, if not given, use "default"
# AWS region
# RUNNING_ON_GITHUB_ACTION
# Example: source sh/create_tfstate_bucket.sh 123456789 tfstate-s3-bucket-name aws-region "false"
# Example: source sh/create_tfstate_bucket.sh tfstate-s3-bucket-name 123456789 aws-profile aws-region "false"
# Terraform state S3 bucket name
TF_STATE_S3_BUCKET_NAME=$1

# AWS Account Number
AWS_ACCOUNT_NUMBER=$2

# AWS Profile, if not given, use "default"
AWS_PROFILE=${3:-"default"}

# AWS Region to create/check resources, if not given, use "us-west-1"
AWS_REGION=${4:-"us-west-1"}
LOCATION_CONSTRAINT=${AWS_REGION}

# Flag to determine whether to export variables to $GITHUB_ENV
RUNNING_ON_GITHUB_ACTION=${5:-"false"}

echo "- TF_STATE_S3_BUCKET_NAME: $TF_STATE_S3_BUCKET_NAME"
echo "- AWS_PROFILE: $AWS_PROFILE"
echo "- AWS_REGION: $AWS_REGION"
echo "- LOCATION_CONSTRAINT: $LOCATION_CONSTRAINT"
echo "- RUNNING_ON_GITHUB_ACTION: $RUNNING_ON_GITHUB_ACTION"

# -----------------------------------------------------------------------------------------------
# ----- Create S3 bucket to keep Terraform state files (if does NOT exist) -----
# -----------------------------------------------------------------------------------------------

# check if Terraform state S3 bucket ALREADY EXISTS
if ! aws s3api head-bucket --bucket "$TF_STATE_S3_BUCKET_NAME" --profile "$AWS_PROFILE" 2>/dev/null; then
    # Create the Terraform state S3 bucket if it DOESN'T exist
    aws s3api create-bucket --bucket "$TF_STATE_S3_BUCKET_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" --create-bucket-configuration LocationConstraint="$LOCATION_CONSTRAINT"
    
    echo "S3 bucket $TF_STATE_S3_BUCKET_NAME created."

    # Enable versioning on the bucket
    aws s3api put-bucket-versioning --bucket "$TF_STATE_S3_BUCKET_NAME" --region "$AWS_REGION" --profile "$AWS_PROFILE" --versioning-configuration Status=Enabled

else
    echo "Bucket $TF_STATE_S3_BUCKET_NAME already exists."
fi

# -----------------------------------------------------------------------------------------------
# ----- Export Terraform variables -----
# -----------------------------------------------------------------------------------------------

# Export ECR repo name as variable for Terraform
export TF_VAR_tfstate_s3_bucket_name="$TF_STATE_S3_BUCKET_NAME"

# Check if the script is running on GitHub Actions and the flag is set to true
if [[ "$RUNNING_ON_GITHUB_ACTION" == "true" ]]; then
    echo "Running on GitHub Actions, exporting environment variables to Github Env..."
    # Export the environment variables to $GITHUB_ENV
    echo "TF_VAR_tfstate_s3_bucket_name=$TF_STATE_S3_BUCKET_NAME" >> $GITHUB_ENV
    echo "Exported TF_VAR_tfstate_s3_bucket_name to Github Env"
fi
