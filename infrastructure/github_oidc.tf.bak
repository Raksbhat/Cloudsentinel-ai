resource "aws_iam_role" "github_actions_role" {
  name = "cloudsentinel-github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRoleWithWebIdentity"

        Principal = {
          Federated = "arn:aws:iam::923187443111:oidc-provider/token.actions.githubusercontent.com"
        }

        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }

          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:Raksbhat/Cloudsentinel-ai:ref:refs/heads/main"
          }
        }
      }
    ]
  })
}
resource "aws_iam_role_policy" "github_actions_policy" {
  name = "cloudsentinel-github-actions-policy"
  role = aws_iam_role.github_actions_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [

      {
        Sid    = "LambdaDeployment"
        Effect = "Allow"

        Action = [
          "lambda:GetFunction",
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration"
        ]

        Resource = "arn:aws:lambda:eu-north-1:923187443111:function:cloudsentinel-api"
      },

      {
        Sid    = "FrontendDeployment"
        Effect = "Allow"

        Action = [
          "s3:ListBucket"
        ]

        Resource = "arn:aws:s3:::cloudsentinel-ai-frontend-923187443111"
      },

      {
        Sid    = "FrontendObjects"
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]

        Resource = "arn:aws:s3:::cloudsentinel-ai-frontend-923187443111/*"
      },

      {
        Sid    = "ApiGatewayRead"
        Effect = "Allow"

        Action = [
          "apigateway:GET"
        ]

        Resource = "*"
      }
    ]
  })
}
