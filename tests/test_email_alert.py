import email_alert


class FakeSMTP:
    instances = []

    def __init__(self, server, port):
        self.server = server
        self.port = port
        self.calls = []
        self.sent_message = None
        FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.calls.append(("exit", exc_type))

    def ehlo(self):
        self.calls.append(("ehlo",))

    def starttls(self):
        self.calls.append(("starttls",))

    def login(self, user, password):
        self.calls.append(("login", user, password))

    def send_message(self, msg):
        self.calls.append(("send_message", msg))
        self.sent_message = msg


def test_send_email_sends_non_empty_alert_and_clears_file(tmp_path, monkeypatch, capsys):
    alert_file = tmp_path / "flight_alert.txt"
    alert_file.write_text("IAH --> HND\n$900 USD\n", encoding="utf-8")

    FakeSMTP.instances = []
    monkeypatch.setattr(email_alert, "PATHS", {"flight_alert": str(alert_file)})
    monkeypatch.setattr(email_alert.smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(email_alert.config, "FROM_EMAIL", "sender@example.com")
    monkeypatch.setattr(email_alert.config, "TO_EMAIL", "receiver@example.com")
    monkeypatch.setattr(email_alert.config, "EMAIL_PASSWORD", "app-password")
    monkeypatch.setattr(email_alert.config, "SMTP_SERVER", "smtp.example.com")
    monkeypatch.setattr(email_alert.config, "SMTP_PORT", 2525)
    monkeypatch.setattr(email_alert.config, "EMAIL_SUBJECT", "Price Alert")

    email_alert.sendEmail()

    smtp = FakeSMTP.instances[0]
    assert smtp.server == "smtp.example.com"
    assert smtp.port == 2525
    assert ("login", "sender@example.com", "app-password") in smtp.calls
    assert smtp.sent_message["From"] == "sender@example.com"
    assert smtp.sent_message["To"] == "receiver@example.com"
    assert smtp.sent_message["Subject"] == "Price Alert"
    assert "IAH --> HND" in smtp.sent_message.get_content()
    assert alert_file.read_text(encoding="utf-8") == ""
    assert "Email has been sent to receiver@example.com" in capsys.readouterr().out


def test_send_email_skips_empty_alert_file_and_clears_it(tmp_path, monkeypatch, capsys):
    alert_file = tmp_path / "flight_alert.txt"
    alert_file.write_text("   \n", encoding="utf-8")

    FakeSMTP.instances = []
    monkeypatch.setattr(email_alert, "PATHS", {"flight_alert": str(alert_file)})
    monkeypatch.setattr(email_alert.smtplib, "SMTP", FakeSMTP)

    email_alert.sendEmail()

    assert FakeSMTP.instances == []
    assert alert_file.read_text(encoding="utf-8") == ""
    assert "File was empty, didn't send email" in capsys.readouterr().out
