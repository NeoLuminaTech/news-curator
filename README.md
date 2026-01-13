# CrewAI News Curator

A production-ready CrewAI application that collects news, summarizes it using LLMs, and sends personalized email digests. Run fully automated via GitHub Actions.

## Features

* **Automated News Collection**: Fetches latest news from Google News RSS by topic.
* **AI Analysis**: Summarizes and provides "Why it matters" insights.
* **Personalization**: Tailors content tone and selection for specific recipients.
* **Email Delivery**: HTML-formatted emails via SMTP.
* **GitHub Actions**: Cron-based scheduling.

## Setup

1. **Clone the Repository**
2. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure**:
    * Update `config/topics.yaml` with your interests.
    * Update `config/recipients.yaml` with your recipient list.
4. **Environment Variables**:
    Create a `.env` file for local testing (DO NOT COMMIT):

    ```
    OPENAI_API_KEY=sk-...
    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USERNAME=your@email.com
    SMTP_PASSWORD=your_app_password
    ```

## Running Locally

```bash
python main.py
```

## GitHub Actions Configuration

1. Go to **Settings > Secrets and variables > Actions**.
2. Add the following Repository Secrets:
    * `OPENAI_API_KEY`
    * `SMTP_HOST`
    * `SMTP_PORT`
    * `SMTP_USERNAME`
    * `SMTP_PASSWORD`

The workflow runs daily at 08:00 UTC. You can also manually trigger it from the "Actions" tab.
