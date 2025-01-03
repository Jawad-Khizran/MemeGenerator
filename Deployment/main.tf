provider "aws" {
  region = "us-west-2"
}

# Create a VPC
resource "aws_vpc" "project_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "Project VPC"
  }
}

# Create Public Subnet 1
resource "aws_subnet" "public_subnet_1" {
  vpc_id                  = aws_vpc.project_vpc.id
  cidr_block              = "10.0.0.0/24"
  availability_zone       = "us-west-2a"
  map_public_ip_on_launch = true
  tags = {
    Name = "Public Subnet 1"
  }
}

# Create Public Subnet 2 in another availability zone
resource "aws_subnet" "public_subnet_2" {
  vpc_id                  = aws_vpc.project_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-west-2b"
  map_public_ip_on_launch = true
  tags = {
    Name = "Public Subnet 2"
  }
}

# Create Private Subnet 1
resource "aws_subnet" "private_subnet_1" {
  vpc_id            = aws_vpc.project_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"
  tags = {
    Name = "Private Subnet 1"
  }
}

# Create Private Subnet 2 in another availability zone
resource "aws_subnet" "private_subnet_2" {
  vpc_id            = aws_vpc.project_vpc.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "us-west-2b"
  tags = {
    Name = "Private Subnet 2"
  }
}

# Create Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.project_vpc.id
  tags = {
    Name = "Public IGW"
  }
}

# Create Public Route Table
resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.project_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = {
    Name = "Public Route Table"
  }
}

# Associate Public Route Table with Public Subnet 1 and 2
resource "aws_route_table_association" "public_subnet_1_association" {
  subnet_id      = aws_subnet.public_subnet_1.id
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_route_table_association" "public_subnet_2_association" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.public_route_table.id
}

# Create Private Route Table
resource "aws_route_table" "private_route_table" {
  vpc_id = aws_vpc.project_vpc.id
  tags = {
    Name = "Private Route Table"
  }
}

# Associate Private Route Table with Private Subnet 1 and 2
resource "aws_route_table_association" "private_subnet_1_association" {
  subnet_id      = aws_subnet.private_subnet_1.id
  route_table_id = aws_route_table.private_route_table.id
}

resource "aws_route_table_association" "private_subnet_2_association" {
  subnet_id      = aws_subnet.private_subnet_2.id
  route_table_id = aws_route_table.private_route_table.id
}

variable "ingress_rules" {
  type = list(number)
  default = [22, 80, 5000, 27017]
}

# Create a Security Group
resource "aws_security_group" "web_server_sg" {
  vpc_id = aws_vpc.project_vpc.id
  name   = "Web Server Security"
  description = "Allow HTTP and SSH inbound"

  dynamic "ingress" {
    iterator = port
    for_each = var.ingress_rules
    content {
      from_port = port.value
      to_port = port.value
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0", "10.0.0.0/24"]
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Web Server"
  }
}

# Launch an EC2 instance
resource "aws_instance" "web_server_1" {
  ami = "ami-07d9cf938edb0739b"  # Amazon Linux 2023 AMI
  instance_type = "t3.medium"
  subnet_id = aws_subnet.public_subnet_1.id
  associate_public_ip_address = true
  security_groups = [aws_security_group.web_server_sg.id]

  user_data = file("user_data.sh")

  tags = {
    Name = "Web Server"
  }
}

# # # Create Elastic IP for NAT Gateway
# # resource "aws_eip" "nat_eip" {
# #   vpc = true
# # }
#
# # # Create NAT Gateway
# # resource "aws_nat_gateway" "nat_gw" {
# #   allocation_id = aws_eip.nat_eip.id
# #   subnet_id     = aws_subnet.public_subnet_1.id
# #   tags = {
# #     Name = "Public_subnet_NAT_Gateway"
# #   }
# # }
#
