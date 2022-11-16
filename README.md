# WIP iracing-exporter

A Prometheus exporter for Iracing metrics.

Plan:
* Run this program on the same machine where Iracing is running.
* Scrape the metrics by using grafana agent for example and push to a prometheus instance.
* Create a Grafana dashboard for live telemetry.


## Installation

* install grafana-agent for windows
* apply the grafana-agent config
* start agent

* clone this directory
* run python exporter.py

The Grafana agent will start scraping the exporter and will send it to a prometheus instance which is configured in the agent config.
For example to grafana.net

