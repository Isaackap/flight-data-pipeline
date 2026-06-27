import json

import secret_load


class FakeSecretsClient:
    def __init__(self):
        self.secret_ids = []
        self.updated_secrets = []

    def get_secret_value(self, SecretId):
        self.secret_ids.append(SecretId)
        return {"SecretString": json.dumps({"SERPAPI_KEY": "secret-api-key"})}

    def update_secret(self, SecretId, SecretString):
        self.updated_secrets.append((SecretId, SecretString))
        return {"ARN": "fake-secret-arn"}


class FakeSession:
    client_instance = FakeSecretsClient()
    client_calls = []

    def client(self, service_name, region_name):
        FakeSession.client_calls.append((service_name, region_name))
        return FakeSession.client_instance


def reset_fake_session():
    FakeSession.client_instance = FakeSecretsClient()
    FakeSession.client_calls = []


def test_get_env_secret_reads_value_from_aws_secret(monkeypatch):
    reset_fake_session()
    monkeypatch.setattr(secret_load.boto3.session, "Session", FakeSession)

    value = secret_load.getEnvSecret("Env", "SERPAPI_KEY")

    assert value == "secret-api-key"
    assert FakeSession.client_calls == [("secretsmanager", "us-east-2")]
    assert FakeSession.client_instance.secret_ids == ["Env"]


def test_get_credentials_writes_secret_string_to_file(tmp_path, monkeypatch):
    reset_fake_session()
    output_file = tmp_path / "credentials.json"
    monkeypatch.setattr(secret_load.boto3.session, "Session", FakeSession)

    secret_load.getCredentials("Credentials", str(output_file))

    assert output_file.read_text(encoding="utf-8") == json.dumps({
        "SERPAPI_KEY": "secret-api-key",
    })
    assert FakeSession.client_instance.secret_ids == ["Credentials"]


def test_update_token_secret_uploads_file_contents(tmp_path, monkeypatch, capsys):
    reset_fake_session()
    token_file = tmp_path / "token.json"
    token_file.write_text('{"refresh_token": "abc"}', encoding="utf-8")
    monkeypatch.setattr(secret_load.boto3.session, "Session", FakeSession)

    secret_load.updateTokenSecret("Token", str(token_file))

    assert FakeSession.client_instance.updated_secrets == [
        ("Token", '{"refresh_token": "abc"}')
    ]
    assert "Secret Token upadated successfully" in capsys.readouterr().out
