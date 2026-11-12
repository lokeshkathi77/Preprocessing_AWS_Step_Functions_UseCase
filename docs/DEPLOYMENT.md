# Deployment runbook

The pipeline bootstrap is the only manual CloudFormation deployment. It
creates the artifact bucket, CodeBuild projects, CodePipeline, and the shared
`InfrastructureDeploymentRole`. Later infrastructure changes are deployed by
pushes to the configured GitHub branch.

## Prerequisites

- An AWS CodeConnections connection to the GitHub repository in `AVAILABLE`
  state.
- An existing ECR image URI for `application/Dockerfile`.
- CodeBuild Linux/Small capacity available in the AWS account.

## Bootstrap

Run from the repository root and supply values for the deployment context:

```bash
aws cloudformation deploy \
  --region "$AWS_REGION" \
  --stack-name "${ENVIRONMENT_NAME}-pipeline" \
  --template-file infrastructure/pipeline/pipeline-root.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    EnvironmentName="$ENVIRONMENT_NAME" \
    ConnectionArn="$CONNECTION_ARN" \
    FullRepositoryId="$GITHUB_REPOSITORY" \
    BranchName="$GITHUB_BRANCH" \
    ContainerImageUri="$CONTAINER_IMAGE_URI" \
    ApplicationStackName="$APPLICATION_STACK_NAME" \
    VpcCidr="$VPC_CIDR" \
    PublicSubnetACidr="$PUBLIC_SUBNET_A_CIDR" \
    PublicSubnetBCidr="$PUBLIC_SUBNET_B_CIDR" \
    Ec2InstanceType="$EC2_INSTANCE_TYPE" \
    EbsVolumeSize="$EBS_VOLUME_SIZE" \
    TaskCpu="$TASK_CPU" \
    TaskMemory="$TASK_MEMORY" \
    LogRetentionInDays="$LOG_RETENTION_IN_DAYS"
```

The command deliberately uses shell variables rather than account IDs,
regions, subnet IDs, bucket names, or image values embedded in source.

## Pipeline evidence

Capture the source revision, successful Validate and Package stages, the
CloudFormation Deploy stage, the deployment role passed to CloudFormation,
and the resulting application stack events. For a workflow execution, also
capture the Step Functions graph, EC2 state transition, ECS stopped task,
CloudWatch logs, and the generated S3 summary.
