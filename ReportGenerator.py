/**
 * Hey there! This module is all about calculating scores for workplace evaluations using the 5S method.
 * 5S is a way to keep workplaces organized and safe.
 * It also creates reports that are easy to read and share.
 */

import { Score } from "@/types/evaluation";

/**
 * This function adds up all the scores to get a total score.
 * It's like adding up grades to get your final score in school!
 *
 * @param scores - These are the scores for different 5S categories.
 * @returns The total score after checking all the rules.
 */
export const calculateTotalScore = (scores: Score): number => {
  // Make sure the scores stay between allowed numbers.
  const normalizedScores = {
    sort: Math.min(10, Math.max(1, scores.sort)),
    setInOrder: Math.min(10, Math.max(1, scores.setInOrder)),
    shine: Math.min(10, Math.max(1, scores.shine)),
    standardize: Math.min(10, Math.max(0, scores.standardize)),
    sustain: Math.min(10, Math.max(0, scores.sustain)),
  };

  // Add up the mandatory scores first.
  const baseScore = normalizedScores.sort + normalizedScores.setInOrder + normalizedScores.shine;

  // If the base score is too low, ignore the optional scores.
  if (baseScore < 22) {
    return baseScore;
  }

  // Add optional scores if the base score is high enough.
  return baseScore + normalizedScores.standardize + normalizedScores.sustain;
};

/**
 * This function calculates the percentage score.
 * It's like converting your test score into a percentage for your report card!
 *
 * @param totalScore - The total score from all categories.
 * @returns A percentage score (from 0 to 100).
 */
export const calculatePercentageScore = (totalScore: number): number => {
  const maxPossibleScore = 50; // The highest score you can get is 50.
  return Math.round((totalScore / maxPossibleScore) * 100);
};

/**
 * This function makes sure all scores follow the rules and fixes them if needed.
 * It's like a teacher checking your answers and correcting them!
 *
 * @param scores - These are the scores for different 5S categories.
 * @returns Scores that follow all the rules.
 */
export const getAdjustedScores = (scores: Score): Score => {
  // Make sure all scores stay within their allowed range.
  const normalizedScores = {
    sort: Math.min(10, Math.max(1, scores.sort)),
    setInOrder: Math.min(10, Math.max(1, scores.setInOrder)),
    shine: Math.min(10, Math.max(1, scores.shine)),
    standardize: Math.min(10, Math.max(0, scores.standardize)),
    sustain: Math.min(10, Math.max(0, scores.sustain)),
  };

  // Add up the mandatory scores.
  const baseScore = normalizedScores.sort + normalizedScores.setInOrder + normalizedScores.shine;

  // If the base score is too low, reset optional scores to 0.
  if (baseScore < 22) {
    return {
      sort: normalizedScores.sort,
      setInOrder: normalizedScores.setInOrder,
      shine: normalizedScores.shine,
      standardize: 0,
      sustain: 0,
    };
  }

  // Return the scores if everything is fine.
  return normalizedScores;
};

/**
 * This function creates a simple text report about the evaluation.
 * It's like a summary of your scores and performance!
 *
 * @param scores - These are the scores for different 5S categories.
 * @param area - The name of the area being evaluated.
 * @returns A text report as a string.
 */
export const createTextReport = (scores: Score, area: string): string => {
  const adjustedScores = getAdjustedScores(scores);
  const totalScore = calculateTotalScore(adjustedScores);
  const percentageScore = calculatePercentageScore(totalScore);

  let report = "5S Evaluation Report\n";
  report += "====================\n";
  report += `Area: ${area}\n`;
  report += `Total Score: ${totalScore}/50\n`;
  report += `Percentage Score: ${percentageScore}%\n\n`;

  report += "Individual Scores:\n";
  report += `Sort: ${adjustedScores.sort}/10\n`;
  report += `Set In Order: ${adjustedScores.setInOrder}/10\n`;
  report += `Shine: ${adjustedScores.shine}/10\n`;
  report += `Standardize: ${adjustedScores.standardize}/10\n`;
  report += `Sustain: ${adjustedScores.sustain}/10\n`;

  return report;
};

/**
 * This function creates all the reports (text and JSON) for the evaluation.
 * It's like having all your report cards ready to go!
 *
 * @param scores - These are the scores for different 5S categories.
 * @param area - The name of the area being evaluated.
 * @returns An object containing both text and JSON reports.
 */
export const generateReports = (scores: Score, area: string): { text: string; json: string } => {
  const adjustedScores = getAdjustedScores(scores);
  const totalScore = calculateTotalScore(adjustedScores);
  const percentageScore = calculatePercentageScore(totalScore);

  const textReport = createTextReport(scores, area);

  const jsonReport = JSON.stringify(
    {
      area,
      scores: adjustedScores,
      totalScore,
      percentageScore,
    },
    null,
    2
  );

  return { text: textReport, json: jsonReport };
};
