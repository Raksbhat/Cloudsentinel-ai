
terraform {
  backend "s3" {
    bucket = "cloudsentinel-tfstate-923187443111"
    key    = "cloudsentinel/terraform.tfstate"
    region = "eu-north-1"
  }


  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}


provider "aws" {
  region = "eu-north-1"
}
resource "aws_dynamodb_table" "findings" {
  name         = "cloudsentinel-findings"
  billing_mode = "PAY_PER_REQUEST"


  hash_key = "finding_id"


  attribute {
    name = "finding_id"
    type = "S"
  }


  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }


  tags = {
    Project = "CloudSentinel"
  }
}
resource "aws_iam_role" "lambda_role" {
  name = "cloudsentinel-lambda-role"


  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}


resource "aws_iam_role_policy" "lambda_policy" {
  name = "cloudsentinel-lambda-policy"
  role = aws_iam_role.lambda_role.id


  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
  Effect = "Allow"
  Action = [
    "dynamodb:PutItem",
    "dynamodb:GetItem",
    "dynamodb:Scan",
    "dynamodb:UpdateItem"
  ]
  Resource = aws_dynamodb_table.findings.arn
},
      {
        Effect = "Allow"
        Action = [
          "guardduty:ListDetectors",
          "guardduty:ListFindings",
          "guardduty:GetFindings",
          "cloudtrail:LookupEvents",
          "securityhub:GetFindings"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "arn:aws:secretsmanager:eu-north-1:923187443111:secret:cloudsentinel/*"
       }
     ]
   })
 }


 resource "aws_lambda_function" "cloudsentinel_api" {
   filename      = "lambda.zip"
   function_name = "cloudsentinel-api"
   role          = aws_iam_role.lambda_role.arn
   handler       = "handler.handler"
   runtime       = "python3.11"
   timeout       = 30
   memory_size   = 256


   environment {
  variables = {
    ENV            = "production"
    FINDINGS_TABLE = aws_dynamodb_table.findings.name
  }
}
 }


 resource "aws_apigatewayv2_api" "cloudsentinel" {
   name          = "cloudsentinel-api"
   protocol_type = "HTTP"


   cors_configuration {
     allow_origins = ["*"]
     allow_methods = ["GET", "POST", "OPTIONS"]
     allow_headers = ["*"]
   }
 }


 resource "aws_apigatewayv2_integration" "lambda" {
   api_id                 = aws_apigatewayv2_api.cloudsentinel.id
   integration_type       = "AWS_PROXY"
   integration_uri        = aws_lambda_function.cloudsentinel_api.invoke_arn
   payload_format_version = "2.0"
 }


 resource "aws_apigatewayv2_route" "default" {
   api_id    = aws_apigatewayv2_api.cloudsentinel.id
   route_key = "$default"
   target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
 }


 resource "aws_apigatewayv2_stage" "prod" {
   api_id      = aws_apigatewayv2_api.cloudsentinel.id
   name        = "$default"
   auto_deploy = true
 }


 resource "aws_lambda_permission" "api_gateway" {
   statement_id  = "AllowAPIGateway"
   action        = "lambda:InvokeFunction"
   function_name = aws_lambda_function.cloudsentinel_api.function_name
   principal     = "apigateway.amazonaws.com"
   source_arn    = "${aws_apigatewayv2_api.cloudsentinel.execution_arn}/*/*"
 }


 output "api_url" {
   value = aws_apigatewayv2_stage.prod.invoke_url
 }



