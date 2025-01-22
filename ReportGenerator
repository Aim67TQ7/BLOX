import fs from 'fs';
import path from 'path';
import { format } from 'date-fns';
import * as XLSX from 'xlsx';

interface Assessment {
    timestamp: string;
    totalScore: number;
    scores: {
        "5s": Record<string, { score: number; observations: string }>;
        safety: Record<string, { score: number; observations: string }>;
    };
    positiveFindings?: string[];
    areasOfConcern?: string[];
    safetyHazards?: string[];
    recommendations: {
        immediate?: string[];
        shortTerm?: string[];
        longTerm?: string[];
    };
}

interface Area {
    name: string;
    imagePath: string;
    department?: string;
    assessedBy?: string;
}

class ReportGenerator {
    private outputDir: string;

    constructor(outputDir = "data/reports") {
        this.outputDir = path.resolve(outputDir);
        if (!fs.existsSync(this.outputDir)) {
            fs.mkdirSync(this.outputDir, { recursive: true });
        }
    }

    private getTimestamp(): string {
        return format(new Date(), 'yyyyMMdd_HHmmss');
    }

    public createTextReport(assessment: Assessment, area: Area): string {
        const timestamp = this.getTimestamp();
        const filename = path.join(this.outputDir, `5S_Assessment_${area.name}_${timestamp}.txt`);

        const lines: string[] = [];

        lines.push("5S and Safety Assessment Report");
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

        // Add Safety Components
        lines.push("\nSafety Components (40 points):");
        lines.push("-".repeat(40));
        for (const [category, data] of Object.entries(assessment.scores.safety)) {
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

        // Safety Hazards
        if (assessment.safetyHazards?.length) {
            lines.push("\nCRITICAL SAFETY HAZARDS:");
            lines.push("-".repeat(40));
            assessment.safetyHazards.forEach(hazard => lines.push(`! ${hazard}`));
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
            ...Object.entries(assessment.scores.safety).map(([category, data]) => ({
                Component: "Safety",
                Category: category,
                Score: data.score,
                MaxScore: 10,
                Observations: data.observations,
            })),
        ];

        // Prepare findings and recommendations
        const findings = {
            Category: ["Positive Findings", "Areas of Concern", "Safety Hazards"],
            Items: [
                assessment.positiveFindings?.join("\n") || "",
                assessment.areasOfConcern?.join("\n") || "",
                assessment.safetyHazards?.join("\n") || "",
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

    public batchExport(assessment: Assessment, area: Area): Record<string, string> {
        return {
            text: this.createTextReport(assessment, area),
            excel: this.createExcelReport(assessment, area),
            json: this.saveJsonData(assessment, area),
        };
    }
}

export default ReportGenerator;
