#!/usr/bin/env node

// This script is a Node.js application for conducting 5S workplace assessments and generating reports. 
// It allows users to input details about a workplace area, process images, and generate detailed
// assessments and recommendations based on the 5S methodology.
// However, the script itself does not actively "do" anything until a user runs it with specific inputs.
// Its purpose is to serve as a framework for organizing data, performing analyses, and generating outputs.

import { existsSync, mkdirSync } from 'fs';
import { join } from 'path';
import { program } from 'commander';
import { 
  getAssessmentDir,
  getAssessmentFilePath,
  getImagesDir,
  getReportsDir,
  getConfigFilePath,
  getDbFilePath,
  getUploadedImagePath,
  getUploadedImagesDir,
  getAssessmentReportFilePath,
  getAssessmentCsvFilePath
} from './utils/paths';
import { 
  createAssessmentDir,
  createAssessmentFile,
  createAssessmentReportFile,
  createAssessmentCsvFile
} from './utils/file-handler';
import { 
  getAssessment,
  getAssessmentDetails,
  saveAssessment
} from './services/assessment';
import { 
  readApiKey,
  readConfig
} from './utils/config-reader';
import { 
  processImage 
} from './services/image-processor';
import { 
  generateAssessmentReport 
} from './services/report-generator';
import { 
  createDb
} from './utils/db-setup';
import { 
  Area,
  AssessmentDetails
} from './models/assessment';
import { 
  AssessmentResponse,
  AssessmentScore,
  AssessmentSafetyHazard
} from './models/assessment-response';
import { 
  AssessmentReport
} from './models/assessment-report';

// The following section allows the user to provide inputs (like area name and image path) when running the script.
program
  .option('-a, --area <name>', 'Name of the area being assessed') // User specifies the area being analyzed.
  .option('-i, --image <path>', 'Path to the image file') // User provides a photo of the area for analysis.
  .option('-d, --department <name>', 'Name of the department') // Add the name of the department for organization.
  .option('-as, --assessor <name>', 'Name of the assessor') // Add the name of the person performing the assessment.
  .requiredOption('-c, --config <path>', 'Path to the configuration file') // The configuration file is required for setup.
  .parse(process.argv);

// These variables store user inputs.
const areaName = program.opts().area; // The area being evaluated.
const imagePath = program.opts().image; // The image path provided by the user.
const department = program.opts().department; // The department associated with the assessment.
const assessor = program.opts().assessor; // The person conducting the assessment.
const configFilePath = program.opts().config; // Path to the necessary configuration file.

// Ensure the configuration file exists before proceeding.
if (!existsSync(configFilePath)) {
  console.error('Error: Configuration file not found.'); // If missing, stop the script.
  process.exit(1);
}

// Load the configuration settings and API key needed for analysis.
const config = readConfig(configFilePath); // Read settings from the provided configuration file.
const apiKey = readApiKey(); // Retrieve the API key for interacting with external services.

// Prepare the database for storing assessment data.
createDb(getDbFilePath()); // Initialize or check the database.

// Create the necessary directories if they don’t exist.
createAssessmentDir(getAssessmentDir()); // Folder for assessment data.
createAssessmentDir(getImagesDir()); // Folder for images.
createAssessmentDir(getReportsDir()); // Folder for reports.
createAssessmentDir(getUploadedImagesDir()); // Folder for uploaded images.

// Process the user-provided image, if applicable.
let processedImagePath = ''; // This will store the processed image path.
let timestamp = ''; // Timestamp when the image was processed.
if (imagePath) {
  try {
    processedImagePath = getUploadedImagePath(imagePath); // Prepare the image for upload.
    timestamp = processImage(imagePath, processedImagePath); // Compress and timestamp the image.
  } catch (error) {
    console.error('Error processing image:', error); // Report any issues with image processing.
    process.exit(1);
  }
}

// Collect details about the assessment.
const assessmentDetails: AssessmentDetails = {
  area: areaName, // Name of the area being assessed.
  image_path: processedImagePath, // Path to the image used for assessment.
  department: department, // Associated department.
  assessed_by: assessor, // Name of the person conducting the assessment.
  timestamp: timestamp // Time of assessment.
};

// Create an area object to represent the assessment.
const area = new Area(assessmentDetails);

// Perform the assessment using external tools or APIs.
const assessmentResponse: AssessmentResponse = getAssessment(area, apiKey); // Fetch results from the AI system.
let assessment: AssessmentScore = {}; // To store scores for the 5S principles.
let assessmentSafetyHazards: AssessmentSafetyHazard[] = []; // To store identified safety hazards.
let assessmentRecommendations: Record<string, string[]> = {}; // To store recommendations for improvement.
if (assessmentResponse) {
  assessment = assessmentResponse.scores; // Extract the scores from the response.
  assessmentSafetyHazards = assessmentResponse.safety_hazards; // Extract safety hazard information.
  assessmentRecommendations = assessmentResponse.recommendations; // Extract improvement suggestions.
}

// Save assessment details to files and database.
createAssessmentFile(getAssessmentFilePath(areaName, timestamp), assessmentDetails); // Save assessment details as a file.
saveAssessment(areaName, timestamp, assessment, assessmentSafetyHazards, assessmentRecommendations); // Store the results in the database.

// Generate reports for the assessment.
const assessmentReport: AssessmentReport = generateAssessmentReport(assessmentDetails, assessment, assessmentSafetyHazards, assessmentRecommendations); // Create a report object.
createAssessmentReportFile(getAssessmentReportFilePath(areaName, timestamp), assessmentReport); // Save the report as a file.
createAssessmentCsvFile(getAssessmentCsvFilePath(areaName, timestamp), assessment); // Save the assessment in CSV format.

// Display results and notify the user where files are saved.
console.log('Assessment Results:');
console.log(assessmentDetails); // Show basic assessment details.
console.log(assessment); // Show 5S scores.
console.log(assessmentSafetyHazards); // Show safety hazard details.
console.log(assessmentRecommendations); // Show improvement recommendations.
console.log(`Assessment files saved to ${getAssessmentDir()}`); // Inform the user of saved locations.
