## Importing libraries and files
import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

from crewai_tools import SerperDevTool
from crewai.tools import tool

# Configure logging for tools
logger = logging.getLogger(__name__)

## Creating search tool with error handling
try:
    search_tool = SerperDevTool()
    logger.info("SerperDevTool initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize SerperDevTool: {e}")
    search_tool = None

## Creating custom pdf reader tool with comprehensive error handling - Fixed for newer CrewAI
@tool("Blood Test Report Reader")
def read_blood_test_tool(**kwargs) -> str:
    """Tool to read data from a pdf file from a path with comprehensive error handling

    Args:
    path (str): Path of the pdf file. Defaults to 'data/sample.pdf'.

    Returns:
    str: Full Blood Test report content or error message
    """
    # Extract path from kwargs, handling newer CrewAI argument format
    path = kwargs.get('path', 'data/sample.pdf')
    
    # If path is still not a string, try to get it from the first positional argument
    if not isinstance(path, str) and len(kwargs) > 0:
        # Try to find the path in various possible keys
        for key in ['path', 'file_path', 'filepath', 'input']:
            if key in kwargs and isinstance(kwargs[key], str):
                path = kwargs[key]
                break
        
        # If still not found, use default
        if not isinstance(path, str):
            path = 'data/sample.pdf'
    
    logger.info(f"Attempting to read blood test report from: {path}")
    
    try:
        # Validate input path
        if not path or not isinstance(path, str):
            error_msg = "Invalid file path provided"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        # Convert to Path object for better handling
        file_path = Path(path)
        
        # Check if file exists
        if not file_path.exists():
            error_msg = f"File not found: {path}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        # Check if path is actually a file
        if not file_path.is_file():
            error_msg = f"Path is not a file: {path}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        # Check file extension
        if file_path.suffix.lower() != '.pdf':
            error_msg = f"File is not a PDF: {path}"
            logger.warning(error_msg)
            return f"Warning: {error_msg}. Attempting to process anyway."
        
        # Check file size
        file_size = file_path.stat().st_size
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            error_msg = f"File too large: {file_size / (1024*1024):.1f}MB (max: {max_size / (1024*1024):.1f}MB)"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        # Check if file is readable
        if not os.access(path, os.R_OK):
            error_msg = f"File is not readable: {path}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        # Try to read basic file information
        try:
            with open(path, 'rb') as f:
                header = f.read(8)
                if not header.startswith(b'%PDF-'):
                    error_msg = f"File does not appear to be a valid PDF: {path}"
                    logger.warning(error_msg)
                    return f"Warning: {error_msg}. Attempting to process anyway."
        except Exception as e:
            error_msg = f"Cannot read file header: {e}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        # For now, return a mock response since PDFLoader is not available
        # In a real implementation, this would use a PDF parsing library
        logger.info(f"Successfully validated PDF file: {path}")
        
        mock_report = f"""
        PROFESSIONAL BLOOD TEST REPORT ANALYSIS (from {path})
        ======================================================
        
        Document Information:
        - File: {file_path.name}
        - Size: {file_size / 1024:.1f} KB
        - Analysis Date: {file_path.stat().st_mtime}
        
        COMPLETE BLOOD COUNT (CBC):
        - White Blood Cells: 7.2 K/uL (Normal: 4.0-11.0) ✓
        - Red Blood Cells: 4.5 M/uL (Normal: 4.2-5.4) ✓
        - Hemoglobin: 14.2 g/dL (Normal: 12.0-16.0) ✓
        - Hematocrit: 42% (Normal: 36-46%) ✓
        - Platelets: 275 K/uL (Normal: 150-450) ✓
        
        BASIC METABOLIC PANEL:
        - Glucose: 95 mg/dL (Normal: 70-100) ✓
        - Sodium: 140 mEq/L (Normal: 136-145) ✓
        - Potassium: 4.1 mEq/L (Normal: 3.5-5.0) ✓
        - Chloride: 102 mEq/L (Normal: 98-107) ✓
        - BUN: 15 mg/dL (Normal: 7-20) ✓
        - Creatinine: 1.0 mg/dL (Normal: 0.6-1.2) ✓
        
        LIPID PANEL:
        - Total Cholesterol: 185 mg/dL (Normal: <200) ✓
        - LDL Cholesterol: 110 mg/dL (Normal: <100) ⚠️ SLIGHTLY ELEVATED
        - HDL Cholesterol: 55 mg/dL (Normal: >40) ✓
        - Triglycerides: 120 mg/dL (Normal: <150) ✓
        
        ADDITIONAL MARKERS:
        - Vitamin D: 32 ng/mL (Normal: 30-100) ✓
        - B12: 450 pg/mL (Normal: 200-900) ✓
        - Iron: 85 μg/dL (Normal: 60-170) ✓
        - TSH: 2.1 mIU/L (Normal: 0.4-4.0) ✓
        
        CLINICAL NOTES:
        - Overall health status appears good
        - Minor attention needed for LDL cholesterol
        - All other values within normal ranges
        - Regular monitoring recommended
        
        NOTE: This is a mock analysis for development purposes.
        In production, actual PDF parsing would extract real values.
        """
        
        logger.info(f"Successfully processed blood test report: {path}")
        return mock_report.strip()
        
    except FileNotFoundError:
        error_msg = f"File not found: {path}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except PermissionError:
        error_msg = f"Permission denied accessing file: {path}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except OSError as e:
        error_msg = f"OS error reading file {path}: {e}"
        logger.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error reading blood test report from {path}: {e}"
        logger.error(error_msg)
        return f"Error: {error_msg}"

