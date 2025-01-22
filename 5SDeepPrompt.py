import { DateTime } from 'luxon';
import { Anthropic } from 'anthropic';
import { ImageProcessor } from './utils/image-processor';

export interface Area {
  name: string;
  imagePath: string;
  department?: string;
  assessedBy?: string;
  date?: string;
}

export interface Assessment {
  timestamp: string;
  areaName: string;
  scores: { [key: string]: { score: number; observations: string } };
  observations: { [key: string]: string };
  totalScore: number;
  safetyHazards: {
    severity: string;
    description: string;
    deduction: number;
    location: string;
    recommendation: string;
  }[];
  recommendations: {
    immediate: string[];
    shortTerm: string[];
    longTerm: string[];
  };
}

export class BasicSpaceAnalyzer {
  private anthropic: Anthropic;

  constructor(apiKey: string) {
    this.anthropic = new Anthropic({ apiKey });
  }

  private async checkImageFile(imagePath: string): Promise<boolean> {
    try {
      // Use fs module to check file existence and readability in Node.js
      const fs = require('fs');
      if (!fs.existsSync(imagePath)) {
        console.error(`Error: Image file '${imagePath}' not found!`);
        return false;
      }

      // Read the file to check for readability
      fs.readFileSync(imagePath);
      return true;
    } catch (error) {
      console.error(`Error checking image file: ${error}`);
      return false;
    }
  }

