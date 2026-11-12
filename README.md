# AWS Transaction Processing Use Case

AWS-native demonstration for daily transaction-file processing:

```text
GitHub
  -> AWS CodeConnections
  -> AWS CodePipeline
  -> AWS CloudFormation
  -> VPC, EC2, ECS, Step Functions
```

The workflow validates an EC2 preprocessing instance and then runs a specific
ECS task definition. Infrastructure is split into separate CloudFormation
templates and deployed from GitHub.

## Implementation order

1. Deploy or update the one-time pipeline bootstrap.
2. Push the separate application stacks through GitHub.
3. Validate the network and IAM resources.
4. Validate the EC2 preprocessing instance.
5. Validate the ECS task definition and image.
6. Execute and audit the Step Functions workflow.

## Dynamic configuration

No AWS account IDs, regions, subnet IDs, security-group IDs, AMI IDs, bucket
names, or credentials are embedded in source. Deployment values are supplied
through CloudFormation parameters, CodePipeline configuration, AWS Systems
Manager public parameters, and CloudFormation references/outputs.

## Templates

| File | Responsibility |
|---|---|
| `cloudformation/bootstrap.yaml` | One-time CodePipeline foundation |
| `cloudformation/network.yaml` | VPC, subnets, routes, security groups |
| `cloudformation/iam.yaml` | Runtime roles and EC2 instance profile |
| `cloudformation/ec2.yaml` | Preprocessing EC2 instance |
| `cloudformation/ecs.yaml` | ECS cluster and task definition |
| `cloudformation/stepfunctions.yaml` | Orchestration state machine |
| `stepfunctions/transaction-workflow.asl.json` | State machine definition |

## IAM clarification

The bootstrap creates one `InfrastructureDeploymentRole`. CodePipeline passes
that role to CloudFormation, and CloudFormation uses it to create both the EC2
instance and ECS task definition. Service runtime roles remain separate because
EC2, ECS, and Step Functions require different trust policies.

The ECS task uses an AWS-provided AWS CLI image supplied as the
`ContainerImage` deployment parameter. No CodeBuild project or ECR build is
required.
