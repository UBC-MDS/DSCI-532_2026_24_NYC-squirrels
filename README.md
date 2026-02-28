# DSCI-532_2026_24_NYC-squirrels

## Project Summary
This project introduces an interactive data visualization dashboard 
designed to explore behavioral patterns and spatial distributions of 
squirrels within New York City’s Central Park. Leveraging data from the 
2018 Central Park Squirrel Census, the application allows squirrel 
researchers and park visitors to filter sightings by specific 
activities, vocalizations, and physical traits. By providing a spatial 
overview of behavioral "hotspots" — such as areas where squirrels are 
most likely to approach humans or engage in rare vocalizations — the 
dashboard facilitates targeted wildlife observation and enhances the 
experience for tourists seeking unique squirrel encounters.
## For Users

### Motivation
Central Park has thousands of squirrel sightings across space, time, and traits. This dashboard helps users quickly explore where squirrels are seen and how patterns differ by fur color, age, and shift.

### What the dashboard solves
- Makes squirrel sightings easy to explore on an interactive map.
- Supports filtering to focus on specific squirrel groups.
- Summarizes key patterns with fur color and shift count charts.
- Provides a table view for exact records.

### Deployed app
- Stable build: <https://elsereneee-nycsquirrelmap.share.connect.posit.cloud>
- Preview build: <https://elsereneee-nycsquirrels-preview.share.connect.posit.cloud>

### Demo
![Project Demo](img/demo.mp4)

## For Contributors

### Install dependencies and run locally

```bash
conda env create -f environment.yml
conda activate squirrels
shiny run src/app.py
```

### Contribution guide
See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow, branch strategy, pull requests, and contribution expectations.
