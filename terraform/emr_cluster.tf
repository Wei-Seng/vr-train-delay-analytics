# Security Groups for EMR (base definitions without cyclic ingress rules)
resource "aws_security_group" "emr_master" {
  name        = "emr-master-sg"
  description = "Security group for EMR master node"
  # vpc_id      = aws_vpc.main.id  # Already commented out, assuming default VPC

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "emr-master-sg"
  }
}

resource "aws_security_group" "emr_core" {
  name        = "emr-core-sg"
  description = "Security group for EMR core nodes"
  # vpc_id      = aws_vpc.main.id  # Already commented out, assuming default VPC

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "emr-core-sg"
  }
}

# Separate ingress rules to avoid cycles
# Allow all traffic to master from core nodes
resource "aws_security_group_rule" "master_ingress_from_core" {
  type                     = "ingress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.emr_master.id
  source_security_group_id = aws_security_group.emr_core.id
}

# Allow SSH to master from anywhere (for debugging)
resource "aws_security_group_rule" "master_ssh" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  security_group_id = aws_security_group.emr_master.id
  cidr_blocks       = ["0.0.0.0/0"]
}

# Allow all traffic to core from master
resource "aws_security_group_rule" "core_ingress_from_master" {
  type                     = "ingress"
  from_port                = 0
  to_port                  = 0
  protocol                 = "-1"
  security_group_id        = aws_security_group.emr_core.id
  source_security_group_id = aws_security_group.emr_master.id
}

# Allow traffic to core from other core nodes (self-referential, no cycle)
resource "aws_security_group_rule" "core_self_ingress" {
  type              = "ingress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.emr_core.id
  self              = true
}

# EMR Cluster for Big Data Processing
resource "aws_emr_cluster" "train_analytics" {
  name          = "vr-trains-spark-cluster"
  release_label = "emr-6.15.0"  # Includes Hadoop 3.3.3, Spark 3.4.1
  applications  = ["Hadoop", "Spark"]
  
  service_role = "EMR_DefaultRole"  # Use existing Lab role
  
  ec2_attributes {
    instance_profile = "EMR_EC2_DefaultRole"
    subnet_id        = "subnet-0007934ef114611ed"
    emr_managed_master_security_group = aws_security_group.emr_master.id
    emr_managed_slave_security_group  = aws_security_group.emr_core.id  # Uses "slave" attribute (legacy), but references core resource
  }

  master_instance_group {
    instance_type  = "m5.xlarge"
    instance_count = 1
    # No bid_price = uses on-demand pricing
  }

  core_instance_group {
    instance_type  = "m5.xlarge"
    instance_count = 2  # 2 worker nodes for distributed processing
    # No bid_price = uses on-demand pricing
  }

  log_uri = "s3://${aws_s3_bucket.processed_data.id}/emr-logs/"

  configurations_json = <<EOF
[
  {
    "Classification": "spark",
    "Properties": {
      "maximizeResourceAllocation": "true"
    }
  }
]
EOF

  auto_termination_policy {
    idle_timeout = 3600  # Terminate after 1 hour idle (save costs)
  }

  tags = {
    Name = "VR Trains Big Data Cluster"
  }
}

# Output cluster ID
output "emr_cluster_id" {
  value       = aws_emr_cluster.train_analytics.id
  description = "EMR cluster ID for job submission"
}

# Upload Spark job script to S3
#resource "aws_s3_object" "spark_job" {
#  bucket = aws_s3_bucket.processed_data.id
#  key    = "scripts/spark_processor.py"
#  source = "${path.module}/../src/spark_processor.py"
#}