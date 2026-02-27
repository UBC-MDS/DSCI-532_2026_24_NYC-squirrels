# DSCI-532_2026_24_NYC-squirrels

## Project Summary
This project introduces an interactive data visualization dashboard designed to explore behavioral patterns and spatial distributions of squirrels within New York City’s Central Park. Leveraging data from the 2018 Central Park Squirrel Census, the application allows squirrel researchers and park visitors to filter sightings by specific activities, vocalizations, and physical traits. By providing a spatial overview of behavioral "hotspots" — such as areas where squirrels are most likely to approach humans or engage in rare vocalizations — the dashboard facilitates targeted wildlife observation and enhances the experience for tourists seeking unique squirrel encounters.

## Setup & Run

```bash
conda env create -f environment.yml
conda activate squirrels
shiny run src/app.py
```

## Deployed App

The app is deployed on Posit Connect Cloud at the links below.

- Stable build (main): <https://elsereneee-nycsquirrelmap.share.connect.posit.cloud>
- Preview build (dev): <https://elsereneee-nycsquirrels-preview.share.connect.posit.cloud>