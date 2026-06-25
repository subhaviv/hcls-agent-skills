"""Pre-flight credential validation for the eval suite."""
import boto3
from botocore.exceptions import BotoCoreError, ClientError


class PreflightError(Exception):
    """Raised when credential pre-flight checks fail."""


def validate_credentials(model_id: str | None = None) -> dict:
    """Validate AWS credentials before eval execution.

    Checks:
    1. sts:GetCallerIdentity — confirms valid credentials
    2. bedrock:ListFoundationModels — confirms Bedrock access

    Returns caller identity dict on success.
    Raises PreflightError with actionable message on failure.
    """
    # 1. Validate credentials via STS
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
    except (BotoCoreError, ClientError) as e:
        raise PreflightError(
            f"AWS credentials invalid or expired. Run 'aws sts get-caller-identity' to debug.\n"
            f"Error: {e}"
        ) from e

    account = identity["Account"]
    arn = identity["Arn"]
    print(f"✓ AWS credentials valid: account={account}, arn={arn}")

    # 2. Validate Bedrock access
    try:
        bedrock = boto3.client("bedrock", region_name="us-east-1")
        bedrock.list_foundation_models(maxResults=1)
    except (BotoCoreError, ClientError) as e:
        raise PreflightError(
            f"Bedrock access check failed. Ensure your role has bedrock:ListFoundationModels permission.\n"
            f"Error: {e}"
        ) from e

    print("✓ Bedrock access confirmed")
    return {"account": account, "arn": arn}
