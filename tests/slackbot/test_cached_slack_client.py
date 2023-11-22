from slackbot.app import cached_slack_client


def test_returns_same_instance_on_subsequent_calls(self):
    client1 = cached_slack_client()
    client2 = cached_slack_client()
    assert client1 is client2