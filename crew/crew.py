from crewai import Crew, Process
from crew.agents import LogisticsCrewAgents
from crew.tasks import LogisticsCrewTasks

class NewsCuratorCrew:
    def __init__(self):
        self.agents = LogisticsCrewAgents()
        self.tasks = LogisticsCrewTasks()

    def run_research_phase(self, topics):
        # Agents
        researcher = self.agents.research_agent()
        macro_agent = self.agents.macro_impact_agent()
        tech_agent = self.agents.tech_signal_agent()
        policy_agent = self.agents.infra_policy_agent()
        practice_agent = self.agents.best_practices_agent()
        talent_agent = self.agents.talent_insights_agent()
        editor_agent = self.agents.editor_agent()
        
        # Tasks
        fetch_task = self.tasks.fetch_news_task(researcher, topics)
        
        macro_task = self.tasks.analyze_macro_task(macro_agent, context=[fetch_task])
        tech_task = self.tasks.analyze_tech_task(tech_agent, context=[fetch_task])
        policy_task = self.tasks.analyze_policy_task(policy_agent, context=[fetch_task])
        practice_task = self.tasks.analyze_best_practices_task(practice_agent, context=[fetch_task])
        talent_task = self.tasks.analyze_talent_task(talent_agent, context=[fetch_task])
        
        compile_task = self.tasks.compile_newsletter_task(
            editor_agent, 
            context=[macro_task, tech_task, policy_task, practice_task, talent_task],
            recipients=[] 
        )

        crew = Crew(
            agents=[researcher, macro_agent, tech_agent, policy_agent, practice_agent, talent_agent, editor_agent],
            tasks=[fetch_task, macro_task, tech_task, policy_task, practice_task, talent_task, compile_task],
            process=Process.sequential, 
            verbose=True
        )

        try:
            result = crew.kickoff()
            return result
        except Exception as e:
            import logging
            from services.news_fetcher import NewsFetcher
            
            logger = logging.getLogger(__name__)
            logger.error(f"LLM Crew Execution Failed: {e}. Initiating GNews Fallback.")
            
            fetcher = NewsFetcher()
            fallback_digest = "<h3>OFFLINE MODE - GNEWS FALLBACK</h3><br>"
            
            try:
                for topic in topics:
                    fallback_digest += f"<h4>Topic: {topic}</h4><ul>"
                    articles = fetcher.fetch_news_gnews(topic)
                    
                    if not articles:
                        fallback_digest += "<li>No recent news found.</li>"
                    
                    for article in articles:
                        fallback_digest += f"<li><a href='{article['url']}'>{article['title']}</a> - {article['source']} ({article['date']})<br>{article['content']}</li>"
                    
                    fallback_digest += "</ul><br>"
                
                return fallback_digest
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                return "<h2>System Offline</h2><p>Unable to generate newsletter due to multiple failures.</p>"

    def run_personalization_phase(self, recipient, master_digest):
        # Agents
        personalizer = self.agents.personalization_agent()
        composer = self.agents.email_composer_agent()
        
        # Tasks
        # We manually inject the master digest into the description as a "context" string
        personalize_task = self.tasks.personalize_task(personalizer, recipient, context=None)
        personalize_task.description += f"\n\n=== MASTER DIGEST ===\n{master_digest}\n====================="
        
        compose_task = self.tasks.compose_email_task(composer, recipient, context=[personalize_task])

        crew = Crew(
            agents=[personalizer, composer],
            tasks=[personalize_task, compose_task],
            process=Process.sequential,
            verbose=True
        )

        try:
            result = crew.kickoff()
            return result
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Personalization Crew Execution Failed: {e}. Falling back to Master Digest.")
            return master_digest
