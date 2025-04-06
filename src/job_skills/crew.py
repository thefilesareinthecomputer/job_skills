from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import os
from dotenv import load_dotenv
from job_skills.tools.perplexity_tool import PerplexityTool
from job_skills.tools.skills_csv_tool import SkillsCSVTool
from job_skills.tools.wikipedia_tool import WikipediaTool
from job_skills.tools.howdoi_tool import HowDoITool

load_dotenv()

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class JobSkills():
    """JobSkills crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=True,
            # allow_delegation=True,
            tools=[HowDoITool(), WikipediaTool(), PerplexityTool()]
        )
        
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True,
            # allow_delegation=True,
            tools=[HowDoITool(), WikipediaTool(), PerplexityTool()] 
        )

    @agent
    def skill_instructor(self) -> Agent:
        return Agent(
            config=self.agents_config['skill_instructor'],
            verbose=True,
            # allow_delegation=True,
            tools=[HowDoITool(), WikipediaTool(), PerplexityTool()]
        )
        
    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            output_file='01_report.md'
        )
        
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            output_file='02_research.md'
        )
        
    @task
    def skill_instructor_task(self) -> Task:
        return Task(
            config=self.tasks_config['skill_instructor_task'],
            output_file='03_instructions.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the JobSkills crew"""
        # Create instances of your agents
        researcher = self.researcher()
        reporting_analyst = self.reporting_analyst()
        skill_instructor = self.skill_instructor()
        
        return Crew(
            manager_agent=reporting_analyst,
            agents=[researcher, skill_instructor],
            tasks=self.tasks,
            # process=Process.hierarchical,
            process=Process.sequential,
            verbose=True,
        )


















# perplexity_llm = LLM(
#     provider="perplexity",
#     api_key=os.getenv("PERPLEXITY_API_KEY"),
#     model="perplexity/sonar-deep-research",
#     base_url="https://api.perplexity.ai/",
#     endpoint="/chat/completions",
#     additional_kwargs={"stop": None}
# )

# perplexity_llm = LLM(
#     api_key=os.getenv("PERPLEXITY_API_KEY"),
#     model="sonar-deep-research",  # Use the model that worked in your test
#     base_url="https://api.perplexity.ai",  # Base URL without the /chat/completions part
#     provider="perplexity"  # Explicitly specify the provider
# )