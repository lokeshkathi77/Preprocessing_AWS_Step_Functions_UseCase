# AWS Transaction Processing Demonstration

AWS-native transaction processing demonstration using CodePipeline, CodeConnections,
CloudFormation, EC2, ECS, S3, and Step Functions.

## Delivery approach

The repository is the source of truth for infrastructure and application changes.
AWS CodePipeline retrieves approved revisions through AWS CodeConnections and
deploys the stack with AWS CloudFormation. No AWS credentials or environment
identifiers are stored in this repository.

## Planned implementation

```text
GitHub
  -> AWS CodeConnections
  -> AWS CodePipeline
  -> AWS CloudFormation
  -> VPC, EC2, ECS, Step Functions
  -> S3 transaction file and CloudWatch audit logs
```

The implementation will be completed in independently verifiable tasks:

1. Repository foundation and configuration contract
2. AWS deployment foundation and CodePipeline connection
3. Network stack
4. EC2 preprocessing resource
5. ECS cluster, image, and task definition
6. Step Functions workflow
7. End-to-end transaction execution
8. Failure, audit, and cleanup demonstration

## Configuration policy

All deployment-specific values must be supplied through CloudFormation
parameters, CodePipeline/CodeBuild environment variables, or AWS Systems
Manager Parameter Store. Templates must use CloudFormation references and
outputs instead of account IDs, regions, subnet IDs, AMI IDs, bucket names,
repository names, or security group IDs embedded in source code.

The required configuration contract will be documented before the first AWS
resource is created.

## Documentation

- [Implementation plan and screenshot checklist](docs/DEMO.md)
- [Configuration contract](docs/CONFIGURATION.md)

## Status

Task 1 - repository foundation: complete.
Task 2 - deployment foundation template: complete.

The bootstrap template is deployed once by an AWS administrator. It creates
the artifact bucket, CodePipeline, and the infrastructure deployment role.
After the application stack exists, pipeline executions are started from the
AWS console or CLI using the configured source connection.
