# ECS Event Alert Pipeline to Slack

This repository sets up a complete AWS monitoring pipeline where an ECS Task sends an alert to Slack via EventBridge, SNS, and a Lambda function.

---

## 🔧 Stack

- Amazon ECS (Fargate)
- Amazon EventBridge
- Amazon SNS
- AWS Lambda
- Slack Webhook

---

## 📦 Components

```
ecs-alert-bot/
├── lambda/
│   └── ecs_alert_handler.py     # Lambda that sends Slack messages
├── docker-app/
│   ├── Dockerfile               # Docker image run on ECS
│   └── app.py  
├── eventbridge/
│   └── ecs-alert-evb-rule.json  # EventBridge rule
```

---

## 🚀 Full Setup Instructions

### 1️⃣ Build and Push Docker Image to ECR

```bash
# Create ECR repo
aws ecr create-repository --repository-name ecs-alert-app

# Authenticate Docker
aws ecr get-login-password | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com

# Build & push image
cd docker-app
docker build -t ecs-alert-app .
docker tag ecs-alert-app:latest <your_ecr_uri>:latest
docker push <your_ecr_uri>:latest
```

---

### 2️⃣ Run the Docker Image in ECS Fargate

- Go to ECS → Create Cluster → "Networking only"
- Create a **task definition**:
  - Launch type: Fargate
  - Container name: `ecs-alert-container`
  - Image: ECR image URI
  - Port: `3000` (optional, not used here)
- Run a task in your cluster using this task definition

---

### 3️⃣ Create SNS Topic

- Go to **SNS** → Create topic:
  - Type: Standard
  - Name: `ecs-alert-topic`

---

### 4️⃣ Create Lambda Function

- Go to **Lambda** → Create function:
  - Name: `ecs-alert-to-slack`
  - Runtime: Python 3.12
- Add environment variable:
  - `SLACK_WEBHOOK_URL` = Your Slack webhook URL
- Upload `ecs_alert_handler.py` as inline code or ZIP
- Deploy

---

### 5️⃣ Subscribe Lambda to SNS

- Go to SNS → Subscriptions → Create:
  - Protocol: AWS Lambda
  - Endpoint: select your Lambda function

---

### 6️⃣ Create EventBridge Rule

- Go to EventBridge → Rules → Create rule
- Choose **Custom pattern** and use this JSON:
```json
{
  "source": ["aws.ecs"],
  "detail-type": ["ECS Task State Change"],
  "detail": {
    "lastStatus": ["STOPPED"]
  }
}
```
- As target, choose **SNS topic**: `ecs-alert-topic`

---

### 7️⃣ Set Up Slack Webhook

- Go to [https://api.slack.com/apps](https://api.slack.com/apps)
- Create a new app → Add "Incoming Webhooks"
- Turn on Webhooks → Add new webhook to channel
- Copy the generated webhook URL
- Paste into Lambda environment variable `SLACK_WEBHOOK_URL`

---

### ✅ Done!

Now every time your ECS task completes (either success or failure), your Slack channel will receive a formatted alert with task status and info.

---

## 📷 Screenshot Example

```
*ECS Task Alert*
• Status: `STOPPED` (Desired: `STOPPED`)
• Task ARN: `arn:aws:ecs:...`
• Cluster ARN: `arn:aws:ecs:...`
• Stop Code: `EssentialContainerExited`
• Containers: `['ecs-alert-container']`
```

---

## 📄 License

MIT