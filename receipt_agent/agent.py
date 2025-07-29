from google.adk.agents import Agent

from .types import Receipt
from .prompt import receipt_itemization_agent_prompt
from tools.gcs import upload_image_to_gcs
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest
from loguru import logger

def upload_receipt_to_gcs(callback_context: CallbackContext, llm_request: LlmRequest): # pylint: disable=unused-argument
    """
    Callback function to upload the receipt image to Google Cloud Storage.

    Args:
        callback_context (CallbackContext): Context for the callback.
        llm_request (LlmRequest): The request containing the receipt image.

    Returns:
        str: The public URL of the uploaded receipt image.
    """
    if llm_request.contents and llm_request.contents[-1].role == 'user':
        for content in llm_request.contents:
            if content.role != 'user':
                continue
            for part in content.parts:
                if part.inline_data is None:
                    continue
                logger.info("Uploading receipt image to GCS")
                upload_image_to_gcs(part.inline_data.data)
                return

root_agent = Agent(
    name="receipt_itemization_agent",
    model="gemini-2.0-flash",
    description="Receipt itemization agent",
    instruction=receipt_itemization_agent_prompt,
    before_model_callback=upload_receipt_to_gcs,
    output_schema=Receipt,
)
