

# ----------------------------------------------------------------------------------------------------------------------
# ---- ECS Task execution role ----
# ----------------------------------------------------------------------------------------------------------------------


# ECS Task Role
resource "aws_iam_role" "ecs_task_role" {
  name = var.ecs_task_iam_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = ["ecs-tasks.amazonaws.com", "ecs.amazonaws.com", "ecr.amazonaws.com"]
        }
      }
    ]
  })

}

data "aws_iam_policy_document" "ecs_task_execution_iam_policy_doc" {
  statement {
    effect = "Allow"
    actions = [
      "s3:*",
      "s3-object-lambda:*",
    ]
    # resources = ["arn:aws:s3:::nasa-dss-bucket"]
    resources = ["*"]
    # resources = [aws_s3_bucket.nasa-dss-bucket.arn]
    # resources = [data.aws_s3_bucket.nasa-dss-bucket.arn]
  }

  statement {
    effect = "Allow"
    actions = [
      # "iam:ListEntitiesForPolicy",
      "ec2:AttachNetworkInterface",
      "ec2:CreateNetworkInterface",
      "ec2:CreateNetworkInterfacePermission",
      "ec2:DeleteNetworkInterface",
      "ec2:DeleteNetworkInterfacePermission",
      "ec2:Describe*",
      "ec2:DetachNetworkInterface",
      "elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
      "elasticloadbalancing:DeregisterTargets",
      "elasticloadbalancing:Describe*",
      "elasticloadbalancing:RegisterInstancesWithLoadBalancer",
      "elasticloadbalancing:RegisterTargets",
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams"
    ]
    resources = ["*"]
  }
}

# create
resource "aws_iam_policy" "ecs_task_execution_iam_policy" {
  name        = var.ecs_task_execution_policy_name
  description = "IAM Policy to attach to ECSTaskExecutionRole that allows ECS tasks to have permissions to access S3 and ECR"
  policy      = data.aws_iam_policy_document.ecs_task_execution_iam_policy_doc.json
}

resource "aws_iam_policy_attachment" "ecs_task_execution_iam_policy_attach" {
  name       = "ecs_task_execution_iam_policy_attach"
  roles      = [aws_iam_role.ecs_task_role.name]
  policy_arn = aws_iam_policy.ecs_task_execution_iam_policy.arn
}

# ----------------------------------------------------------------------------------------------------------------------
# ---- Github user IAM permissions ----
# Used for deploying terraform and new docker image to ECS via Github Actions
# ----------------------------------------------------------------------------------------------------------------------

variable "github_iam_user_name" {
  description = "Name of the IAM user for MROS webapp deployment via Github Actions"
  default     = "mros-webapp-github-actions-user"
}

# # IAM User for Github Actions to upload new Docker image to ECR 
# resource "aws_iam_user" "github_user" {
#   name = "github-actions-user"   
# }

data "aws_iam_user" "github_user" {
  user_name = var.github_iam_user_name
}

# # extra IAM permissions the github-user needs that are NOT covered by AWS managed policy ("arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess")
# data "aws_iam_policy_document" "github_user_iam_policy_doc" {

#   statement {
#     effect = "Allow"
#     actions = [
#       "ecs:UpdateService",
#       "ecs:DescribeServices",
#       "ecs:RegisterTaskDefinition",
#       "ecs:DescribeTaskDefinition",
#       "ecs:RegisterTaskDefinition",
#       "ecs:DeregisterTaskDefinition",
#       "ecs:DescribeTasks",
#       "ecs:RunTask",
#       "iam:PassRole",
#     ]
#     resources = ["*"]
#   }
# }

# # create
# resource "aws_iam_policy" "github_user_iam_policy" {
#   name        = "github-user-iam-policy"
#   description = "IAM Policy to attach to the GitHub Actions User (github-user) that allows for permissions to ECS"
#   policy      = data.aws_iam_policy_document.github_user_iam_policy_doc.json
# }

# # attach github-user with AWS managed policy ("arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess")
# resource "aws_iam_user_policy_attachment" "github_user_attach1" {
#   user       = aws_iam_user.github_user.name
#   policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
# }

# # attach github-user extra needed IAM permissions ("github_user_extra_iam_policy" block above)
# resource "aws_iam_user_policy_attachment" "github_user_attach2" {
#   user       = aws_iam_user.github_user.name
#   policy_arn = aws_iam_policy.github_user_iam_policy.arn
# }