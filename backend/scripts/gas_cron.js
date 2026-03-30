/**
 * Google Apps Script cron jobs for Burnout Beacon.
 *
 * Setup:
 * 1. Go to https://script.google.com and create a new project
 * 2. Paste this code
 * 3. Set Script Properties:
 *    - API_BASE_URL: your backend URL (e.g. https://burnout-beacon-api.onrender.com)
 * 4. Run installTriggers() once to set up automated schedules
 */

function getConfig() {
  const props = PropertiesService.getScriptProperties();
  return {
    baseUrl: props.getProperty('API_BASE_URL') || 'http://localhost:8002',
  };
}

function callEndpoint(path, method) {
  const config = getConfig();
  const url = config.baseUrl + path;
  const options = {
    method: method || 'post',
    headers: { 'Content-Type': 'application/json' },
    muteHttpExceptions: true,
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    Logger.log(path + ' -> ' + response.getResponseCode() + ': ' + response.getContentText());
    return JSON.parse(response.getContentText());
  } catch (e) {
    Logger.log('Error calling ' + path + ': ' + e.message);
    return null;
  }
}

/** Run every morning at 6 AM — aggregates yesterday's metrics */
function dailyMetrics() {
  callEndpoint('/api/cron/daily-metrics', 'post');
}

/** Run every 6 hours — check burnout risk for all users */
function burnoutCheck() {
  callEndpoint('/api/cron/burnout-check', 'post');
}

/** Run every 4 hours — check deadlines, inactivity, overwork */
function alertSweep() {
  callEndpoint('/api/cron/alert-sweep', 'post');
}

/** Run every morning at 7 AM — reschedule any missed sessions */
function rescheduleMissed() {
  callEndpoint('/api/cron/reschedule-missed', 'post');
}

/** Run weekly on Monday — generate fresh recommendations */
function generateRecommendations() {
  callEndpoint('/api/cron/generate-recommendations', 'post');
}

/** Install all time-based triggers. Run this once manually. */
function installTriggers() {
  // Clear existing triggers
  ScriptApp.getProjectTriggers().forEach(function(trigger) {
    ScriptApp.deleteTrigger(trigger);
  });

  // Daily metrics — 6 AM every day
  ScriptApp.newTrigger('dailyMetrics')
    .timeBased()
    .everyDays(1)
    .atHour(6)
    .create();

  // Burnout check — every 6 hours
  ScriptApp.newTrigger('burnoutCheck')
    .timeBased()
    .everyHours(6)
    .create();

  // Alert sweep — every 4 hours
  ScriptApp.newTrigger('alertSweep')
    .timeBased()
    .everyHours(4)
    .create();

  // Reschedule missed — 7 AM every day
  ScriptApp.newTrigger('rescheduleMissed')
    .timeBased()
    .everyDays(1)
    .atHour(7)
    .create();

  // Generate recommendations — Monday 8 AM
  ScriptApp.newTrigger('generateRecommendations')
    .timeBased()
    .onWeekDay(ScriptApp.WeekDay.MONDAY)
    .atHour(8)
    .create();

  Logger.log('All triggers installed successfully.');
}