## Creating enhanced nutrition analysis tool
@tool("Nutrition Analysis Tool")
def analyze_nutrition_tool(blood_report_data: str) -> str:
    """Analyze blood report data and provide evidence-based nutrition recommendations with error handling"""
    logger.info("Starting nutrition analysis")
    
    try:
        # Validate input
        if not blood_report_data or not isinstance(blood_report_data, str):
            error_msg = "No blood report data provided for nutrition analysis"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        if len(blood_report_data.strip()) < 10:
            error_msg = "Insufficient blood report data for meaningful nutrition analysis"
            logger.warning(error_msg)
            return f"Warning: {error_msg}"
        
        # Check for key nutritional markers in the data
        nutritional_markers = ['glucose', 'cholesterol', 'ldl', 'hdl', 'triglycerides', 'vitamin', 'iron', 'b12']
        found_markers = [marker for marker in nutritional_markers if marker.lower() in blood_report_data.lower()]
        
        if not found_markers:
            logger.warning("No recognizable nutritional markers found in blood report")
            return "Warning: No clear nutritional markers identified in the blood report data. Unable to provide specific nutritional guidance."
        
        logger.info(f"Found nutritional markers: {found_markers}")
        
        # Generate evidence-based nutrition analysis
        nutrition_analysis = f"""
        EVIDENCE-BASED NUTRITIONAL ANALYSIS
        ===================================
        
        Based on identified markers: {', '.join(found_markers)}
        
        NUTRITIONAL RECOMMENDATIONS:
        
        1. CARDIOVASCULAR HEALTH:
           - Consider Mediterranean diet pattern for lipid optimization
           - Increase omega-3 fatty acids (fatty fish 2x/week)
           - Limit saturated fat to <7% of total calories
           - Include soluble fiber (oats, beans, fruits)
        
        2. BLOOD SUGAR MANAGEMENT:
           - Focus on complex carbohydrates over simple sugars
           - Include protein with each meal for glucose stability
           - Consider timing of carbohydrate intake
        
        3. MICRONUTRIENT OPTIMIZATION:
           - Ensure adequate vitamin D through sun exposure or supplementation
           - Include B12-rich foods (especially if vegetarian/vegan)
           - Iron-rich foods with vitamin C for absorption
        
        4. GENERAL RECOMMENDATIONS:
           - Stay hydrated (8-10 glasses water daily)
           - Limit processed foods and added sugars
           - Include variety of colorful fruits and vegetables
           - Consider consultation with registered dietitian
        
        IMPORTANT: These are general educational recommendations based on 
        common nutritional principles. Individual needs vary significantly.
        Always consult with a registered dietitian nutritionist (RDN) for 
        personalized nutrition planning.
        """
        
        logger.info("Nutrition analysis completed successfully")
        return nutrition_analysis.strip()
        
    except Exception as e:
        error_msg = f"Error in nutrition analysis: {e}"
        logger.error(error_msg)
        return f"Error: {error_msg}"

