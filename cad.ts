// File: supabase/functions/analyzeAndGenerateScript/index.ts
// Import the 'serve' function from Deno's standard HTTP server module.
// This function is used to create and run the Edge Function server.
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
// Start the server and define the request handler as an asynchronous function.
serve(async (req)=>{
  try {
    // Parse the JSON body of the incoming request to extract 'script' and 'prompt'.
    const { script, prompt } = await req.json();
    // Validate that both 'script' and 'prompt' are provided in the request body.
    if (!script || !prompt) {
      return new Response(JSON.stringify({
        error: "Missing 'script' or 'prompt' in request body."
      }), {
        status: 400,
        headers: {
          "Content-Type": "application/json"
        }
      });
    }
    // Retrieve the Anthropic API key from the environment variables.
    const anthropicApiKey = Deno.env.get("ANTHROPIC_API_KEY");
    if (!anthropicApiKey) {
      return new Response(JSON.stringify({
        error: "Anthropic API key not configured."
      }), {
        status: 500,
        headers: {
          "Content-Type": "application/json"
        }
      });
    }
    // Construct the prompt to guide Claude's response.
    const promptText = `
You are a CAD automation expert proficient in SmartAssembly scripting.

Please explain the following SmartAssembly script:

${script}

Based on the above script, generate a new script that fulfills the following requirement:

${prompt}
`;
    // Make a POST request to Anthropic's API with the constructed prompt.
    const response = await fetch("https://api.anthropic.com/v1/complete", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${anthropicApiKey}`,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
      },
      body: JSON.stringify({
        model: "claude-3-sonnet-20240229",
        prompt: promptText,
        max_tokens_to_sample: 1000,
        temperature: 0.7 // Set the creativity level of the AI's response.
      })
    });
    // Check if the response from Anthropic's API is successful.
    if (!response.ok) {
      const errorText = await response.text();
      return new Response(JSON.stringify({
        error: `Anthropic API error: ${errorText}`
      }), {
        status: 500,
        headers: {
          "Content-Type": "application/json"
        }
      });
    }
    // Parse the JSON response from Anthropic's API.
    const data = await response.json();
    // Extract the AI-generated content from the response.
    const aiResponse = data.completion;
    // Return the AI-generated content as a JSON response.
    return new Response(JSON.stringify({
      result: aiResponse
    }), {
      status: 200,
      headers: {
        "Content-Type": "application/json"
      }
    });
  } catch (error) {
    // Handle any unexpected errors that occur during processing.
    return new Response(JSON.stringify({
      error: error.message
    }), {
      status: 500,
      headers: {
        "Content-Type": "application/json"
      }
    });
  }
});
