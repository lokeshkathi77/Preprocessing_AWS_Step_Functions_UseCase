# Demonstration Plan and Screenshot Checklist

This document is updated as each implementation task is completed. Screenshots
should show the AWS resource name, region, account context where appropriate,
and the relevant status or configuration. Do not capture credentials, tokens,
or sensitive transaction data.

## Evidence naming

Use this naming convention:

```text
task-<number>-<short-description>.<png|jpg>
```

Store screenshots outside the repository unless they contain no sensitive
information and are explicitly intended as project documentation.

## Task 1 - Repository foundation

Goal: establish GitHub as the version-controlled source of truth.

Screenshots:

- GitHub repository page showing the repository name and private visibility.
- Repository file tree showing the documentation and planned implementation
  directories.
- Commit history showing the foundation commit.

Expected evidence:

```text
GitHub repository
  -> versioned implementation plan
  -> configuration contract
```

## Task 2 - AWS deployment foundation

Goal: connect GitHub to AWS CodePipeline without storing AWS credentials in
GitHub.

Screenshots:

- AWS CodeConnections connection in `AVAILABLE` state.
- CodePipeline source configuration showing the connection and branch.
- IAM role trust policy and permission summary, with account-specific details
  redacted when necessary.
- Successful pipeline source-stage execution.

## Task 3 - Network stack

Goal: create the VPC, subnets, route tables, and security groups through
CloudFormation.

Screenshots:

- CloudFormation stack resources in `CREATE_COMPLETE`.
- VPC CIDR and subnet layout.
- Private subnet route table.
- EC2 and ECS security group rules.

## Task 4 - EC2 preprocessing resource

Goal: create and validate the preprocessing instance.

Screenshots:

- EC2 instance state, subnet, and security group.
- No public IPv4 address assigned.
- Systems Manager managed-node status, if enabled.
- CloudFormation output identifying the instance.

## Task 5 - ECS task definition

Goal: run a fixed, CloudFormation-created ECS task definition in private
subnets.

Screenshots:

- ECS cluster.
- Task definition revision and container configuration.
- ECR image tag or digest.
- ECS networking configuration with public IP disabled.
- CloudWatch log group and stream.

## Task 6 - Step Functions workflow

Goal: coordinate EC2 readiness and ECS task execution.

Screenshots:

- State machine definition overview.
- Successful execution graph.
- Execution input and output with sample values redacted if needed.
- Retry and failure paths in the definition.

## Task 7 - End-to-end processing

Goal: process one daily transaction file.

Screenshots:

- S3 object arrival or test input.
- Step Functions execution showing EC2 and ECS states.
- ECS stopped task with successful exit status.
- CloudWatch application logs.

## Task 8 - Failure, audit, and cleanup

Goal: prove recoverability and traceability.

Screenshots:

- EC2 stopped-instance recovery execution.
- ECS failure execution after retries.
- CloudWatch error log.
- CloudTrail event showing an infrastructure change.
- CloudFormation deletion or final clean stack state.

## Evidence chain

The final demonstration must be traceable from:

```text
GitHub commit
  -> CodeConnections source revision
  -> CodePipeline execution
  -> CloudFormation change set and stack events
  -> EC2/ECS resources
  -> Step Functions execution
  -> CloudWatch logs
  -> CloudTrail audit event
```
