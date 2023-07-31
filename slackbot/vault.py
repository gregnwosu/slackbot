from azure.identity.aio import EnvironmentCredential
from azure.keyvault.secrets.aio import SecretClient
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

VAULT_URL = os.environ["VAULT_URL"]

os.environ["AZURE_CLIENT_ID"] = os.environ["ARM_CLIENT_ID"]
os.environ["AZURE_CLIENT_SECRET"] = os.environ["ARM_CLIENT_SECRET"]
os.environ["AZURE_TENANT_ID"] = os.environ["ARM_TENANT_ID"]


async def get_secret(secret_name):
    async with EnvironmentCredential() as credential:
        async with SecretClient(vault_url=VAULT_URL, credential=credential) as client:
            secret = await client.get_secret(secret_name)
            return secret.value
