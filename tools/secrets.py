from google.cloud import secretmanager
import os

class SecretsManager:
    def __init__(self, project_id: str | None = None):
        self.client = secretmanager.SecretManagerServiceClient()
        if project_id is None:
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.project_id = project_id

    def get_secret(self, secret_name: str) -> str:
        """
        Retrieves the value of a secret from Google Cloud Secret Manager.

        Args:
            secret_name (str): The name of the secret to retrieve.

        Returns:
            str: The value of the secret.
        """
        name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
        response = self.client.access_secret_version(name=name)
        return response.payload.data.decode('UTF-8')