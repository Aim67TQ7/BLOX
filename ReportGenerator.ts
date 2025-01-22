/**
 * Purpose of the Code:
 * - This code helps generate different types of reports (text, Excel, and JSON) for 5S and Hazard assessments.
 * - It organizes data about scores, observations, and recommendations into user-friendly formats.
 * - Makes it easy to store, share, and review the assessment information.
 * - Handles:
 *   - Text report generation for easy reading.
 *   - Excel report creation for structured data analysis.
 *   - JSON report saving for further programmatic processing.
 */

import fs from 'fs';
import path from 'path';
import { format } from 'date-fns';
import * as XLSX from 'xlsx';

// Describes the structure of the assessment data
interface Assessment {
    timestamp: string; // When the assessment was done
    totalScore: number; // Overall score out of 100
    scores: {
        "5s": Record<string, { score: number; observations: string }>; // 5S scores and notes
        hazard: Record<string, { score: number; observations: string }>; // Hazard scores and notes
    };
    positiveFindings?: string[]; // List of good things observed
    areasOfConcern?: string[]; // List of issues found
    criticalHazards?: string[]; // Critical problems
    recommendations: {
        immediate?: string[]; // Actions to do right away
        shortTerm?: string[]; // Actions to do in 1-2 weeks
        longTerm?: string[]; // Actions to do in 1-3 months
    };
}

// Describes the structure of the area being assessed
interface Area {
    name: string; // Name of the area
    imagePath: string; // Path to an image of the area
    department?: string; // Name of the department
    assessedBy?: string; // Name of the person who did the assessment
}

class ReportGenerator {
    private outputDir: string; // Folder to save the reports

    constructor(outputDir = "data/reports") {
        this.outputDir = path.resolve(outputDir);
        if (!fs.existsSync(this.outputDir)) {
            fs.mkdirSync(this.outputDir, { recursive: true }); // Create the folder if it doesn't exist
        }
    }

    // Get the current date and time in a specific format for filenames
    private getTimestamp(): string {
        return format(new Date(), 'yyyyMMdd_HHmmss');
    }

    // Create a text report
    public createTextReport(assessment: Assessment, area: Area): string {
        const timestamp = this.getTimestamp();
        const filename = path.join(this.outputDir, `5S_Assessment_${area.name}_${timestamp}.txt`);

        const lines: string[] = [];

        // Add header information
        lines.push("5S and Hazard Assessment Report");
        lines.push("==============================\n");
        lines.push(`Area: ${area.name}`);
        lines.push(`Date: ${assessment.timestamp}`);

        if (area.department) lines.push(`Department: ${area.department}`);
        if (area.assessedBy) lines.push(`Assessed By: ${area.assessedBy}`);

        lines.push(`\nTotal Score: ${assessment.totalScore}/100`);

        // Add 5S Components
        lines.push("\n5S Components (60 points):");
        lines.push("-".repeat(40));
        for (const [category, data] of Object.entries(assessment.scores["5s"])) {
            lines.push(`${category.charAt(0).toUpperCase() + category.slice(1)}: ${data.score}/12 points`);
            lines.push(`Observations: ${data.observations}\n`);
        }

        // Add Hazard Components
        lines.push("\nHazard Components (40 points):");
        lines.push("-".repeat(40));
        for (const [category, data] of Object.entries(assessment.scores.hazard)) {
            lines.push(`${category.replace('_', ' ')}: ${data.score}/10 points`);
            lines.push(`Observations: ${data.observations}\n`);
        }

        // Positive Findings
        if (assessment.positiveFindings?.length) {
            lines.push("\nPositive Findings:");
            lines.push("-".repeat(40));
            assessment.positiveFindings.forEach(finding => lines.push(`• ${finding}`));
        }

        // Areas of Concern
        if (assessment.areasOfConcern?.length) {
            lines.push("\nAreas of Concern:");
            lines.push("-".repeat(40));
            assessment.areasOfConcern.forEach(concern => lines.push(`• ${concern}`));
        }

        // Critical Hazards
        if (assessment.criticalHazards?.length) {
            lines.push("\nCRITICAL HAZARDS:");
            lines.push("-".repeat(40));
            assessment.criticalHazards.forEach(hazard => lines.push(`! ${hazard}`));
        }

        // Recommendations
        lines.push("\nRecommended Actions:");
        lines.push("-".repeat(40));

        if (assessment.recommendations.immediate?.length) {
            lines.push("\nImmediate Actions (24-48 hours):");
            assessment.recommendations.immediate.forEach(action => lines.push(`• ${action}`));
        }

        if (assessment.recommendations.shortTerm?.length) {
            lines.push("\nShort-term Improvements (1-2 weeks):");
            assessment.recommendations.shortTerm.forEach(action => lines.push(`• ${action}`));
        }

        if (assessment.recommendations.longTerm?.length) {
            lines.push("\nLong-term Initiatives (1-3 months):");
            assessment.recommendations.longTerm.forEach(action => lines.push(`• ${action}`));
        }

        fs.writeFileSync(filename, lines.join('\n'));
        return filename;
    }

