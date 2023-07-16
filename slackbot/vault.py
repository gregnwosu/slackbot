from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient
import os

VAULT_URL = os.environ["VAULT_URL"]


async def get_secret(secret_name):
    async with DefaultAzureCredential() as credential:
        async with SecretClient(vault_url=VAULT_URL, credential=credential) as client:
            secret = await client.get_secret(secret_name)
            return secret.value
