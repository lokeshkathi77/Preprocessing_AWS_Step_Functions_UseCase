# Deployment runbook

The pipeline bootstrap is the only manual CloudFormation deployment. It
creates the artifact bucket, CodePipeline, and the shared
`InfrastructureDeploymentRole`. Later infrastructure changes are deployed by
pushes to the configured GitHub branch. CodePipeline deploys each application
CloudFormation template directly from the source artifact; CodeBuild is not
used.

## Prerequisites

- An AWS CodeConnections connection to the GitHub repository in `AVAILABLE`
  state.
- An existing ECR image URI for `application/Dockerfile`.
- The existing CodeConnections connection is in `AVAILABLE` state.

## Build the compatible ECS image

Run these commands from the repository root, not from the separate
`UseCase_AWS_Step_Functions/ecs_processor` directory:

```bash
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
export ECR_REPOSITORY="transaction-processor"
export IMAGE_TAG="processor-$(date +%Y%m%d%H%M%S)"
export CONTAINER_IMAGE_URI="${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"

aws ecr get-login-password --region "$AWS_REGION" |
  docker login --username AWS --password-stdin "$ECR_REGISTRY"

docker build \
  --file application/Dockerfile \
  --tag "$CONTAINER_IMAGE_URI" \
  application

docker push "$CONTAINER_IMAGE_URI"
```

This image runs `application/processor.py` with `RUN_MODE=s3`,
`INPUT_BUCKET`, `INPUT_KEY`, and `OUTPUT_BUCKET`.

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

Capture the source revision, successful Network, Storage, SecurityGroups, IAM,
EC2, ECSCluster, ECSTask, and StepFunctions stages, the deployment role passed
to CloudFormation, and the resulting application stack events. For a workflow execution, also
capture the Step Functions graph, EC2 state transition, ECS stopped task,
CloudWatch logs, and the generated S3 summary.

The Step Functions stack invokes the ECS task by its environment-specific task
family name rather than importing a task-definition ARN export. This allows
CloudFormation to create new ECS task-definition revisions without an export
update dependency.