    // Create an Excel report
    public createExcelReport(assessment: Assessment, area: Area): string {
        const timestamp = this.getTimestamp();
        const filename = path.join(this.outputDir, `5S_Assessment_${area.name}_${timestamp}.xlsx`);

        // Prepare scores data
        const scoresData = [
            ...Object.entries(assessment.scores["5s"]).map(([category, data]) => ({
                Component: "5S",
                Category: category,
                Score: data.score,
                MaxScore: 12,
                Observations: data.observations,
            })),
            ...Object.entries(assessment.scores.hazard).map(([category, data]) => ({
                Component: "Hazard",
                Category: category,
                Score: data.score,
                MaxScore: 10,
                Observations: data.observations,
            })),
        ];

        // Prepare findings and recommendations
        const findings = {
            Category: ["Positive Findings", "Areas of Concern", "Critical Hazards"],
            Items: [
                assessment.positiveFindings?.join("\n") || "",
                assessment.areasOfConcern?.join("\n") || "",
                assessment.criticalHazards?.join("\n") || "",
            ],
        };

        const recommendations = {
            Timeframe: [],
            Actions: [],
        };

        ["immediate", "shortTerm", "longTerm"].forEach(key => {
            const actions = assessment.recommendations[key as keyof Assessment["recommendations"]];
            if (actions) {
                recommendations.Timeframe.push(...Array(actions.length).fill(key));
                recommendations.Actions.push(...actions);
            }
        });

        const workbook = XLSX.utils.book_new();
        const scoresSheet = XLSX.utils.json_to_sheet(scoresData);
        const findingsSheet = XLSX.utils.json_to_sheet(findings);
        const recommendationsSheet = XLSX.utils.json_to_sheet(recommendations);

        XLSX.utils.book_append_sheet(workbook, scoresSheet, "Scores");
        XLSX.utils.book_append_sheet(workbook, findingsSheet, "Findings");
        XLSX.utils.book_append_sheet(workbook, recommendationsSheet, "Recommendations");

        XLSX.writeFile(workbook, filename);
        return filename;
    }

    // Save the assessment data in JSON format
    public saveJsonData(assessment: Assessment, area: Area): string {
        const timestamp = this.getTimestamp();
        const filename = path.join(this.outputDir, `5S_Assessment_${area.name}_${timestamp}.json`);

        const data = {
            area,
            assessment,
        };

        fs.writeFileSync(filename, JSON.stringify(data, null, 4));
        return filename;
    }

    // Generate all report formats (text, Excel, JSON)
    public batchExport(assessment: Assessment, area: Area): Record<string, string> {
        return {
            text: this.createTextReport(assessment, area),
            excel: this.createExcelReport(assessment, area),
            json: this.saveJsonData(assessment, area),
        };
    }
}

export default ReportGenerator;
