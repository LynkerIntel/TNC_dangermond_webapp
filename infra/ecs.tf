# ------------------------------------------------------------------------------
# ---- ECS Cluster -----
# ------------------------------------------------------------------------------

# ECS Cluster
resource "aws_ecs_cluster" "ecs_cluster" {
  name = var.ecs_cluster_name
}

# ------------------------------------------------------------------------------
# ---- ECS Task definition -----
# ------------------------------------------------------------------------------

# ECS Task Definition
resource "aws_ecs_task_definition" "ecs_task_definition" {
  family                   = var.ecs_task_definition_family_name 
  container_definitions    = jsonencode([
    {
      name      = var.ecs_container_name
      image     = data.aws_ecr_repository.app_ecr_repo.repository_url
      # image     = var.ecr_repo_url
      # image = "${var.ecr_repo_url}:${data.aws_ecr_image.repo_image.image_tags}"
      cpu       = 2048
      memory    = 6144
      portMappings = [
        {
          name          = var.ecs_container_port_mapping_name
          containerPort = 10000
          hostPort      = 10000
          # containerPort = var.ecs_container_port_mapping_port
          # hostPort      = var.ecs_container_port_mapping_port
          protocol      = "tcp"
          appProtocol   = "http"
        },
        {
          name          = var.ecs_host_port_mapping_name
          containerPort = 80
          hostPort      = 80
          # containerPort = var.ecs_host_port_mapping_port
          # hostPort      = var.ecs_host_port_mapping_port
          protocol      = "tcp"
          appProtocol   = "http"
        }
      ]
      essential = true
      environment = []
      mountPoints = []
      volumesFrom = []
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-create-group" = "true"
          "awslogs-group"        = var.ecs_log_group_name
          "awslogs-region"       = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
  task_role_arn       = aws_iam_role.ecs_task_role.arn
  execution_role_arn  = aws_iam_role.ecs_task_role.arn
  network_mode        = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu = "2048"
  memory = "6144"
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture = "X86_64"
  }
}

# # ECS Service
resource "aws_ecs_service" "ecs_service" {
  name            = var.ecs_service_name
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.ecs_task_definition.arn
  desired_count   = 1
  # iam_role        = aws_iam_role.ecs_task_role.arn
  # depends_on      = [aws_iam_role.ecs_task_role]
  # depends_on      = [aws_lb.nasa_dss_alb]
  depends_on      = [aws_lb_listener.alb_listener]
  launch_type     = "FARGATE"

  # ordered_placement_strategy {
  #   type  = "binpack"
  #   field = "cpu"
  # }

  # reference ALB target group 
  load_balancer {
    target_group_arn = aws_lb_target_group.alb_target_group.arn
    container_name   = var.ecs_container_name
    container_port   = 10000
  }

  # subnets associated with ECS service
  network_configuration {
    subnets  = [data.aws_subnet.subnet1.id, data.aws_subnet.subnet2.id]
    assign_public_ip = true
    # security_groups 
    security_groups = [aws_security_group.ecs_task_security_group.id]
  }

}