import json
import os
import urllib.request

def lambda_handler(event, context):
    webhook_url = os.environ['SLACK_WEBHOOK_URL']

    for record in event['Records']:
        sns_message = record['Sns']['Message']
        try:
            detail = json.loads(sns_message)['detail']
            task_arn = detail.get('taskArn', 'N/A')
            cluster_arn = detail.get('clusterArn', 'N/A')
            last_status = detail.get('lastStatus', 'N/A')
            desired_status = detail.get('desiredStatus', 'N/A')
            stop_code = detail.get('stopCode', 'N/A')
            containers = detail.get('containers', [])

            msg = (
                f"*ECS Task Alert*\n"
                f"• Status: `{last_status}` (Desired: `{desired_status}`)\n"
                f"• Task ARN: `{task_arn}`\n"
                f"• Cluster ARN: `{cluster_arn}`\n"
                f"• Stop Code: `{stop_code}`\n"
                f"• Containers: `{[c.get('name') for c in containers]}`"
            )
        except Exception as e:
            msg = f"Failed to parse SNS message: {e}\nRaw: {sns_message}"

        payload = {
            "text": msg
        }

        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            urllib.request.urlopen(req)
        except Exception as e:
            print(f"Error sending to Slack: {e}")

    return {"statusCode": 200, "body": "Notification sent"}
