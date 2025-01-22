/**
 * Purpose of the Express Server Setup:
 * - Handle Incoming Requests:
 *   This server listens for user or system requests through HTTP methods (e.g., GET, POST) and processes them.
 * - Route Registration:
 *   It defines specific paths (endpoints) for interactions, such as "/api/data".
 * - Middleware Setup:
 *   Includes helpers to log request and response details and handle errors.
 * - Environment-Specific Configuration:
 *   In development, it sets up Vite for rapid testing and hot-reloading.
 *   In production, it serves static files (e.g., frontend assets).
 * - Server Initialization:
 *   Creates an HTTP server that listens on port 5000 to serve both API requests and frontend content.
 * - Logging:
 *   Logs essential details like the time, request method, path, status code, and duration for monitoring and debugging.
 * - Error Handling:
 *   Catches errors and returns meaningful responses to users while maintaining server stability.
 */

import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic } from "./vite";
import { createServer } from "http";

function log(message: string) {
  // This function prints messages with the current time, so we know when something happens.
  const formattedTime = new Date().toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  });

  console.log(`${formattedTime} [express] ${message}`);
}

const app = express();

// This tells our app to understand big chunks of data sent by people, like really big messages.
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

// Example of authentication middleware
app.use((req: Request, res: Response, next: NextFunction) => {
  // Get the token from the headers
  const token = req.headers['authorization'];

  // Check if the token exists and is valid (for simplicity, we just check if it matches "Bearer mysecrettoken")
  if (token === "Bearer mysecrettoken") {
    next(); // If valid, move to the next middleware or route handler
  } else {
    res.status(401).json({ message: "Unauthorized" }); // If invalid, send an error response
  }
});

// This is like a helper that watches what people are asking for (requests) and what we send back (responses).
app.use((req, res, next) => {
  const start = Date.now(); // Remember the time when we start.
  const path = req.path; // Save the path of what people are asking for.
  let capturedJsonResponse = undefined; // This will keep what we send back if it’s in JSON.

  // We are changing how we send JSON so we can remember what we sent.
  const originalResJson = res.json;
  res.json = function (bodyJson, ...args) {
    capturedJsonResponse = bodyJson; // Save what we’re about to send back.
    return originalResJson.apply(res, [bodyJson, ...args]);
  };

  // When we finish sending the response, we check how long it took and write it down.
  res.on("finish", () => {
    const duration = Date.now() - start; // Calculate how many milliseconds it took.
    if (path.startsWith("/api")) { // Only watch requests that start with "/api".
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`; // Add the response we sent.
      }

      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "…"; // If it’s too long, shorten it.
      }

      log(logLine); // Print the log.
    }
  });

  next(); // Keep going to the next part of the app.
});

(async () => {
  // This sets up all the special paths people can use to talk to our app.
  registerRoutes(app);

  // This makes a server that uses our app to handle things.
  const server = createServer(app);

  // This catches mistakes and tells people what went wrong.
  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500; // If we don’t know the error, we say it’s a big problem (500).
    const message = err.message || "Internal Server Error"; // If there’s no message, use a default one.

    res.status(status).json({ message }); // Tell the person what happened in a simple way.
    throw err; // Keep the error so we can fix it later.
  });

  // If we’re testing and building the app, we set up Vite.
  if (app.get("env") === "development") {
    await setupVite(app, server); // This helps us test our app and make changes quickly.
  } else {
    serveStatic(app); // If it’s ready for people to use, we serve the final files.
  }

  // Always listen for people on port 5000, like a phone number for the app.
  const PORT = 5000;
  server.listen(PORT, "0.0.0.0", () => {
    log(`serving on port ${PORT}`); // Tell us that the app is ready and where to find it.
  });
})();
