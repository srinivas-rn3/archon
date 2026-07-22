from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from botocore.exceptions import ClientError


def with_retry(func):
    """
    Decorator that retries a function up to 3 times with exponential
    backoff, specifically for transient failures (throttling, timeouts,
    momentary network issues) when calling Bedrock.

    Does NOT retry on things like invalid model ID or bad permissions —
    those will fail the same way every time, so retrying is pointless.
    """
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(ClientError),
        reraise=True,  # if all retries fail, raise the real error, don't swallow it
    )(func)