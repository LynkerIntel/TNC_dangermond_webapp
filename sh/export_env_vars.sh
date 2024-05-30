#!/bin/bash

# Export all of the environment variables needed for the Terraform configuration
# # Provide AWS Profile as an argument to the script, if not given, use "default"
# Provide ECR repo tag as an argument to the script, if not given, use "latest"
# Provide RUNNING_ON_GITHUB_ACTION as an argument to the script, if not given, use "false"
# Github Actions will provide Github SHA as ECR repo tag for the Docker image

# Example: source sh/export_env_vars.sh ecr-repo-tag false

# # AWS Profile, if not given, use "default"
# AWS_PROFILE=${1:-"default"}

# Provided ECR repo tag and if not given, use "latest"
ECR_REPO_TAG=${1:-"latest"}

# Flag to determine whether to export variables to $GITHUB_ENV
RUNNING_ON_GITHUB_ACTION=${2:-"false"}

# # Export the AWS profile as a Terraform variable
# export "TF_VAR_aws_profile"="$AWS_PROFILE"

# VPC variables
export "TF_VAR_vpc_id"="vpc-db49ecbd"
export "TF_VAR_subnet_id1"="subnet-f928bc9f"
export "TF_VAR_subnet_id2"="subnet-e348e8b9"

# Export S3 bucket containing MROS output data
export "TF_VAR_output_s3_bucket_name"="mros-output-bucket"

# Export ECR image tag as Terraform variable
export "TF_VAR_ecr_image_tag"="$ECR_REPO_TAG"

# IAM Roles/Policy names
export "TF_VAR_ecs_task_iam_role_name"="mros-ecs-task-role"
export "TF_VAR_ecs_task_execution_policy_name"="mros-ecs-task-execution-policy"

# ECS Cluster/Service/Task names
export "TF_VAR_ecs_cluster_name"="mros-ecs-cluster"
export "TF_VAR_ecs_service_name"="mros-ecs-service"
export "TF_VAR_ecs_container_name"="mros-app-container"
export "TF_VAR_ecs_task_definition_family_name"="mros-task-definition"
export "TF_VAR_ecs_container_port_mapping_name"="mros-container-10000-tcp"
export "TF_VAR_ecs_container_port_mapping_port"=10000
export "TF_VAR_ecs_host_port_mapping_name"="mros-container-80-tcp"
export "TF_VAR_ecs_host_port_mapping_port"=80
export "TF_VAR_ecs_log_group_name"="/ecs/mros-task-definition"

# ALB security group name
export "TF_VAR_alb_security_group_name"="mros-alb-security-group"

# ECS task security group name
export "TF_VAR_ecs_task_security_group_name"="mros-task-security-group"

# ALB name
export "TF_VAR_alb_name"="mros-alb"

# ALB target group name
export "TF_VAR_alb_target_group_name"="mros-alb-target-group"

# Check if the script is running on GitHub Actions (RUNNING_ON_GITHUB_ACTION=true), if so
# then export the environment variables to $GITHUB_ENV so they are made available to
# the next steps in the workflow
if [[ "$RUNNING_ON_GITHUB_ACTION" == "true" ]]; then

    echo "Running on GitHub Actions, exporting environment variables to Github Env..."

    # # Export the environment variables to $GITHUB_ENV
    # # AWS Profile
    # echo "TF_VAR_aws_profile=$AWS_PROFILE" >> $GITHUB_ENV

    # VPC variables
    echo "TF_VAR_vpc_id=vpc-db49ecbd" >> $GITHUB_ENV
    echo "TF_VAR_subnet_id1=subnet-f928bc9f" >> $GITHUB_ENV
    echo "TF_VAR_subnet_id2=subnet-e348e8b9" >> $GITHUB_ENV
    
    # S3 bucket containing MROS output data
    echo "TF_VAR_output_s3_bucket_name=mros-output-bucket" >> $GITHUB_ENV

    # ECR image tag
    echo "TF_VAR_ecr_image_tag=$ECR_REPO_TAG" >> $GITHUB_ENV

    # IAM Roles/Policy names
    echo "TF_VAR_ecs_task_iam_role_name=mros-ecs-task-role" >> $GITHUB_ENV
    echo "TF_VAR_ecs_task_execution_policy_name=mros-ecs-task-execution-policy" >> $GITHUB_ENV
    
    # ECS Cluster/Service/Task names
    echo "TF_VAR_ecs_cluster_name=mros-ecs-cluster" >> $GITHUB_ENV
    echo "TF_VAR_ecs_service_name=mros-ecs-service" >> $GITHUB_ENV
    echo "TF_VAR_ecs_container_name=mros-app-container" >> $GITHUB_ENV
    echo "TF_VAR_ecs_task_definition_family_name=mros-task-definition" >> $GITHUB_ENV
    echo "TF_VAR_ecs_container_port_mapping_name=mros-container-10000-tcp" >> $GITHUB_ENV
    echo "TF_VAR_ecs_container_port_mapping_port=10000" >> $GITHUB_ENV
    echo "TF_VAR_ecs_host_port_mapping_name=mros-container-80-tcp" >> $GITHUB_ENV
    echo "TF_VAR_ecs_host_port_mapping_port=80" >> $GITHUB_ENV
    echo "TF_VAR_ecs_log_group_name=/ecs/mros-task-definition" >> $GITHUB_ENV

    # ALB security group name
    echo "TF_VAR_alb_security_group_name=mros-alb-security-group" >> $GITHUB_ENV

    # ECS task security group name
    echo "TF_VAR_ecs_task_security_group_name=mros-task-security-group" >> $GITHUB_ENV

    # ALB name
    echo "TF_VAR_alb_name=mros-alb" >> $GITHUB_ENV

    # ALB target group name
    echo "TF_VAR_alb_target_group_name=mros-alb-target-group" >> $GITHUB_ENV


fi