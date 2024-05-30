# Load Balancer (ALB)
resource "aws_lb" "alb" {
  name               = var.alb_name
  internal           = false # Set to true for internal ALB
  load_balancer_type = "application"
  enable_deletion_protection = false # Set to true to enable deletion protection

  security_groups = [aws_security_group.alb_security_group.id]
  # subnets         = [for subnet in aws_subnet.public : subnet.id]
  subnets         = [data.aws_subnet.subnet1.id, data.aws_subnet.subnet2.id]
  # subnets            = aws_subnet.my_subnets[*].id
}

# Target group for the ALB
resource "aws_lb_target_group" "alb_target_group" {
  name     = var.alb_target_group_name
  port     = 80
  protocol = "HTTP"
  target_type = "ip"
  vpc_id   = data.aws_vpc.default_vpc.id
}

# load balancer listener to forward traffic to the target group
resource "aws_lb_listener" "alb_listener" {
  load_balancer_arn = aws_lb.alb.arn
  port              = "80"
  protocol          = "HTTP"
  # port              = "443"
  # protocol          = "HTTPS"
  # ssl_policy        = "ELBSecurityPolicy-2016-08"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.alb_target_group.arn
  }
}