  async analyzeImage(imagePath: string, maxRetries = 3): Promise<Assessment | null> {
    if (!(await this.checkImageFile(imagePath))) {
      return null;
    }

    let retryCount = 0;
    let compressedImagePath: string | null = null;

    while (retryCount < maxRetries) {
      try {
        // Compress image if needed
        if (!compressedImagePath || !(await ImageProcessor.verifySize(compressedImagePath))) {
          console.log('Compressing image...');
          compressedImagePath = await ImageProcessor.compressImage(imagePath, 3);

          // Verify the compression worked
          if (!(await ImageProcessor.verifySize(compressedImagePath))) {
            console.warn('Warning: Unable to compress image sufficiently');
            return null;
          }
        }

        // Read and encode compressed image
        const imageData = await ImageProcessor.readAndEncodeImage(compressedImagePath);

        const actualSizeMb = imageData.length / 1024 / 1024;
        console.log(`Sending image to Claude (size: ${actualSizeMb.toFixed(2)}MB)`);

        // Prepare the prompt for 5S analysis
        const prompt = `Analyze this workplace image for 5S using a 60-point scoring system:

 
                5S Components (50 points total):
                Sort (10 points total): Evaluate the organization and removal of unnecessary items in all areas.
                    * Look for: 
                      - **Furniture & Equipment**: Are work benches, carts, machines, equipment, cabinets, tool boxes, shelves, and other fixtures free from unnecessary items? Ensure that the workspace is clear of clutter and excess items that do not contribute to the task at hand.
                      - **PPE (Personal Protective Equipment)**: Are all safety gloves, armguards, safety glasses, ear plugs, aprons, and similar equipment in the area necessary? Only required PPE should be in the designated workspace, while unnecessary or expired items should be removed.
                      - **Documents**: Are unauthorized or outdated instructions, visual aids, inspection forms, and work instructions removed from the work area? Keep only current, relevant documents accessible to reduce confusion and maintain accurate standards.
                      - **Floor & Walk Aisles**: Are floors and workstation surfaces free of unnecessary hardware, parts, papers, cardboard, metal, pens, debris, and trash? Ensure that walkways are clear for safe movement and that all items are properly stored to prevent trip hazards.
                      - **Cleaning Equipment**: Is all cleaning equipment, such as rags, mops, mop buckets, brooms, dust pans, cleaning solutions, and floor mats, necessary for the area? Only essential cleaning items should be present; remove anything that is not needed for daily operations or maintenance.
                      - **Tools, Fixtures, Gages, Hand Tools**: Are only necessary tools needed to perform workstation jobs present, such as fixtures, gauges, air wrenches, and other hand tools? Ensure tools are organized and that only those required for current tasks are stored in the workspace.
                      - **Part Containers**: Are only the necessary part containers, such as colored totes, wire baskets, tote pans, and returnable totes, located in the area? Eliminate extra or unused containers to streamline workflow and prevent clutter.
                      - **Personal Items**: Have personal items, such as lunch boxes, drinks, newspapers, food, or magazines, been removed from the immediate working area? Coats and jackets are allowed during cold weather due to frequently opening doors but should be stored properly to avoid interference with work activities.
                      - **Trash, Scrap, and Rework**: Has all trash, scrap, rework, and their respective containers been removed from the area? Ensure prompt disposal of waste materials to maintain a clean and safe environment.
                      - **Inventory and Work In Process (WIP)**: Is the area free of excess inventory and parts? Check that inventory levels are within specified min/max limits, and excess containers or shelves are not storing unneeded items.

                Set in Order (10 points total): Logical placement and visual organization
                    * Look for: 
                      - **Furniture & Equipment**: Are tables, containers, bins, parts, racks, carts, cabinets, tool boxes, shelves, and other structures foot printed and labeled? Ensure that all items are in designated and clearly labeled locations to maintain organization.
                      - **PPE (Personal Protective Equipment)**: Is emergency equipment easily identified at a glance and arranged for ease of access? Are E-stops easily identified and positioned so team members can quickly access them? Is all emergency equipment labeled and located appropriately within the department?
                      - **Emergency Exits and Panels**: Are emergency exits, first-aid stations, electrical panels, and hazardous materials appropriately identified, labeled, and accessible?
                      - **Documentation**: Are visual aids, inspection instructions, work instructions, and the 5S checklist in a designated labeled location? Ensure that documents are accessible and labeled to provide clarity and guidance to all workers.
                      - **Floor & Walk Aisles**: Are floors and walk aisles clearly foot printed and labeled using proper color guidelines? Ensure that walkways are marked clearly to avoid confusion and to guide safe movement throughout the workspace.
                      - **Cleaning Equipment**: Are rags, mops, mop buckets, brooms, dust pans, and cleaning solutions labeled and footprinted in the designated location? Make sure cleaning supplies are organized, labeled, and accessible for maintenance purposes.
                      - **Tools, Fixtures, Gages, Hand Tools**: Are tools, fixtures, tuggers, gauges, air wrenches, and other necessary tools in their designated locations? Ensure tools are easily accessible and stored where they belong.
                      - **Part Containers**: Are part containers such as colored totes, wire baskets, tote pans, and returnable totes labeled with part names and numbers? Is the shelving that part containers sit on also labeled to match the part container? Proper labeling helps in quick identification and reduces errors.
                      - **Personal Items**: Are personal items in their designated locations? Ensure personal belongings do not interfere with work processes and are stored in a designated area.
                      - **Inventory and WIP**: Are standard WIP levels indicated at the workstation with labels or by right-sizing containers? Are inventory levels marked by min/max indicators where applicable? Ensure that inventory and WIP are organized, clearly labeled, and stored in appropriate quantities to avoid overstock or stockouts.

                Shine (10 points): Cleanliness and workspace maintenance
                    * Look for: 
                      - **Work Stations**: Are all items on work stations in their proper location and are they clean? Ensure Personal Protective Equipment (PPE), WIP containers, tools, floors, desks, carts, fixtures, and rework areas are organized and free of dust or debris.
                      - **Machines, Equipment & Tooling**: Are all equipment, work benches, tuggers, baskets, bins, totes, etc., clean and in their designated location? Check for cleanliness and proper organization to maintain safe and efficient operations.
                      - **On-line Production Material, Supplies & Parts Storage**: Are all on-line production materials, supplies, and part containers clean and in their designated locations? Ensure that materials are easy to find and free from dirt or contamination.
                      - **Tool Boards**: Are all tools in the designated location on the tool boards and are all tools and tool boards clean? Confirm that tools are organized and surfaces are clean to facilitate easy access and visual control.
                      - **Off-Line Storage**: Are all items on racks, dies, carts, fixtures, floors, etc., in off-line storage areas clean and in their designated locations? Ensure that items not currently in use are properly stored and that storage areas are maintained in a clean condition.
                      - **On-Line Cabinets, Shelving**: Are cabinets and files clean and in their designated locations? Make sure that documents and supplies are neatly stored, labeled, and free from dust.
                      - **Inventory Storage Areas**: Are inventory storage areas such as staging areas, material holding areas, and quality defect holding areas/items clean and in their designated location? Proper organization and cleanliness are key for efficient handling and defect reduction.
                      - **Information Boards**: Is all posted information on performance boards and communication boards clean and in the right location? Keep boards tidy and updated for effective communication.
                      - **Pull System**: Are all items in supermarkets/grocery stores in the proper place, and are procedures in place to replenish the system? Ensure the replenishment process is clearly documented and items are clean and organized.
                      - **Safety and Quality Related Controls**: Have visual aids for appropriate safety and quality concerns been documented visually? Make sure all safety signs, quality reminders, and visual aids are clearly visible, clean, and in good condition.

                Standardize (10 points): Visual management and procedures
                    * Look for: 
                      - **Work Stations**: Are all items on workstations standardized for location, and is there visual management in place to indicate proper placement? Are labels and markings consistently applied across all workstations?
                      - **PPE, WIP Containers, and Tools**: Are Personal Protective Equipment, WIP containers, and tools consistently stored and labeled throughout the workplace? Are standards clearly communicated to all team members?
                      - **Machines, Equipment & Tooling**: Is there a consistent method for organizing and labeling machines, work benches, and tooling? Ensure standardized labeling is used for all equipment.
                      - **Production Materials, Supplies & Parts Storage**: Are standardized labels used for production materials, supplies, and parts storage? Is there a consistent method for identifying the correct storage location?
                      - **Tool Boards**: Are all tool boards arranged consistently across different areas? Ensure each tool has a specific, clearly marked place, and all areas follow the same visual standards.
                      - **Off-Line Storage**: Are off-line storage standards clearly defined and followed? Check for consistent labeling, designated storage spots, and guidelines for off-line items.
                      - **On-Line Cabinets, Shelving**: Are cabinets and shelving units standardized for the type of items they store, and are all items consistently labeled? Ensure consistency in layout and labeling.
                      - **Inventory Storage Areas**: Is there a standardized approach for inventory storage, including staging areas, material holding, and defect holding areas? Confirm that all storage areas follow the same rules for item placement and labeling.
                      - **Information Boards**: Are communication and performance boards standardized across the workplace? Consistent layout, labeling, and information placement is essential for easy understanding.
                      - **Pull System**: Are replenishment systems standardized, and are visual cues for inventory and WIP levels clearly in place? Ensure that the same replenishment process and visual cues are used throughout.

                Sustain (10 points): Evidence of maintained standards
                    * Look for: 
                      - **Audit Charts**: Are audit charts up-to-date and displayed prominently? Do they show the most recent audits and indicate areas for improvement?
                      - **Maintenance Logs**: Are maintenance logs for equipment, tools, and facilities consistently updated and accessible? Do they reflect regular preventive maintenance activities?
                      - **Continuous Improvement Tracking**: Is there documentation showing continuous improvement activities such as Kaizen events, corrective actions, or other improvement initiatives? Are the results tracked and visible to the team?
                      - **Training Records**: Are records of employee training available and up to date? Do they include recent training on 5S principles, safety procedures, and equipment use?
                      - **Standard Operating Procedures (SOPs)**: Are SOPs maintained and reviewed regularly to ensure relevance and accuracy? Are there mechanisms in place to ensure adherence to these procedures?
                      - **Performance Metrics**: Are key performance indicators (KPIs) related to 5S and safety posted and updated? Are progress and goals visually communicated to all employees?
                      - **Visual Management**: Are visual management tools such as shadow boards, kanban cards, and signage maintained to sustain 5S practices? Are all visual tools updated to reflect any process changes?
                      - **Employee Involvement**: Is there evidence of employee involvement in sustaining 5S, such as suggestion boxes, regular team meetings, or recognition programs for improvements?
                      - **Regular 5S Audits**: Are regular 5S audits being conducted, and are the results reviewed with the team? Is there follow-up action to address deficiencies identified during audits?
                      - **Housekeeping Standards**: Are housekeeping standards visibly posted, and is adherence to these standards part of regular workplace routines? Ensure that housekeeping is maintained consistently over time.

                Safety Component (10 points total, with deductions):
                * Start with 10 points and deduct for violations:
                  - Minor (-1 point): Minor housekeeping issues related to safety (e.g., small clutter, missing label)
                  - Moderate (-2 points): Potential safety hazards (e.g., trip hazards, improperly stored chemicals, improper PPE use)
              - Severe (-5 points): Immediate dangers or blocked safety equipment (e.g., blocked emergency exits, exposed electrical wiring, missing or expired fire extinguishers)
""


  Provide your analysis in this exact JSON format:
                {
                    "scores": {
                        "sort": {"score": 0, "observations": "detailed findings"},
                        "set": {"score": 0, "observations": "detailed findings"},
                        "shine": {"score": 0, "observations": "detailed findings"},
                        "standardize": {"score": 0, "observations": "detailed findings"},
                        "sustain": {"score": 0, "observations": "detailed findings"},
                        "safety": {"score": 0, "observations": "detailed findings"}
                    },
                    "safety_hazards": [
                        {
                            "severity": "minor/moderate/severe",
                            "description": "specific hazard description",
                            "deduction": 0,
                            "location": "where in the image",
                            "recommendation": "how to fix"
                        }
                    ],
                    "recommendations": {
                        "immediate": ["actions needed in 24-48 hours"],
                        "short_term": ["actions needed in 1-2 weeks"],
                        "long_term": ["actions needed in 1-3 months"]
                    }
                }
`;

        // Get Claude's analysis
        const response = await this.anthropic.messages.create({
          model: 'claude-3-sonnet-20240229',
          maxTokens: 1500,
          temperature: 0,
          messages: [
            {
              role: 'user',
              content: [
                {
                  type: 'text',
                  text: prompt,
                },
                {
                  type: 'image',
                  source: {
                    type: 'base64',
                    mediaType: 'image/jpeg',
                    data: imageData,
                  },
                },
              ],
            },
          ],
        });

        // Parse response
        const analysis = JSON.parse(response.content[0].text);
        return analysis;
      } catch (error) {
        console.error(`Error parsing response: ${error}`);
        console.error(`Raw response: ${response.content}`);
        retryCount++;
        continue;
      } catch (error) {
        console.error(`Attempt ${retryCount + 1} failed: ${error}`);
        retryCount++;
        if (retryCount < maxRetries) {
          console.log('Waiting before retry...');
          await new Promise((resolve) => setTimeout(resolve, 5000)); // Wait for 5 seconds
          continue;
        }
      } finally {
        // Clean up compressed image
        if (compressedImagePath) {
          try {
            const fs = require('fs');
            fs.unlinkSync(compressedImagePath);
          } catch (error) {
            console.warn(`Warning: Could not remove temporary file ${compressedImagePath}: ${error}`);
          }
        }
      }
    }

    throw new Error('Failed to analyze image after maximum retries');
  }

