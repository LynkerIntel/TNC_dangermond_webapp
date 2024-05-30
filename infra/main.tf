# Created by: Angus Watters
# Created on: 2024-12-01

# Main Terraform file for the MROS Web app CI/CD Pipeline:
# - main.tf contains the terraform state S3 backend configuration

# The main.tf file declares the provider, backend, and local variables for the project.
# A skeleton of the required variables can be found in the variables_template.tf file
# The Terraform infrastructure is continually updated by a GitHub Actions workflow that 
# runs the Terraform code and applies any changes to the infrastructure as needed.

# ---------------------------------------------
# ---- Instantiate Terraform w/ S3 backend ----
# ---------------------------------------------

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      # version = "~> 4.0"
    }
  }
  backend "s3" {
    # bucket = "mros-webapp-tfstate-bucket"
    key    = "terraform.tfstate"
    # region = "us-west-1"
    # profile = "angus-lynker"
  }

}

# terraform {
#   required_providers {
#     aws = {
#       source  = "hashicorp/aws"
#       version = "~> 4.0"
#     }
#   }
# }

# provider "aws" {
#   region  = var.aws_region
#   profile = var.aws_profile
# }

# ---------------------------------------------
# ---- Specify provider (region + profile) ----
# ---------------------------------------------

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

# -------------------------
# ---- Local variables ----
# -------------------------
# - tag variable for naming resources by the project name ("mros")

locals {
    name_tag = "mros"
}