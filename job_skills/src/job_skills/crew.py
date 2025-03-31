from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import os
from dotenv import load_dotenv
from job_skills.tools.perplexity_tool import PerplexityTool
from job_skills.tools.skills_csv_tool import SkillsCSVTool

load_dotenv()

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

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
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            verbose=True,
            tools=[SkillsCSVTool(), PerplexityTool()]  # Add both tools to the researcher
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the JobSkills crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
