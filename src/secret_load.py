import boto3
import json
import os

# Grab all environment variables stored in a single AWS Secret
def getEnvSecret(secret_name, secret_value) -> str:
    secret_name = secret_name
    region_name = "us-east-2"

    # Create a secrets manager client
    session = boto3.session.Session()
    client = session.client(
        service_name = "secretsmanager",
        region_name = region_name
    )

    get_secret_value_response = client.get_secret_value(
        SecretId = secret_name
    )

    secret = get_secret_value_response["SecretString"]
    secret = json.loads(secret)
    #print(secret[secret_value])
    return secret[secret_value]

# Grab the token and credentials json data stored in a AWS Secret, and write to a .json file
def getCredentials(secret_name, filename):
    secret_name = secret_name
    filename = filename
    region_name = "us-east-2"

    # Create a secrets manager client
    session = boto3.session.Session()
    client = session.client(
        service_name = "secretsmanager",
        region_name = region_name
    )

    get_secret_value_response = client.get_secret_value(
        SecretId = secret_name
    )

    secret = get_secret_value_response["SecretString"]
    with open(filename, "w+") as file:
        file.write(secret)
    #print("File created")

# Update the 'token.json' token AWS Secret with the new one in case it got refreshed/regenerated
def updateTokenSecret(secret_name, filename):
    secret_name = secret_name
    filename = filename
    region_name = "us-east-2"

    with open(filename, "r") as file:
        new_token_data = file.read()

    # Create a secrets manager client
    session = boto3.session.Session()
    client = session.client(
        service_name = "secretsmanager",
        region_name = region_name
    )

    update_secret_value_response = client.update_secret(
        SecretId = secret_name,
        SecretString = new_token_data
    )

    print(f"Secret {secret_name} upadated successfully")
