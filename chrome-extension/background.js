const POLL_INTERVAL_MINUTES = 0.016; // ~1 second
let lastNotified = "";

// 🔁 Set up polling alarm on install
chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create("pollPrediction", { periodInMinutes: POLL_INTERVAL_MINUTES });
  console.log("Alarm created for polling every", POLL_INTERVAL_MINUTES, "minutes");
});

// 🔄 Poll the FastAPI backend
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "pollPrediction") {
    fetch("http://localhost:8000/predict/latest")
      .then((res) => res.json())
      .then((data) => {
        console.log("Fetched prediction:", data);

        // Skip if response contains an error
        if (data.error) return;

        const current = `${data.species}-${data.confidence}`;
        if (current !== lastNotified) {
          chrome.notifications.create({
            type: "basic",
            iconUrl: `http://localhost:8000/images/${data.image_filename}`,
            title: "Bird Detected!",
            message: `Species: ${data.species}\nConfidence: ${(data.confidence * 100).toFixed(1)}%\nClick to view details.`,
            priority: 2
          });
          lastNotified = current;
        }
      })
      .catch((err) => {
        console.error("Polling error:", err);
      });
  }
});

// 🔗 Handle clicks on notifications
chrome.notifications.onClicked.addListener(() => {
  chrome.tabs.create({ url: "http://localhost:5500/dashboard.html" });
});
