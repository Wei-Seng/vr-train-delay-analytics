# --- EC2 Application Server ---

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
    cidr_blocks = ["0.0.0.0/0"] # ⚠️ Consider restricting to your IP for better security
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
resource "aws_instance" "app_server" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t2.micro" # Free-tier eligible

  vpc_security_group_ids = [aws_security_group.app_server_sg.id]
  subnet_id              = "subnet-0007934ef114611ed"

  # Attach the pre-existing LabRole via its instance profile
  iam_instance_profile = "LabInstanceProfile"

  # You must create a key pair named "vockey" in the EC2 console first
  key_name = "vockey"

  tags = {
    Name = "VR Train Analytics Server"
  }
}

# 1. SNS Topic for alerts (new resource)
resource "aws_sns_topic" "alerts" {
  name = "vr-trains-alerts"
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = "2401493@sit.singaporetech.edu.sg"  # Must confirm subscription
}

# 2. CloudWatch Alarm (new resource)
resource "aws_cloudwatch_metric_alarm" "ec2_cpu_high" {
  alarm_name          = "vr-trains-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Alert when CPU exceeds 80%"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    InstanceId = aws_instance.app_server.id
  }
}

# 4. Output the server's public IP address
output "app_server_public_ip" {
  description = "The public IP address of the application server"
  value       = aws_instance.app_server.public_ip
}