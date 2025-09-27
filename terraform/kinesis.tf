# This Terraform file defines the AWS Kinesis Data Stream.
# It acts as a durable, scalable buffer for our real-time events.
resource "aws_kinesis_stream" "realtime_trains" {
  # This name must match the STREAM_NAME used in the producer and consumer.
  name = "vr-realtime-train-stream"

  # A shard is like a lane on the highway. For this project, one is enough.
  shard_count = 1

  # How long Kinesis should remember the data (24 hours is default and fine).
  retention_period = 24

  tags = {
    Name      = "VR Realtime Stream"
    ManagedBy = "Terraform"
    Owner     = "Person B"
  }
}
