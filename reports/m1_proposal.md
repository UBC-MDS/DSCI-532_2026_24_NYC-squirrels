# Proposal: Central Park Squirrel Behavior Dashboard

### Section 1: Motivation and Purpose

**Our role:** Data visualization consultants

**Target audience:** Squirrel researchers and Central Park visitors (tourists)

Central Park is home to a diverse population of eastern gray squirrels, yet understanding their complex behavioral patterns and spatial distribution remains a challenge for both scientific study and public engagement. For researchers, identifying specific hotspots for rare behaviors or vocalizations is time-consuming without a centralized visual tool. Similarly, tourists interested in seeing unique squirrels with rare colorations or squirrels that are comfortable with human interaction often lack guidance on where to look. To address these challenges, we propose building an interactive data visualization dashboard. This tool will allow researchers to pinpoint ideal observation locations based on behavioral filters and enable tourists to discover areas of the park that match their interests, such as high-density zones for rare squirrel color combinations or specific interaction types.

### Section 2: Description of the Data

We will be visualizing the 2018 Central Park Squirrel Census dataset, which contains 3,023 squirrel sightings. Each observation is described by 31 variables that capture physical characteristics, location, and behavior. These variables include:

* **Spatial and Temporal Data:** Geographic coordinates (`X`, `Y`, `Lat/Long`), `Hectare` identifiers, and the `Date` and `Shift` (AM/PM) all have 3,023 non-null entries (100% complete). These are essential for mapping squirrel hotspots.

* **Physical Characteristics:** `Primary Fur Color` (2,968 non-null) and `Age` (2,902 non-null) are largely complete, while `Highlight Fur Color` (1,937 non-null) provides additional detail for specific identifying markers.

* **Behavioral Indicators:** Core behaviors such as `Running`, `Chasing`, `Climbing`, `Eating`, and `Foraging` are captured for all 3,023 sightings as boolean flags.

* **Communication and Human Interaction:** Vocalizations (`Kuks`, `Quaas`, `Moans`) and interaction indicators (`Approaches`, `Indifferent`, `Runs from`) also have 3,023 non-null entries.

* **Sparse/Qualitative Data:** Some fields like `Specific Location` (476 non-null) and `Other Activities` (437 non-null) have fewer entries but offer valuable qualitative descriptions for deeper exploration.

Using this data, we will derive new insights, such as behavioral density maps and interaction profiles, to help users understand how squirrel activity varies across different regions of Central Park. 

### Section 3: Research Questions & Usage Scenarios

**Persona:** Maria is a wildlife ecology graduate student at Columbia University who is studying urban animal behavior. She is preparing fieldwork in Central Park and needs to identify optimal observation locations for studying specific squirrel behaviors and interaction patterns. She has limited time for field visits and wants to maximize data collection efficiency by targeting areas with the highest concentration of behaviors relevant to her research.

**Usage Scenario:** Maria is planning a week of field observations focused on squirrel–human interaction dynamics. She wants to understand where in the park squirrels are most likely to approach humans versus flee, and whether fur colour correlates with these behaviors. Using the dashboard, she filters by interaction type (e.g., "Approaches" vs. "Runs from") and overlays the results on the park map. She notices that the southern hectares have a higher density of squirrels that approach humans, likely due to heavier foot traffic and tourist feeding. She also discovers that black-furred squirrels are proportionally more likely to flee. With this insight, she schedules her morning observations in the south end for approach behavior and targets the northern wooded areas for studying avoidance behavior, saving days of unguided surveying.

**User Stories:**

1. *As a* wildlife ecology researcher, *I want to* filter squirrel sightings on a map by specific behaviors (running, eating, foraging, climbing) *so that I can* identify behavioral hotspots and plan targeted field observations in those areas.

2. *As a* Central Park tourist, *I want to* see which areas of the park have the highest density of squirrels that are comfortable around humans (indifferent or approaching) *so that I can* visit those spots for a more interactive wildlife experience.

3. *As a* squirrel census volunteer, *I want to* compare the distribution of fur colours and vocalization patterns across different park regions and times of day (AM/PM shift) *so that I can* understand whether certain squirrel populations dominate specific habitats or are more active at particular times.

### Section 4: Exploratory Data Analysis

We focus on **User Story 1** — a researcher identifying behavioral hotspots — and show that the data supports this task with two visualizations from our EDA notebook ([`notebooks/eda.ipynb`](../notebooks/eda.ipynb)).

**Visualization 1 — Sightings Map by Location and Fur Colour:**
A scatter plot of all sightings by geographic coordinates, coloured by fur colour. The map shows that sightings cluster in specific areas of the park rather than being spread evenly, helping a researcher quickly identify high-density zones to prioritize for field visits.

**Visualization 2 — Proportion of Squirrels That Run From Humans by Fur Colour:**
A bar chart comparing flee rates across fur colour groups. Black squirrels flee at ~31%, compared to ~22% for gray and cinnamon squirrels. This tells the researcher that fur colour is linked to human-avoidance behavior, which can guide where and how to set up observations.

These visualizations confirm that the dataset contains meaningful spatial and behavioral patterns that an interactive dashboard can help users explore and act on.

### Section 5: App Sketch & Description

![Sketch](../img/sketch.png)

The dashboard combines spatial mapping and behavioural summaries to help users explore squirrel sightings in Central Park. The interface includes a global filter bar, a full-park map, a zoomed zone view, a count display, and three behaviour-focused bar charts.

**Global Filters (Top Control Panel)**
* includes three filters: Location (single select), Age (multi-select), and Time of Day (AM/PM) (multi-select)
* visual components update dynamically to reflect selected criteria

**Main Map Panel (Full Park View)**
* map of Central Park displaying all filtered squirrel sightings as points
* points coloured by primary fur colour
* enables users to identify density patterns around the park

**Zoomed Zone View**
* secondary map displaying a zoomed-in view of different park zones
* provides better resolution for more local density patterns
* updates dynamically with the location filter

**Sighting Count Display**
* summary box displaying the number of squirrel sightings currently selected
* provides immediate quantitative context
* updates dynamically based on selected filters

**Movement Chart**
* bar chart that summarises movement-related behaviors, including running, chasing, climbing, eating, and foraging
* bars represent the frequency of each behaviour within the selected subset

**Vocalisation Chart**
* bar chart summarising squirrel vocalisations (kuks, quaas, and moans)
* displays the frequency of each vocalisation within the selected subset

**Human Interaction Chart**
* bar chart displaying the frequency of human interaction behaviours (approaches, indifferent, and runs from)
* displays the frequency of each human interaction behaviour within the selected subset