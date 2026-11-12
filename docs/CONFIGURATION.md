# Configuration contract

Deployment-specific values are supplied at deployment time. They are never
embedded in templates or scripts.

| Parameter | Purpose |
|---|---|
| `EnvironmentName` | Environment tag and naming context |
| `VpcCidr` | VPC address range |
| `PrivateSubnetACidr` | Private subnet A range |
| `PrivateSubnetBCidr` | Private subnet B range |
| `ContainerImage` | ECS image URI, supplied by the deployment |
| `TransactionBucketName` | S3 bucket containing transaction files |
| `AvailabilityZoneA/B` | Optional AZ overrides; otherwise derived dynamically |

The AMI is resolved from the AWS Systems Manager public parameter
`/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64`.
Availability zones default to the first two AZs returned by CloudFormation.

The deployment role is the only infrastructure provisioning role required by
the use case. Runtime roles are separate service roles and are created by the
same CloudFormation deployment.

The pipeline creates an immutable ECR repository, builds `application/` with
AWS CodeBuild, pushes an image tagged with the source commit SHA, and passes
that image URI to the ECS stack through a CodePipeline variable.

The worker expects a CSV object with an `amount` column by default. The
optional `TRANSACTION_AMOUNT_COLUMN` environment variable can select a
different column without changing the container code.
