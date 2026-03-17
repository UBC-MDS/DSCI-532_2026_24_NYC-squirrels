---
editor_options: 
  markdown: 
    wrap: 72
---

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
experience for tourists seeking unique squirrel encounters. \## For
Users

### Motivation

Central Park has thousands of squirrel sightings across space, time, and
traits. This dashboard helps users quickly explore where squirrels are
seen and how patterns differ by fur color, age, and shift.

### What the dashboard solves

-   Makes squirrel sightings easy to explore on an interactive map.
-   Supports filtering to focus on specific squirrel groups.
-   Summarizes key patterns with fur color and shift count charts.
-   Provides a table view for exact records.

### Deployed app

-   Stable build:
    <https://elsereneee-nycsquirrelmap.share.connect.posit.cloud>
-   Preview build:
    <https://elsereneee-nycsquirrels-preview.share.connect.posit.cloud>

### Demo

[![Watch dashboard
demo](img/demo.png)](https://github.com/UBC-MDS/DSCI-532_2026_24_NYC-squirrels/blob/main/img/demo.mp4)

### Using the Dashboard

1. **Use filters** (left sidebar) to select specific squirrel traits
2. **Explore the map** to see spatial distributions
3. **Review charts** (right side) for patterns in fur color, shifts, and behaviors
4. **Ask questions** in the Chat tab for AI-powered natural language queries

## For Contributors

### Install dependencies and run locally

1. **Clone and set up the environment:**

``` bash
conda env create -f environment.yml
conda activate squirrels
pip install -r requirements.txt
```

2. **(Optional) Configure AI features:**

Create a `.env` file in the project root and add your OpenAI API key:

``` bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. **Run the application:**

``` bash
python src/data_processing.py
shiny run src/app.py
```

The app will be available at `http://localhost:xxxx`

### Running Tests
This project uses pytest for unit testing logic and Playwright for verifying dashboard behaviors.

1. Install testing tools:
Ensure you have the browser engines installed after setting up your environment:

```bash
pip install pytest-playwright
playwright install
```

2. Run all tests:
You can run the entire suite with a single command from the project root:

```bash
pytest tests/
```

### Contribution guide

See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow, branch strategy,
pull requests, and contribution expectations.
