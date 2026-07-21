import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()

groq_llm = LLM(
    model="openai/llama-3.3-70b-versatile",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)

async def run_marketing_crew(inputs: dict) -> dict: # 👈 ১. রিটার্ন টাইপ dict করা হলো

    researcher = Agent(
        role="Senior Market Research Analyst",
        goal="Conduct in-depth market research and extract actionable insights for {brand_name}.",
        backstory="You are an expert market analyst skilled at identifying target audience pain points.",
        llm=groq_llm,
        verbose=True,
        allow_delegation=False
    )

    copywriter = Agent(
        role="Creative Marketing Copywriter",
        goal="Draft high-converting ad copies and marketing content based on research insights.",
        backstory="You are a master copywriter who excels at creating viral marketing content.",
        llm=groq_llm,
        verbose=True,
        allow_delegation=False
    )

    research_task = Task(
        description="Analyze the market context for the brand: '{brand_name}'. Product: {product_description}",
        expected_output="A structured market analysis report highlighting key insights.",
        agent=researcher
    )

    copywriting_task = Task(
        description="Draft 3 compelling ad copy variations based on research.",
        expected_output="3 high-converting ad copies clearly formatted.",
        agent=copywriter
    )

    marketing_crew = Crew(
        agents=[researcher, copywriter],
        tasks=[research_task, copywriting_task],
        process=Process.sequential,
        verbose=True,
        max_rpm=15
    )

    # Crew এক্সিকিউট করা
    await marketing_crew.kickoff_async(inputs=inputs)

    # 👈 ২. প্রতিটি টাস্কের আউটপুট এক্সট্র্যাক্ট করে Dictionary আকারে রিটার্ন করা
    return {
        "research_result": str(research_task.output.raw),
        "ad_copies": str(copywriting_task.output.raw)
    }

