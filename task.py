## Importing libraries and files
from crewai import Task

from agents import comprehensive_analyst, MEDICAL_DISCLAIMER
from tools import search_tool, read_blood_test_tool

## Creating a single comprehensive blood test analysis task
comprehensive_blood_analysis = Task(
    description="""Provide a complete, evidence-based analysis of the blood test results for the user's query: {query}.

Your comprehensive analysis should include:

**DOCUMENT VERIFICATION:**
1. Verify the document is a legitimate blood test report
2. Assess document quality and completeness
3. Identify any limitations based on document quality

**MEDICAL INTERPRETATION:**
1. Review and interpretation of all blood test values
2. Identification of values outside normal reference ranges
3. Explanation of what abnormal values might indicate
4. Clinical significance of findings

**NUTRITIONAL GUIDANCE:**
1. Relationships between blood markers and nutritional status
2. Evidence-based dietary recommendations
3. Foods that may support optimal blood marker levels
4. General nutritional guidance for health maintenance

**EXERCISE RECOMMENDATIONS:**
1. Exercise considerations based on blood test markers
2. Safe progression and intensity guidelines
3. Any contraindications or precautions
4. ACSM-based exercise guidance

**SAFETY & DISCLAIMERS:**
1. Clear limitations without clinical context
2. Emphasis on medical professional consultation
3. Appropriate medical disclaimers

Base all recommendations on established medical knowledge, peer-reviewed research, and clinical guidelines.""",

    expected_output=f"""Provide a comprehensive professional analysis in the following format:

**DOCUMENT VERIFICATION & QUALITY ASSESSMENT**
- Document type confirmation and authenticity assessment
- Quality evaluation and readability assessment
- Any limitations identified in the document

**COMPREHENSIVE BLOOD TEST ANALYSIS**
- Complete Blood Count (CBC) interpretation
- Basic/Comprehensive Metabolic Panel analysis
- Lipid panel interpretation
- Additional markers assessment (vitamins, hormones, etc.)
- Overall health status summary
- Values outside normal ranges with explanations

**CLINICAL INTERPRETATION & SIGNIFICANCE**
- What the results may indicate about current health status
- Areas of concern requiring medical attention
- Positive findings and healthy markers
- Limitations of analysis without full clinical context

**EVIDENCE-BASED NUTRITIONAL GUIDANCE**
- Blood markers related to nutritional status
- Dietary recommendations based on current results
- Foods to emphasize for optimal health
- Nutritional factors that may influence lab values
- Hydration and general dietary guidance

**SAFE EXERCISE RECOMMENDATIONS**
- Exercise capacity assessment based on blood markers
- Recommended types and intensity of physical activity
- Safety considerations and contraindications
- Progressive exercise guidelines
- Importance of medical clearance

**PROFESSIONAL RECOMMENDATIONS**
- Immediate actions recommended
- Follow-up testing suggestions
- When to consult healthcare providers
- Monitoring recommendations

{MEDICAL_DISCLAIMER}

**Professional Consultation Emphasis**: For nutritional planning, consult with a Registered Dietitian Nutritionist (RDN). For exercise prescription, work with a Certified Exercise Physiologist (CEP) or qualified fitness professional. Always obtain medical clearance before making significant dietary or exercise changes.""",

    agent=comprehensive_analyst,
    tools=[read_blood_test_tool],
    async_execution=False,
)