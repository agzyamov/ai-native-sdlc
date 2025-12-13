resource "aws_dynamodb_table" "alert_history" {
  name           = "ProcessChangeAlerts"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "PartitionKey"
  range_key      = "SortKey"

  attribute {
    name = "PartitionKey"
    type = "S"
  }

  attribute {
    name = "SortKey"
    type = "S"
  }

  attribute {
    name = "EventTimestamp"
    type = "N"
  }

  global_secondary_index {
    name            = "EventTimestamp-index"
    hash_key        = "PartitionKey"
    range_key       = "EventTimestamp"
    projection_type = "ALL"
  }

  ttl {
    attribute_name = "TTL"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = {
    Name        = "ProcessChangeAlerts"
    Description = "Stores alert history for ADO process change monitoring"
  }
}

