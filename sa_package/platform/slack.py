import requests
import json

# ========================================================================
# 슬랙 메시지 보내기
# ========================================================================

def send_slack_message(token, text, channel="data-management-crawler"):
    headers = headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }
    payload = {
        "channel": channel,
        "text": text,
    }
    requests.post(
        "https://slack.com/api/chat.postMessage",
        headers=headers,
        data=json.dumps(payload)
    )


def send_slack_message_formatted(token, subject, body=None, link=None, msg_type=None, channel=None):

    """
    msg_type : "notice", "error", "log"
    """

    if msg_type == "notice":
        channel = "crawler-notice"
        emoji = ":mega:"

    elif msg_type == "error":
        channel = "crawler-notice"
        emoji = ":rotating_light:"

    elif msg_type == "log":
        channel = "crawler-log"
        emoji = ":left_speech_bubble:"

    else:
        if channel is None:
            channel = "data-management-crawler"
        emoji = ":bulb:"

    text = f"""{emoji} *{subject}*\n"""
    if body is not None:
        body_cleansed = """\n
        """.join(body.split('\n'))
        
        text = text + f"""
        {body_cleansed}"""

    if link is not None:
        text = text + f"""
        *<{link}|링크>* 에서 확인하기
        """
    
    headers = headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    payload = {
        "channel": channel,
        "text": text,
    }

    requests.post(
        "https://slack.com/api/chat.postMessage",
        headers=headers,
        data=json.dumps(payload)
    )