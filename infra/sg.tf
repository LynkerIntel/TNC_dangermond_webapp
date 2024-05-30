# Security group for the ALB
resource "aws_security_group" "alb_security_group" {
  name        = var.alb_security_group_name
  description = "Security group for MROS app ALB"

  # Ingress rules
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }


}

# 
resource "aws_security_group" "ecs_task_security_group" {
  name        = var.ecs_task_security_group_name
  vpc_id      = data.aws_vpc.default_vpc.id

  ingress {
    protocol        = "tcp"
    from_port       = 10000
    to_port         = 10000
    security_groups = [aws_security_group.alb_security_group.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}
