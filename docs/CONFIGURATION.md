# Configuration contract

Deployment-specific values are supplied at deployment time. They are never
embedded in templates or scripts.

| Parameter | Purpose |
|---|---|
| `EnvironmentName` | Environment tag and naming context |
| `VpcCidr` | VPC address range |
| `PublicSubnetCidr` | Public subnet range used only for the NAT gateway |
| `PrivateSubnetACidr` | Private subnet A range |
| `PrivateSubnetBCidr` | Private subnet B range |
| `ContainerImage` | AWS-provided or approved existing image URI |
| `TransactionBucketName` | S3 bucket containing transaction files |
| `AvailabilityZoneA/B` | Optional AZ overrides; otherwise derived dynamically |

The AMI is resolved from the AWS Systems Manager public parameter
`/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64`.
Availability zones default to the first two AZs returned by CloudFormation.

The deployment role is the only infrastructure provisioning role required by
the use case. Runtime roles are separate service roles and are created by the
same CloudFormation deployment.

The pipeline does not use CodeBuild. It passes the existing `ContainerImage`
parameter directly to the ECS stack.

The worker expects a CSV object with an `amount` column by default. The
optional `TRANSACTION_AMOUNT_COLUMN` environment variable can select a
different column without changing the container code.

The EC2 preprocessing step keeps every input row. Missing values use these
field-specific defaults:

| Field | Default |
|---|---|
| `transaction_id` | `UNKNOWN` |
| `customer_id` | `UNKNOWN` |
| `amount` | `0` |
| `currency` | `UNKNOWN` |
| `transaction_date` | `UNKNOWN` |

The normalized file is passed to ECS; no reject file is generated.

Private workloads use the NAT gateway for outbound access to SSM, S3, and the
public AWS-provided container image. EC2 and ECS do not receive public IPs.
