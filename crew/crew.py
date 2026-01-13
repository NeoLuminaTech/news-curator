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

        result = crew.kickoff()
        return result

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

        result = crew.kickoff()
        return result
