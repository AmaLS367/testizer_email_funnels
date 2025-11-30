# Testizer email funnels · Scheduling guide

This document describes how often and in what order to run the funnel script, as well as the general scheduling strategy.

## 1. Which Tasks Need to Run

Main working task:

- `app.main`

  Responsible for:

  - selecting new candidates by tests;
  - adding contacts to Brevo lists;
  - recording funnel entry in the `funnel_entries` table;
  - syncing certificate purchases with MODX tables.

Reporting task:

- `app.report_conversions`

  Used for periodic conversion reports, run manually as needed.

## 2. Main Task Execution Frequency

Recommended logic:

- Frequency: every 10-30 minutes, depending on load and requirements.
- With a small number of tests, you can start with hourly runs.

Reasons:

- tests and purchases don't happen every second;
- too frequent runs create unnecessary database load;
- too infrequent runs reduce "freshness" of funnels and emails.

## 3. Sequence of Actions Before Moving to Schedule

Before enabling automatic execution:

1. Verify that `.env` is configured.

2. Run the script several times manually with `APP_DRY_RUN=true`:

   ```powershell
   python -m app.main
   ```

3. Check logs in `logs/app.log`.

4. Change `APP_DRY_RUN` to `false` when script behavior is satisfactory.

5. Run manually again and verify that:

   * contacts actually appear in Brevo;

   * the `funnel_entries` table is populated;

   * there are no errors in logs.

Only after this should automatic scheduling be enabled.

## 4. Setting Up Schedule on Server

A production server can use its own scheduling mechanism:

* cron or similar system on hosting;
* hosting control panel with graphical task scheduler;
* separate task orchestrator if already in use.

General recommendations for any system:

* the startup command should be the Python task from the project root;
* virtual environment should be activated before startup;
* work logs should be written to a file for diagnostics.

Specific schedule implementation depends on infrastructure and can be configured by the server administrator.

## 5. Example Schedule Logic

Regardless of the system used, the logic can be:

1. Run the main funnel task every 15 minutes.

   * If the previous run is still running, don't start a new task copy.
   * It's important to avoid parallel runs that work with the same tables.

2. Once a day (e.g., at night) generate a conversion report manually and track dynamics:

   ```powershell
   python -m app.report_conversions --from-date 2024-01-01
   ```

3. Change run frequency if needed when:

   * load noticeably increases;
   * funnel logic changes;
   * closer to real-time synchronization is required.

## 6. Schedule Control and Debugging

After enabling automatic scheduling, you should:

* periodically check `logs/app.log`;
* monitor if new entries appear in `funnel_entries`;
* compare the number of new tests and the number of new funnel entries.

If something goes wrong:

* temporarily disable automatic execution;
* run the task manually and analyze logs;
* restore scheduling only after eliminating error causes.

