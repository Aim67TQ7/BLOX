# Purpose of the Code:
# - This code helps generate different types of reports (text, Excel, and JSON) for 5S and Hazard assessments.
# - It organizes data about scores, observations, and recommendations into user-friendly formats.
# - Makes it easy to store, share, and review the assessment information.
# - Handles:
#   - Text report generation for easy reading.
#   - Excel report creation for structured data analysis.
#   - JSON report saving for further programmatic processing.

import os
import json
from datetime import datetime
import pandas as pd

class ReportGenerator:
    def __init__(self, output_dir="data/reports"):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)  # Create the folder if it doesn't exist

    def get_timestamp(self):
        # Get the current date and time in a specific format for filenames
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def create_text_report(self, assessment, area):
        # Create a text report
        timestamp = self.get_timestamp()
        filename = os.path.join(self.output_dir, f"5S_Assessment_{area['name']}_{timestamp}.txt")

        lines = []

        # Add header information
        lines.append("5S and Hazard Assessment Report")
        lines.append("==============================\n")
        lines.append(f"Area: {area['name']}")
        lines.append(f"Date: {assessment['timestamp']}")

        if area.get('department'):
            lines.append(f"Department: {area['department']}")
        if area.get('assessedBy'):
            lines.append(f"Assessed By: {area['assessedBy']}")

        lines.append(f"\nTotal Score: {assessment['totalScore']}/100")

        # Add 5S Components
        lines.append("\n5S Components (60 points):")
        lines.append("-" * 40)
        for category, data in assessment['scores']['5s'].items():
            lines.append(f"{category.capitalize()}: {data['score']}/12 points")
            lines.append(f"Observations: {data['observations']}\n")

        # Add Hazard Components
        lines.append("\nHazard Components (40 points):")
        lines.append("-" * 40)
        for category, data in assessment['scores']['hazard'].items():
            lines.append(f"{category.replace('_', ' ').capitalize()}: {data['score']}/10 points")
            lines.append(f"Observations: {data['observations']}\n")

        # Positive Findings
        if assessment.get('positiveFindings'):
            lines.append("\nPositive Findings:")
            lines.append("-" * 40)
            for finding in assessment['positiveFindings']:
                lines.append(f"• {finding}")

        # Areas of Concern
        if assessment.get('areasOfConcern'):
            lines.append("\nAreas of Concern:")
            lines.append("-" * 40)
            for concern in assessment['areasOfConcern']:
                lines.append(f"• {concern}")

        # Critical Hazards
        if assessment.get('criticalHazards'):
            lines.append("\nCRITICAL HAZARDS:")
            lines.append("-" * 40)
            for hazard in assessment['criticalHazards']:
                lines.append(f"! {hazard}")

        # Recommendations
        lines.append("\nRecommended Actions:")
        lines.append("-" * 40)

        for key, label in [("immediate", "Immediate Actions (24-48 hours):"),
                           ("shortTerm", "Short-term Improvements (1-2 weeks):"),
                           ("longTerm", "Long-term Initiatives (1-3 months):")]:
            if assessment['recommendations'].get(key):
                lines.append(f"\n{label}")
                for action in assessment['recommendations'][key]:
                    lines.append(f"• {action}")

        with open(filename, 'w') as file:
            file.write('\n'.join(lines))

        return filename

    def create_excel_report(self, assessment, area):
        # Create an Excel report
        timestamp = self.get_timestamp()
        filename = os.path.join(self.output_dir, f"5S_Assessment_{area['name']}_{timestamp}.xlsx")

        # Prepare scores data
        scores_data = []
        for category, data in assessment['scores']['5s'].items():
            scores_data.append({
                "Component": "5S",
                "Category": category,
                "Score": data['score'],
                "MaxScore": 12,
                "Observations": data['observations']
            })
        for category, data in assessment['scores']['hazard'].items():
            scores_data.append({
                "Component": "Hazard",
                "Category": category,
                "Score": data['score'],
                "MaxScore": 10,
                "Observations": data['observations']
            })

        # Prepare findings and recommendations
        findings = {
            "Category": ["Positive Findings", "Areas of Concern", "Critical Hazards"],
            "Items": [
                '\n'.join(assessment.get('positiveFindings', [])),
                '\n'.join(assessment.get('areasOfConcern', [])),
                '\n'.join(assessment.get('criticalHazards', []))
            ]
        }

        recommendations = []
        for key, label in [("immediate", "Immediate"), ("shortTerm", "Short Term"), ("longTerm", "Long Term")]:
            for action in assessment['recommendations'].get(key, []):
                recommendations.append({"Timeframe": label, "Action": action})

        # Write to Excel
        with pd.ExcelWriter(filename) as writer:
            pd.DataFrame(scores_data).to_excel(writer, sheet_name="Scores", index=False)
            pd.DataFrame(findings).to_excel(writer, sheet_name="Findings", index=False)
            pd.DataFrame(recommendations).to_excel(writer, sheet_name="Recommendations", index=False)

        return filename

    def save_json_data(self, assessment, area):
        # Save the assessment data in JSON format
        timestamp = self.get_timestamp()
        filename = os.path.join(self.output_dir, f"5S_Assessment_{area['name']}_{timestamp}.json")

        data = {
            "area": area,
            "assessment": assessment
        }

        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

        return filename

    def batch_export(self, assessment, area):
        # Generate all report formats (text, Excel, JSON)
        return {
            "text": self.create_text_report(assessment, area),
            "excel": self.create_excel_report(assessment, area),
            "json": self.save_json_data(assessment, area)
        }
