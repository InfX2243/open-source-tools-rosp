// Sample frontend client accessing env variables
const apiUrl = process.env.API_GATEWAY_URL || "https://api.example.com";
const debugMode = process.env.DEBUG === "true";
const telemetryKey = import.meta.env.VITE_ANALYTICS_KEY;

export function initClient() {
  console.log(`Connecting to ${apiUrl} with debug=${debugMode}`);
}
