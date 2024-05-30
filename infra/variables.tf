# # -------------------------------------------------------------------------------
# # ---- General provider variables ----
# # -------------------------------------------------------------------------------

# # AWS profile to use for AWS CLI.
# variable "aws_profile" {
#   description = "Profile to use for AWS CLI."
#   type        = string
#   default     = "angus-lynker"

# }

# # # AWS region to use for AWS CLI.
# variable "aws_account_number" {
#   description = "Account number."
#   type        = string
#   default     = "645515465214"
#   sensitive   = true
# }

# # # AWS region to use for AWS CLI.
# variable "aws_region" {
#   description = "Region to use for AWS CLI."
#   type        = string
#   default     = "us-west-1"
# }

# # -----------------------------------
# # ---- VPC variables ----
# # -----------------------------------

# # VPC ID.
# variable "vpc_id" {
#   description = "VPC ID."
#   type        = string
#   default     = "vpc-db49ecbd"
# }

# variable "subnet_id1" {
#   description = "Default subnet 1 ID."
#   type        = string
#   default     = "subnet-f928bc9f"
# }

# variable "subnet_id2" {
#   description = "Default subnet 2 ID."
#   type        = string
#   default     = "subnet-e348e8b9"
# }

# # ---------------------------------------------------------------
# # ------------- S3 Bucket variables ----------
# # ---------------------------------------------------------------

# variable "output_s3_bucket_name" {
#     description = "Name of the S3 bucket with the data used by the MROS app"
#     type        = string
#     default      = "mros-output-bucket"
#     sensitive   = true
# }

# # ---------------------------------------------------------------
# # ------------- ECR variables ----------
# # ---------------------------------------------------------------

# variable "ecr_repo_name" {
#     description = "Name of the ECR repo to store the Docker image."
#     type        = string
#     default     = "mroswebapp"
#     sensitive   = true
# }

# variable "ecr_repo_url" {
#     description = "URL of the ECR repo to store the Docker image"
#     type        = string
#     # default     = "mros-sqs-consumer-lambda-ecr"
#     # sensitive   = true
# }

# variable "ecr_image_tag" {
#     description = "Tag of the ECR repo to store the Docker image"
#     type        = string
#     default     = "latest"
#     # sensitive   = true
# }

# # ---------------------------------------------------------------
# # ------------- ECS IAM variables ----------
# # ---------------------------------------------------------------

# variable "ecs_task_iam_role_name" {
#   description = "The name of the IAM role to create for the ECS task"
#   type        = string
#   default     = "mros-ecs-task-role"
# }

# variable "ecs_task_execution_policy_name" {
#   description = "The name of the IAM role to create for the ECS task"
#   type        = string
#   default     = "mros-ecs-task-execution-policy"
# }

# # ---------------------------------------------------------------
# # ------------- ECS variables ----------
# # ---------------------------------------------------------------

# # ECS cluster name.
# variable "ecs_cluster_name" {
#   description = "Name of the ECS cluster"
#   default = "mros-ecs-cluster"
# }

# # ECS service name.
# variable "ecs_service_name" {
#   description = "Name of the ECS service" 
#   default = "mros-ecs-service"
# }

# variable "ecs_container_name" {
#   description = "Name of the container to associate with the load balancer"
#   type        = string
#   default = "mros-app-container"
# }

# variable "ecs_task_definition_family_name" {
#   description = "Name of the task definition family"
#   default = "mros-task-definition"
# }

# #  ECS container port name and number, this is the port that the container listens on.
# variable "ecs_container_port_mapping_name" {
#   description = "Name for the port mapping for ECS container"
#   default = "mros-container-10000-tcp"
# }

# variable "ecs_container_port_mapping_port" {
#   description = "Port mapping for ECS container"
#   default     = 10000
# }

# # ECS host port name and number, this is the port that the host listens on.
# variable "ecs_host_port_mapping_name" {
#   description = "Name for the port mapping for ECS host"
#   default = "mros-container-80-tcp"
# }

# variable "ecs_host_port_mapping_port" {
#   description = "Port mapping for ECS host"
#   default     = 80
# }

# # ECS log group name that gets created for the task.
# variable "ecs_log_group_name" {
#   description = "Name of the log group for the ECS task"
#   default = "/ecs/mros-task-definition"
# }

# # ---------------------------------------------------------------
# # ------------- Security group variables ----------
# # ---------------------------------------------------------------

# variable "alb_security_group_name" {
#   description = "Name of the security group for the ALB"
#   default     = "mros-alb-security-group"
# }

# variable "ecs_task_security_group_name" {
#   description = "Name of the security group for the MROS DSS task"
#   default     = "mros-task-security-group"
# }

# # ---------------------------------------------------------------
# # ------------- Load balancer (ALB) variables ----------
# # ---------------------------------------------------------------

# variable "alb_name" {
#   description = "The name of the load balancer"
#   type        = string
#   default = "mros-alb"
# }

# variable "alb_target_group_name" {
#   description = "The name of the target group"
#   type        = string
#   default = "mros-alb-target-group"
# }

# # ---------------------------------------------------------------------------------------------------------
# # ------------- Application specific variables (API keys, credential, etc.) ----------
# # ---------------------------------------------------------------------------------------------------------

# # Mapbox API key used by the application.
# variable "mapbox_api_key" {
#   description = "Mapbox API key"
#   type        = string
#   default     = "pk.eyJ1IjoiZG1yYWdhciIsImEiOiJjbG9nYXI0ZGYwdHB0MmlwZWFvNGh3NXVwIn0.ykWdWVZEY2fqNvsXcgFl3Q"
#   sensitive   = true
# }

# # # -------------------------------------------------------------------------------------------------------------------------------
# # # ------------------------------------------ S3 Bucket (TF State S3 bucket) variables -------------------------------------------
# # # ---- name of the S3 bucket that contains the S3 backend Terraform state files (exported from sh/build_static_resources.sh) ----
# # # -------------------------------------------------------------------------------------------------------------------------------

# # Terraform state file S3 bucket name
# variable "tfstate_s3_bucket_name" {
#     description = "Name of the S3 bucket to store the Terraform state files to use S3 as a terraform backend"
#     type        = string
#     # default     = "mros-webapp-tfstate-bucket"
# }

# # # # Terraform state file name
# # variable "tfstate_s3_object_key" {
# #     description = "Name of the S3 object key of the Terraform state files to use S3 as a terraform backend"
# #     type        = string
# #     default     = "terraform.tfstate"
# # }