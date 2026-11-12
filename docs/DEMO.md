# Demonstration and screenshot checklist

Do not capture credentials, access keys, session tokens, or real transaction
data. Use the `demo` environment and synthetic transaction files.

## Bootstrap

Capture:

- CodeConnection in `AVAILABLE` state
- CloudFormation bootstrap stack in `CREATE_COMPLETE`
- CodePipeline Source, Package, and Deploy stages
- Infrastructure deployment role trust policy

## Application deployment

Capture:

- GitHub commit and pipeline source revision
- CloudFormation change set
- CloudFormation nested stack resources
- VPC, private subnets, route tables, and security groups

## EC2 and ECS

Capture:

- EC2 running in a private subnet with no public IPv4
- Systems Manager managed-node status
- ECS task definition revision
- ECR image tagged with the GitHub source commit SHA
- ECS task network configuration with public IP disabled
- CloudWatch log group and task log stream

## Workflow

Start Step Functions with:

```json
{
  "instanceId": "<CloudFormation EC2 output>",
  "transactionFile": "s3://<transaction-bucket>/daily/transactions.csv"
}
```

Capture:

- Successful execution graph
- EC2 check/start state
- ECS `runTask.sync` state
- ECS stopped task and CloudWatch logs
- CloudTrail event for the infrastructure deployment

## Failure test

Stop the EC2 instance and rerun the workflow. Then use a test image that exits
non-zero and verify retries, failure history, and logs.
