# Velib Tracker

This was a project that I worked on while completing the [Jedha Bootcamp](https://en.jedha.co) *Data Lead* course, which focuses on data engineering.

## Project Goal

The project goal was to track the number of bikes available at the Velib station closest to my apartment.

Velib offers a [public API](https://velib-metropole-opendata.smoove.pro/opendata/Velib_Metropole/station_status.json) that can be queried to retrieve the number of bikes (mechanical and electric) available at all their stations. I used this API to extract the data of interest to me and wrote a simple web application to display them.

## Project Components

The project was designed in a modular way and its components are:

1. ETL (Extract, Transform, Load) component: I wrote an *AWS Lambda* function (`aws-lambdas/etl.py`) to query the Velib API, extract the data I was interested in, and store the filtered data in a *AWS DynamoDB* table. I then used *AWS CloudWatch Events* to trigger the *Lambda* function every 10 minutes (starting on July 26th 2021).

2. Public API: I wrote a second *AWS Lambda* function (`aws-lambdas/api.py`), which was used, together with *AWS API Gateway*, to build a public REST API exposing the data stored in my *DynamoDB* table.

3. Web application: I built a simple Flask application (`viz-app`) to retrieve and display the data accumulated through time and compute some statistics.

4. CI-CD (Continuous Integration-Continuous Delivery) component: I used *Docker* to build a containerized version of the app and wrote a *GitHub* action (`.github/workflows/build-and-upload.yaml`) to automatically push the image created via the `Dockerfile` to my *Docker Hub* account.

## Project Output

The data were collected during the span of approximately one month, from August 28th to September 28th 2021. The data and a screenshot of the running web application can be found in the folder `output`.
