# CHANGELOG

All notable changes to this project are documented in this file.

## [0.4.0] - 2026-03-17

### Added

-   Project description with styled background in sidebar for improved user onboarding

-   Total squirrel count display below fur color legend on map

-   Updated README with clear setup and usage instructions including OpenAI API configuration

-   Clickable map legend that allows for fur colour selection and updates outputs (as well as checkboxes)

-   Automated testing suite in `tests/` featuring 4 Playwright behavior tests and 1 pytest unit test.

-   Integration tests in `tests/test_app.py` to verify data synchronization between the map legend and data table footer.

-   AI Tab stability test to ensure the chat interface and navigation load correctly.

-   Unit tests in `tests/test_utils.py` for isolated verification of color-mapping functions.

### Changed

-   Enhanced sidebar user information box with gradient background and visual styling

-   Data cleaning moved from `eda.ipynb` and `app.py` to new `data_processing.py` script to improve read

-   DuckDB and Parquet implemented into `app.py`

-   Use checkboxed rather than selectize for filters (#120)

-   Convert the behaviour filter to multi-select pill like the other filters (#120)

-   Make the basemap selector more intuitive (#120)

-   Adjust chart width to remove whitespace (#120)

-   AI tab UI redesigned with chat feature as a fixed-height scrollable left sidebar (#96)

-   Moved `color_for_fur` and `color_for_shift` functions from `app.py` into a modular `src/utils.py` for testing (#127)

-   Organized the project by moving all source code (`app.py`, `utils.py`, `data_processing.py`) into a `src/` directory (#127)

-   Added tests folder with 2 tests files with conftest and utils (#127)

-   Updated test-related content in requirements.txt, readme file, and changelog accordingly (#127)

-   Fixed the src/ path issues when republishing (#129)

### Fixed

- Fixed infinite loop on behavior filter by wrapping input read in `reactive.isolate()` context manager

-   **Feedback prioritization issue link:** #88

-   **Tests:** #82

### Known Issues

- None

### Release Highlight: [Component Click Event Interaction]

We built a clickable legend for the map component of the dashboard. All outputs in the dashboard react to this component, and checkboxes are also updated to remain aligned with the legend. The component filters the squirrels by fur colour, and makes the key takeaway of the map a little more intuitive to use, and thus infer from.

-   **Option chosen:** D
-   **PR:** #125
-   **Why this option over the others:** As our Querychat has performed well thus far, we opted to add a component click event interaction to make our map feel more interactive. We chose this path over LLM logging as we feel the map is the cornerstone of our dashboard, and improving it provides more value to its users.
-   **Feature prioritization issue link:** #113

### Collaboration

-   **CONTRIBUTING.md:** Updated via PR (#131) to include our Milestone 3 retrospective and formalize our new collaboration norms for testing, documentation, and ownership.
-   **M3 retrospective:** We successfully transitioned from a static dashboard to a complex, AI-integrated product by utilizing parallel development tracks for the Map UI and the AI Analysis tab. 
-   **M4:** In Milestone 4, we pivoted toward production stability by optimizing data performance with a Parquet and DuckDB backend and resolving critical map rendering latencies. The user experience was refined through a scrollable AI sidebar, intuitive basemap selectors, and data imputation for cleaner UI filters. To secure the codebase, a testing suite was established, and the workflow matured by managing all tasks through prioritized GitHub Issues and atomic, peer-reviewed pull requests.

### Reflection

```{=html}
<!-- Standard (see General Guidelines): what the dashboard does well, current limitations,
     any intentional deviations from DSCI 531 visualization best practices. -->
```

Generally, we prioritised feedback that either critically improved the functional capabilities of our dashboard, or represented necessary visual improvements which made our app more intuitive to use. Overall, the changes made to the dashboard over the last few weeks have made it attractive, easy to use, and functional. Perhaps the biggest success of the dashboard is the interactive map which serves as the centre piece. As such, we found Lecture 3 of DSCI 532 (Geospatial Visualisation) to be extremely useful in working with GeoJSON data and creating maps with Altair.

However, the map also represents our biggest limitation. One of our intentions when beginning to plan the project was to be able to divide the map into chunks. In this way, we could help our users narrow down which areas of the park they would be most likely to find squirrels in. While this didn't come to fruition, we believe that users are still able to do so, but with slightly more effort. Another struggle that we had throughout the project was the latency of some of our outputs. For this reason, we believe it would have been very helpful to spend more time discussing strategies for mitigating laggy components in class.

```{=html}
<!-- Most useful: which lecture, material, or feedback shaped your work most this milestone,
     and anything you wish had been covered. -->
```

## [0.3.0] - 2026-03-08

### Added

-   Added a new AI Analysis tab powered by QueryChat.
-   Added chat interface for natural-language filtering.
-   Added chat-filtered data table.
-   Added charts based on chat-filtered dataframe.
-   Added CSV download for chat-filtered data.

![Chat feature](img/chat_feature.png)

### Changed

-   Updated app to support both regular filtering and AI-driven filtering.
-   Configured AI client to use GitHub Models via environment variables.

### Fixed

-   Improved empty-state handling for AI outputs.

[![Prompt](img/sample_prompt.png)] [![Output Data](img/prompt_output.png)]

### Known Issues

-   AI filters may occasionally be inconsistent.
-   API rate limits can slow responses.

### Reflection

-   AI tab improves usability and exploration workflow.
