# AWS Transaction Processing Use Case

This repository demonstrates a GitHub-driven AWS transaction workflow:

```text
GitHub -> CodeConnections -> CodePipeline -> CodeBuild -> CloudFormation
       -> VPC, EC2, ECS, S3, Step Functions
```

The pipeline validates the Python processor, packages the nested
CloudFormation application template and preprocessing script, and deploys it
with the shared `InfrastructureDeploymentRole`. The EC2 step validates or
starts the preprocessing instance and runs `application/preprocess.py`
directly through Systems Manager. The ECS Fargate task reads the cleaned CSV
from S3 and writes a JSON summary to S3.

## Deployment

1. Create or authorize an AWS CodeConnections connection to the GitHub
   repository.
2. Deploy `infrastructure/pipeline/pipeline-root.yaml` once with the
   connection ARN, repository ID, and existing ECR image URI.
3. Push changes to `main`. CodePipeline runs tests, uploads the preprocessing
   script, packages nested templates, and deploys
   `infrastructure/application/application-root.yaml`.

The connection ARN, repository, image URI, network CIDRs, and sizing values
are parameters. No account IDs, regions, credentials, or resource IDs are
embedded in the repository.

## Application contract

The processor accepts CSV columns `transaction_id`, `amount`, and `currency`.
Missing or invalid records are reported in the JSON summary; valid records are
also included in the result. In S3 mode, set `INPUT_BUCKET`, `INPUT_KEY`,
`OUTPUT_BUCKET`, `TRANSACTION_DATE`, and `EXECUTION_ID`.

Start the state machine with an input similar to:

```json
{
  "bucket": "<input-bucket>",
  "key": "incoming/transactions.csv",
  "transactionDate": "2026-11-12",
  "executionId": "daily-001"
}
```

Step Functions validates or starts EC2, runs `application/preprocess.py`
through Systems Manager, uploads cleaned and rejected CSV files to the output
bucket, and then runs ECS against the cleaned CSV.

## Evidence

Record the GitHub revision, CodePipeline stages, CloudFormation stack events,
EC2 state, ECS task definition revision, Step Functions execution graph,
CloudWatch logs, and the generated S3 summary. Never capture credentials or
real transaction data.