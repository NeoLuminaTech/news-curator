import os
import yaml
import logging
from dotenv import load_dotenv
import datetime
from crew.crew import NewsCuratorCrew
from services.mailer import Mailer
from jinja2 import Environment, FileSystemLoader
from config.llm_config import configure_llm

# Load environment variables
load_dotenv()

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def render_email(template_path, context):
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))
    return template.render(context)

def main():
    logger.info("Starting Logistics Intelligence Radar...")
    
    # Configure LLM Provider (Fallback Logic)
    configure_llm()

    # Load Configs
    topics_config = load_config('config/topics.yaml')
    recipients_config = load_config('config/recipients.yaml')

    topics = [t['name'] for t in topics_config['topics']]
    # We pass the full topics config description/keywords if needed, but the agents handle it.
    
    recipients = recipients_config['recipients']

    logger.info(f"Loaded {len(topics)} mandatory sections.")

    # Initialize Crew
    news_crew = NewsCuratorCrew()

    # PHASE 1: Research & Master Digest
    logger.info("Starting Phase 1: Global Research & Master Digest...")
    try:
        # In this new flow, run_research_phase returns the COMPILED Master Digest string
        master_digest = news_crew.run_research_phase(topics)
        logger.info("Master Digest Analysis Completed.")
    except Exception as e:
        logger.error(f"Research Phase Failed: {e}")
        return

    # PHASE 2: Personalization & Delivery
    mailer = Mailer()
    template_path = 'email/templates/newsletter.html'

    logger.info("Starting Phase 2: Personalization & Delivery...")
    for recipient in recipients:
        logger.info(f"Processing Brief for: {recipient['name']} ({recipient['role']})")
        try:
            # Generate Personalized Body (HTML Fragment or Full HTML)
            # The agent is returning "Complete HTML string".
            # BUT our template wrapper needs just the body content if we want to wrap it consistently.
            # OR we let the agent control the whole thing.
            # Let's assume the agent returns the CONTENT BLOCK (HTML formatted but inside the body).
            # To be safe, let's treat the output as the "body" to be injected into our Jinja template.
            
            p_result = news_crew.run_personalization_phase(recipient, str(master_digest))
            
            # Since CrewAI kickoff returns an object, we cast to str.
            personalized_content = str(p_result)

            # Render final email with Wrapper
            today_str = datetime.datetime.now().strftime("%d-%B")
            final_email_html = render_email(template_path, {
                'name': recipient['name'],
                'subject': "Tirwin Pulse | Logistics Intelligence Brief", 
                'body': personalized_content,
                'date': today_str
            })
            
            subject = "Tirwin Pulse | Logistics Intelligence Brief"
            
            # Sending
            success = mailer.send_email(
                to_email=recipient['email'],
                subject=subject,
                html_body=final_email_html,
                text_body="Please enable HTML to view this intelligence brief."
            )
            
            if success:
                logger.info(f"Brief sent to {recipient['email']}")
            else:
                logger.error(f"Failed to send brief to {recipient['email']}")

        except Exception as e:
            logger.error(f"Error processing for {recipient['name']}: {e}")
            continue

    logger.info("Logistics Radar Run Completed.")

if __name__ == "__main__":
    main()
