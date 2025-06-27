## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent
from crewai import LLM

from tools import search_tool, read_blood_test_tool

### Loading LLM - Using Google Gemini instead of OpenAI
llm = LLM(
    model="gemini/gemini-1.5-flash", 
    temperature=0.1,
    api_key=os.getenv("GOOGLE_API_KEY")
)

# Creating a Single Comprehensive Medical Professional Agent
comprehensive_analyst = Agent(
    role="Comprehensive Medical Analysis Professional",
    goal="Provide complete, evidence-based analysis of blood test results including medical interpretation, nutritional guidance, and exercise recommendations for: {query}. Always include appropriate medical disclaimers and recommend consulting with healthcare professionals.",
    verbose=True,
    memory=True,
    backstory=(
        "You are a highly qualified medical professional with comprehensive expertise across multiple disciplines: "
        "- 15+ years as a certified medical laboratory scientist (ASCP certified) with expertise in clinical diagnostics "
        "- Board-certified Registered Dietitian Nutritionist (RDN) with Master's degree in Clinical Nutrition "
        "- Certified Exercise Physiologist (CEP) through ACSM with specialization in medical exercise prescription "
        "- Extensive experience in medical document verification and quality assurance "
        "You combine deep knowledge of laboratory medicine, evidence-based nutrition science, and exercise physiology "
        "to provide comprehensive yet safe guidance. You always emphasize professional medical supervision, "
        "provide appropriate disclaimers, and base all recommendations on peer-reviewed research and established "
        "clinical guidelines from organizations like ASCP, Academy of Nutrition and Dietetics, ACSM, and AHA. "
        "You ALWAYS complete your full analysis in a single comprehensive response covering all requested sections."
    ),
    tools=[read_blood_test_tool],
    llm=llm,
    max_iter=5,
    max_execution_time=300,
    allow_delegation=False,
    step_callback=None
)

# Medical Disclaimer Constants
MEDICAL_DISCLAIMER = """
**IMPORTANT MEDICAL DISCLAIMER**: This analysis is for educational purposes only and does not constitute medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical decisions. Laboratory results should be interpreted by your physician in the context of your medical history, symptoms, and clinical examination. Do not make changes to medications, diet, or exercise routines without proper medical supervision.
"""
