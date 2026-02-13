# Proposal: Central Park Squirrel Behavior Dashboard

### Section 1: Motivation and Purpose

**Our role:** Data visualization consultants

**Target audience:** Squirrel researchers and Central Park visitors (tourists)

Central Park is home to a diverse population of eastern gray squirrels, yet understanding their complex behavioral patterns and spatial distribution remains a challenge for both scientific study and public engagement. For researchers, identifying specific hotspots for rare behaviors or vocalizations is time-consuming without a centralized visual tool. Similarly, tourists interested in seeing unique squirrels with rare colorations or squirrels that are comfortable with human interaction often lack guidance on where to look. To address these challenges, we propose building an interactive data visualization dashboard. This tool will allow researchers to pinpoint ideal observation locations based on behavioral filters and enable tourists to discover areas of the park that match their interests, such as high-density zones for rare squirrel color combinations or specific interaction types.

### Section 2: Description of the Data

We will be visualizing the 2018 Central Park Squirrel Census dataset, which contains 3,023 squirrel sightings. Each observation is described by 31 variables that capture physical characteristics, location, and behavior. These variables include:

* **Spatial and Temporal Data:** Geographic coordinates (`X`, `Y`, `Lat/Long`), `Hectare` identifiers, and the `Date` and `Shift` (AM/PM) all have 3,023 non-null entries (100% complete). These are essential for mapping squirrel hotspots.

* **Physical Characteristics:** `Primary Fur Color` (2,968 non-null) and `Age` (2,902 non-null) are largely complete, while `Highlight Fur Color` (1,937 non-null) provides additional detail for specific identifying markers..

* **Behavioral Indicators:** Core behaviors such as `Running`, `Chasing`, `Climbing`, `Eating`, and `Foraging` are captured for all 3,023 sightings as boolean flags.

* **Communication and Human Interaction:** Vocalizations (`Kuks`, `Quaas`, `Moans`) and interaction indicators (`Approaches`, `Indifferent`, `Runs from`) also have 3,023 non-null entries.

* **Sparse/Qualitative Data:** Some fields like `Specific Location` (476 non-null) and `Other Activities` (437 non-null) have fewer entries but offer valuable qualitative descriptions for deeper exploration.

Using this data, we will derive new insights, such as behavioral density maps and interaction profiles, to help users understand how squirrel activity varies across different regions of Central Park. 
