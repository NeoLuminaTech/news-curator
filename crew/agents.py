from crewai import Agent
from crewai.tools import BaseTool
from services.news_fetcher import NewsFetcher

# Keep the same tool
class NewsSearchTool(BaseTool):
    name: str = "News Search Tool"
    description: str = "Search for news articles by topic."

    def _run(self, topic: str) -> str:
        fetcher = NewsFetcher()
        articles = fetcher.fetch_news(topic)
        output = f"Reference News for topic '{topic}':\n\n"
        for i, art in enumerate(articles, 1):
            output += f"{i}. TITLE: {art['title']}\n   SOURCE: {art['source']} ({art['date']})\n   URL: {art['url']}\n   CONTENT: {art['content']}\n\n"
        return output

class LogisticsCrewAgents:
    def research_agent(self):
        return Agent(
            role='Logistics Intelligence Researcher',
            goal='Fetch high-signal news across 5 mandatory categories: Macro, Tech, Policy, Best Practices, Talent.',
            backstory='You are an elite research analyst for the global logistics industry. You know exactly where to look for high-impact updates.',
            tools=[NewsSearchTool()],
            verbose=True,
            memory=True
        )

    def macro_impact_agent(self):
        return Agent(
            role='Global Trade Analyst (India Focus)',
            goal='Analyze global macro events and explicitly derive the impact on Indian exporters/importers.',
            backstory='You are an expert on global trade winds. You connect the dots between a Suez blockage and an exporter in Mumbai.',
            verbose=True
        )

    def tech_signal_agent(self):
        return Agent(
            role='Logistics Technology Scout',
            goal='Filter hype from reality in logistics tech. Focus on deployable solutions for India.',
            backstory='You are a pragmatic technologist. You care about ROI and adoption in Tier-2 Indian cities, not just SV buzzwords.',
            verbose=True
        )

    def infra_policy_agent(self):
        return Agent(
            role='India Policy & Infrastructure Expert',
            goal='Track GatiShakti, DFCs, and regulatory shifts in India.',
            backstory='You have deep connections in the Ministry of Commerce. You know how policy translates to ground reality.',
            verbose=True
        )

    def best_practices_agent(self):
        return Agent(
            role='Operational Excellence Strategist',
            goal='Curate global case studies that Indian companies can adopt.',
            backstory='You study giants like Maersk and DHL to find lessons for the Indian market.',
            verbose=True
        )

    def talent_insights_agent(self):
        return Agent(
            role='Workforce Transformation Specialist',
            goal='Address the talent gap in Indian logistics.',
            backstory='You focus on the human element: skilling, retention, and the shift to "digital blue-collar".',
            verbose=True
        )

    def personalization_agent(self):
        return Agent(
            role='Personal Communication Assistant',
            goal='Tailor news insights to the specific interests and role of a recipient.',
            backstory='You are a personal aide who understands exactly what your focus is. You filter content to match a specific professional tone.',
            verbose=True
        )

    def email_composer_agent(self):
        return Agent(
            role='Professional Email Copywriter',
            goal='Compose a structured, engaging, and professional HTML email newsletter.',
            backstory='Your job is to take the master digest and format it perfectly into HTML for the user.',
            verbose=True
        )