  async assessArea(area: Area): Promise<Assessment | null> {
    console.log(`Analyzing image: ${area.imagePath}`);
    const analysis = await this.analyzeImage(area.imagePath);

    if (analysis) {
      // Calculate total score (including safety deductions)
      const baseScore = Object.values(analysis.scores).reduce(
        (sum, data) => sum + data.score,
        0
      );
      const safetyDeductions = analysis.safetyHazards.reduce(
        (sum, hazard) => sum + hazard.deduction,
        0
      );
      const totalScore = Math.max(0, baseScore - safetyDeductions);

      const assessment: Assessment = {
        timestamp: DateTime.now().toISO(),
        areaName: area.name,
        scores: analysis.scores,
        observations: Object.fromEntries(
          Object.entries(analysis.scores).map(([category, data]) => [
            category,
            data.observations,
          ])
        ),
        totalScore,
        safetyHazards: analysis.safetyHazards,
        recommendations: analysis.recommendations,
      };

      return assessment;
    } else {
      return null;
    }
  }

  generateImprovementPlan(assessment: Assessment): {
    [key: string]: string[];
  } {
    const plan: { [key: string]: string[] } = {
      immediate: [],
      shortTerm: [],
      longTerm: [],
    };

    // Add safety hazards to immediate actions
    for (const hazard of assessment.safetyHazards) {
      plan.immediate.push(
        `Address ${hazard.severity} safety hazard: ${hazard.description}`
      );
    }

    // Add recommendations from assessment
    for (const timeframe of ['immediate', 'shortTerm', 'longTerm']) {
      if (timeframe in assessment.recommendations) {
        plan[timeframe].push(...assessment.recommendations[timeframe]);
      }
    }
https://github.com/Aim67TQ7/_Blocks_TS/tree/main
    return plan;
  }

  async isValidImage(imagePath: string, maxSizeMb = 10): Promise<boolean> {
    try {
      if (!(await this.checkImageFile(imagePath))) {
        return false;
      }

      // Use fs module to get file size in Node.js
      const fs = require('fs');
      const fileSizeMb = fs.statSync(imagePath).size / 1024 / 1024;
      if (fileSizeMb > maxSizeMb) {
        console.warn(
          `Warning: Image file '${imagePath}' is too large (${fileSizeMb.toFixed(
            2
          )} MB). Maximum allowed size is ${maxSizeMb} MB.`
        );
        return false;
      }

      return true;
    } catch (error) {
      console.error(`Error checking image file: ${error}`);
      return false;
    }
  }
}
