## Importing libraries and files
from crewai import Task

from agents import comprehensive_analyst, MEDICAL_DISCLAIMER
from tools import search_tool, read_blood_test_tool

## Creating a single comprehensive blood test analysis task
comprehensive_blood_analysis = Task(
    description="""Provide a complete, evidence-based analysis of the blood test results for the user's query: {query}.
Analyze the provided report and generate a concise, easy-to-read summary. The output should be well-structured markdown.""",

    expected_output=f"""A concise, professionally formatted markdown report.

### Overall Summary
A brief, top-level summary of the findings (2-3 sentences).

### Key Findings & Interpretation
- **Marker Group (e.g., Complete Blood Count):** Status (e.g., All values within normal range).
- **Key Abnormal Marker (e.g., LDL Cholesterol):** Provide the value and a brief, clear interpretation of what it means.
- Use bullet points for each key marker or group of markers. Be direct and avoid conversational language.

### Recommendations
#### Nutrition
- Actionable dietary recommendations based on the findings. Use bullet points.
#### Exercise
- Safe and effective exercise recommendations. Use bullet points.
#### Follow-up
- Recommendations for monitoring and when to consult a healthcare professional.

### Document Quality Assessment
- A brief, one-line note on the document's quality and any limitations.

---
{MEDICAL_DISCLAIMER}

**Professional Consultation Emphasis**: For nutritional planning, consult with a Registered Dietitian Nutritionist (RDN). For exercise prescription, work with a Certified Exercise Physiologist (CEP) or qualified fitness professional. Always obtain medical clearance before making significant dietary or exercise changes.""",

    agent=comprehensive_analyst,
    tools=[read_blood_test_tool],
    async_execution=False,
)