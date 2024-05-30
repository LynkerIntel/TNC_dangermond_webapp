# ----------------------------------------------------------------------------------------------------------------------
# ---- VPC and subnet data resources ----
# ----------------------------------------------------------------------------------------------------------------------

# # VPC Data Block
data "aws_vpc" "default_vpc" {
  id = var.vpc_id
}

# Default VPC subnet 1 data block
data "aws_subnet" "subnet1" {
  id = var.subnet_id1
}

# Default VPC subnet 2 data block
data "aws_subnet" "subnet2" {
  id = var.subnet_id2
}