# Configuration Contract

This project intentionally does not commit environment-specific identifiers.
Every value below must be supplied by an AWS-native configuration mechanism or
derived from CloudFormation.

## Values supplied at deployment time

| Value | Owner | Mechanism |
|---|---|---|
| AWS region | deployment environment | CodePipeline/CloudFormation parameter |
| environment name | deployment environment | CloudFormation parameter |
| GitHub repository and branch | CodeConnections | AWS connection configuration |
| artifact bucket | deployment foundation | CloudFormation output or parameter |
| transaction bucket | deployment foundation | CloudFormation output or parameter |
| ECR repository | deployment foundation | CloudFormation output |
| container image reference | build/deployment stage | CodeBuild output or parameter |
| VPC and subnet IDs | network stack | CloudFormation references |
| security group IDs | network stack | CloudFormation references |
| AMI ID | AWS Systems Manager public parameter | dynamic lookup |
| task definition ARN | ECS stack | CloudFormation output/reference |
| state machine ARN | Step Functions stack | CloudFormation output |

## Prohibited source values

Do not embed any of the following in templates, scripts, or documentation:

- AWS account IDs
- access keys, secret keys, or session tokens
- fixed regions
- fixed subnet, VPC, security group, instance, or task IDs
- manually allocated AMI IDs
- environment-specific bucket names
- credentials or transaction records

## Resolution rules

1. Use CloudFormation parameters only for values that must vary by deployment.
2. Use `Ref`, `Fn::GetAtt`, `Fn::Sub`, exports, and stack parameters to connect
   resources.
3. Resolve the current Amazon Linux AMI from an AWS Systems Manager public
   parameter rather than storing an AMI ID.
4. Generate globally unique names with CloudFormation stack values or omit
   names where AWS can generate them.
5. Pass runtime transaction locations as Step Functions execution input.

Any exception must be documented in the pull request and in this file.

## CloudFormation template boundaries

Each resource area has its own template. `main.yaml` is the root nested-stack
orchestration template and passes deployment parameters to child templates:

| Template | Responsibility |
|---|---|
| `bootstrap.yaml` | One-time CodePipeline, packaging, and deployment foundation |
| `main.yaml` | Root nested-stack orchestration |
| `network.yaml` | VPC, subnets, routes, and security groups |
| `ec2.yaml` | EC2 preprocessing resources |
| `ecs.yaml` | ECS cluster and task definition |
| `stepfunctions.yaml` | Step Functions state machine |
| `buildspec.yml` | AWS CodeBuild packaging of nested templates |

CodeBuild packages the separate child templates to S3 before CloudFormation
deploys the root template. This is required because nested-stack
`TemplateURL` values must resolve to S3 objects.
