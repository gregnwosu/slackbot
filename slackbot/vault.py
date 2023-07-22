from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.secrets.aio import SecretClient
import os
from dotenv import load_dotenv, find_dotenv
import async_lru

load_dotenv(find_dotenv())

VAULT_URL = os.environ["VAULT_URL"]

# cache result from async function
@async_lru(maxsize=50)
async def get_secret(secret_name):
    async with DefaultAzureCredential() as credential:
        async with SecretClient(vault_url=VAULT_URL, credential=credential) as client:
            secret = await client.get_secret(secret_name)
            return secret.value
