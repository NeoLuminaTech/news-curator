from crewai import Task

class LogisticsCrewTasks:
    def fetch_news_task(self, agent, topics):
        return Task(
            description=f"""
                Search for the high-impact news articles for the following mandatory logistics sections: {topics}.
                Focus on reliable trade journals, major news outlets, and Indian financial news.
                Return a raw list of articles grouped by section.
            """,
            expected_output="A structured list of raw news articles grouped by the 5 sections.",
            agent=agent
        )

    def _create_analysis_task(self, agent, section_name, context, specific_instruction):
        return Task(
            description=f"""
                You are responsible for the '{section_name}' section of the intelligence brief.
                
                Using the provided raw news (from previous task context):
                1. Select the top 2 most critical stories for this section. (You MUST select exactly 2 stories. If fewer than 2 are obviously critical, include the next best relevant stories to meet the count of 2.)
                2. {specific_instruction}
                3. STRICT OUTPUT FORMAT for each selected story:
                   - HEADLINE: Executive tone, no clickbait.
                   - SUMMARY: 2-3 concise bullet points.
                   - INDIA IMPACT (CRITICAL): What does this mean for Indian exporters/importers? (Mandatory)
                   - URL: Source link. (CRITICAL: MUST be a valid, direct url to the article. Do not fabricate.)
                   
                If no news is found, provide a "Nothing critical to report today" note but do not hallucinate.
            """,
            expected_output=f"Structured intelligence block for {section_name}.",
            agent=agent,
            context=context
        )

    def analyze_macro_task(self, agent, context):
        return self._create_analysis_task(
            agent, 
            "GLOBAL MACRO RADAR", 
            context,
            "Focus on trade lanes, freight rates, and geopolitical shifts. explicitly connect global events to Indian trade costs."
        )

    def analyze_tech_task(self, agent, context):
        return self._create_analysis_task(
            agent, 
            "LOGISTICS TECH LAB", 
            context,
            "Focus on WES, automation, and AI. Filter out hype. Mention adoption potential in India."
        )

    def analyze_policy_task(self, agent, context):
        return self._create_analysis_task(
            agent, 
            "GOVERNMENT & POLICY", 
            context,
            "Focus on GatiShakti, DFCs, Customs, and regulatory updates in India."
        )

    def analyze_best_practices_task(self, agent, context):
        return self._create_analysis_task(
            agent, 
            "GLOBAL BEST PRACTICES", 
            context,
            "Identify operational shifts in global giants (e.g., resilience vs lean) and apply lessons for Indian firms."
        )

    def analyze_talent_task(self, agent, context):
        return self._create_analysis_task(
            agent, 
            "THE LOGISTICS TALENT BENCH", 
            context,
            "Focus on the skills gap, blue-collar tech roles, and workforce transformation in India."
        )

    def compile_newsletter_task(self, agent, context, recipients):
        # Master Digest Compilation
        return Task(
            description="""
                Aggregate the outputs from all 5 analysis agents.
                Format them into a single coherent Master Digest text block.
                Ensure the 5-section structure is preserved exactly.
            """,
            expected_output="A full master digest string.",
            agent=agent,
            context=context
        )

    def personalize_task(self, agent, recipient, context):
        return Task(
            description=f"""
                You are preparing a update for {recipient['name']}, who is a {recipient['role']}.
                Their interests are: {recipient['interests']}.
                Their preferred tone is: {recipient['tone']}.

                Using the Master Digest:
                1. Start with "Dear {recipient['name']},".
                2. Write a warm, slightly philosophical opening paragraph (approx 50 words) about resilience, strategy, or the current year (2025). Do NOT focus on dry business start immediately. Be human.
                3. Follow with EXACTLY this sentence structure: "This edition offers insights on [List the 5 key headlines/topics from the digest], and [Last Topic]."
                4. Sign off this intro section with "Hope you find this effort worthwhile."
                5. Then, append the COMPLETE Master Digest exactly as provided.
                6. CRITICAL: DO NOT REMOVE ANY STORIES.
            """,
            expected_output=f"A text block starting with Dear {recipient['name']}, followed by the philosophical intro, the topics summary, and then the full digest.",
            agent=agent,
            context=context
        )

    def compose_email_task(self, agent, recipient, context):
        return Task(
            description=f"""
                Compose a full HTML email for {recipient['name']}.
                Subject Line: Urgent Logistics Intel: [Key Topic]
                
                Structure:
                - Greeting
                - The Philosophical Opening & Topic List (Copy this VERBATIM from the context. Do not rewrite.)
                - The 5 Sections (Render the Master Digest content nicely with dividers).
                  For each story, include a "Read More" button using this HTML: <a href="[URL]" class="read-more-btn" style="display: inline-block; padding: 8px 15px; background-color: #0066cc; color: #ffffff; text-decoration: none; border-radius: 4px; font-weight: bold; margin-top: 8px;">Read More</a>
                - Closing Insight
                
                Output ONLY the raw HTML content. DO NOT exclude the "This edition offers insights on..." sentence.
            """,
            expected_output="A complete HTML string.",
            agent=agent,
            context=context
        )
