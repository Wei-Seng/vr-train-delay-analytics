# Defines the EC2 application server

# 1. Find the latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# 2. Define a Security Group (virtual firewall)
resource "aws_security_group" "app_server_sg" {
  name        = "app-server-sg"
  description = "Allow SSH and Streamlit web traffic"

  ingress {
    description = "SSH access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # WARNING: Open to all IPs. Restrict to your IP for better security.
  }

  ingress {
    description = "Streamlit web traffic"
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Create the EC2 instance
resource "aws_ec2_instance" "app_server" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t2.micro" # Free-tier eligible

  vpc_security_group_ids = [aws_security_group.app_server_sg.id]
  
  # Attach the pre-existing LabRole via its instance profile
  iam_instance_profile = "LabInstanceProfile" # From your screenshot

  # IMPORTANT: You must create a key pair named "vockey" in the EC2 console first.
  key_name = "vockey"

  tags = {
    Name = "VR Train Analytics Server"
  }
}

# 4. Output the server's public IP address
output "app_server_public_ip" {
  description = "The public IP address of the application server"
  value       = aws_ec2_instance.app_server.public_ip
}