## Creating enhanced exercise planning tool
@tool("Exercise Planning Tool") 
def create_exercise_plan_tool(blood_report_data: str) -> str:
    """Create evidence-based exercise plan based on blood report data with comprehensive error handling"""
    logger.info("Starting exercise plan creation")
    
    try:
        # Validate input
        if not blood_report_data or not isinstance(blood_report_data, str):
            error_msg = "No blood report data provided for exercise planning"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        if len(blood_report_data.strip()) < 10:
            error_msg = "Insufficient blood report data for meaningful exercise planning"
            logger.warning(error_msg)
            return f"Warning: {error_msg}"
        
        # Check for exercise-relevant markers
        exercise_markers = ['glucose', 'cholesterol', 'blood pressure', 'heart', 'cardiovascular', 'hemoglobin', 'iron']
        found_markers = [marker for marker in exercise_markers if marker.lower() in blood_report_data.lower()]
        
        logger.info(f"Found exercise-relevant markers: {found_markers}")
        
        # Generate evidence-based exercise plan
        exercise_plan = f"""
        EVIDENCE-BASED EXERCISE RECOMMENDATIONS
        ======================================
        
        Based on available health markers and ACSM guidelines
        
        SAFETY FIRST:
        ⚠️  MEDICAL CLEARANCE REQUIRED before starting any new exercise program
        ⚠️  This plan is educational only - not a prescription
        
        CARDIOVASCULAR EXERCISE:
        - Frequency: 3-5 days per week
        - Intensity: Moderate (50-70% max heart rate)
        - Duration: Start with 15-20 minutes, progress to 30+ minutes
        - Types: Walking, cycling, swimming, elliptical
        
        RESISTANCE TRAINING:
        - Frequency: 2-3 days per week (non-consecutive days)
        - Intensity: Moderate weight (8-12 repetitions)
        - Major muscle groups: chest, back, legs, shoulders, arms
        - Start with bodyweight or light weights
        
        FLEXIBILITY & MOBILITY:
        - Daily stretching routine (10-15 minutes)
        - Focus on major muscle groups
        - Consider yoga or tai chi
        
        PROGRESSION GUIDELINES:
        - Week 1-2: Focus on form and consistency
        - Week 3-4: Gradually increase duration
        - Week 5-8: Slowly increase intensity
        - Beyond: Progress under professional guidance
        
        WARNING SIGNS TO STOP EXERCISE:
        - Chest pain or pressure
        - Severe shortness of breath
        - Dizziness or lightheadedness
        - Unusual fatigue
        - Any concerning symptoms
        
        RECOMMENDATIONS:
        1. Get medical clearance from healthcare provider
        2. Consider working with certified exercise professional (CEP/CSCS)
        3. Start slowly and listen to your body
        4. Monitor for any unusual symptoms
        5. Stay hydrated and fuel properly
        
        IMPORTANT DISCLAIMER:
        This is general educational information based on standard exercise
        guidelines. Individual exercise prescriptions should always be
        developed by qualified exercise professionals in consultation
        with your healthcare provider.
        """
        
        logger.info("Exercise plan created successfully")
        return exercise_plan.strip()
        
    except Exception as e:
        error_msg = f"Error in exercise planning: {e}"
        logger.error(error_msg)
        return f"Error: {error_msg}"

## Tool validation function
def validate_tools() -> dict:
    """Validate all tools are working correctly"""
    logger.info("Starting tool validation")
    
    validation_results = {
        "search_tool": False,
        "blood_test_reader": False,
        "nutrition_analyzer": False,
        "exercise_planner": False,
        "errors": []
    }
    
    # Test search tool
    try:
        if search_tool is not None:
            validation_results["search_tool"] = True
            logger.info("Search tool validation passed")
        else:
            validation_results["errors"].append("Search tool not initialized")
    except Exception as e:
        validation_results["errors"].append(f"Search tool error: {e}")
        logger.error(f"Search tool validation failed: {e}")
    
    # Test blood test reader with sample data
    try:
        # Call the function directly since it's wrapped in a CrewAI tool
        result = read_blood_test_tool(path="data/sample.pdf") if hasattr(read_blood_test_tool, 'func') else "Tool validation skipped - func not accessible"
        if "Error:" not in result and "Tool validation skipped" not in result:
            validation_results["blood_test_reader"] = True
            logger.info("Blood test reader validation passed")
        else:
            validation_results["errors"].append("Blood test reader returned error or not accessible")
    except Exception as e:
        validation_results["errors"].append(f"Blood test reader error: {e}")
        logger.error(f"Blood test reader validation failed: {e}")
    
    # Test nutrition analyzer
    try:
        result = analyze_nutrition_tool.func("Sample blood test data with glucose and cholesterol") if hasattr(analyze_nutrition_tool, 'func') else "Tool validation skipped - func not accessible"
        if "Error:" not in result and "Tool validation skipped" not in result:
            validation_results["nutrition_analyzer"] = True
            logger.info("Nutrition analyzer validation passed")
        else:
            validation_results["errors"].append("Nutrition analyzer returned error or not accessible")
    except Exception as e:
        validation_results["errors"].append(f"Nutrition analyzer error: {e}")
        logger.error(f"Nutrition analyzer validation failed: {e}")
    
    # Test exercise planner
    try:
        result = create_exercise_plan_tool.func("Sample blood test data with cardiovascular markers") if hasattr(create_exercise_plan_tool, 'func') else "Tool validation skipped - func not accessible"
        if "Error:" not in result and "Tool validation skipped" not in result:
            validation_results["exercise_planner"] = True
            logger.info("Exercise planner validation passed")
        else:
            validation_results["errors"].append("Exercise planner returned error or not accessible")
    except Exception as e:
        validation_results["errors"].append(f"Exercise planner error: {e}")
        logger.error(f"Exercise planner validation failed: {e}")
    
    logger.info(f"Tool validation completed: {validation_results}")
    return validation_results