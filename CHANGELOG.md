# CHANGELOG

All notable changes to this project are documented in this file.

## [0.5.0] - 2026-03-17

### Added

- Project description with styled background in sidebar for improved user onboarding
- Total squirrel count display below fur color legend on map
- Updated README with clear setup and usage instructions including OpenAI API configuration
- Clickable map legend that allows for fur colour selection and updates outputs (as well as checkboxes) [PR #...]

-   <!-- New features, components, tests - one line each. Reference PRs where relevant (e.g. #12). -->

### Changed

- Enhanced sidebar user information box with gradient background and visual styling

-   Data cleaning moved from `eda.ipynb` and `app.py` to new `data_processing.py` script to improve read

-   DuckDB and Parquet implemented into `app.py`

-   Use checkboxed rather than selectize for filters (#120)

-   Convert the behaviour filter to multi-select pill like the other filters (#120)

-   Make the basemap selector more intuitive (#120)

-   Adjust chart width to remove whitespace (#120)

-   AI tab UI redesigned with chat feature as a fixed-height scrollable left sidebar (#96)

### Fixed

-   <!-- Bugs resolved since M3. -->
- Fixed infinite loop on behavior filter by wrapping input read in `reactive.isolate()` context manager

-   **Feedback prioritization issue link:** #88

### Known Issues

-   <!-- Anything incomplete or broken TAs should be aware of (so it isn't mistaken for unfinished work). -->

### Release Highlight: [Component Click Event Interaction]

<!-- One short paragraph describing what you built and what it does for the user. -->

-   **Option chosen:** D
-   **PR:** #...
-   **Why this option over the others:** As our Querychat has performed well thus far, we opted to add a component click event interaction to make our map feel more interactive. We chose this path over LLM logging as we feel the map is the cornerstone of our dashboard, and improving it provides more value to its users.
-   **Feature prioritization issue link:** #113

### Collaboration

<!-- Summary of workflow or collaboration improvements made since M3. -->

-   **CONTRIBUTING.md:** <!-- Link to the PR that updated it with your M3 retrospective and M4 norms. -->
-   **M3 retrospective:** <!-- What changed in your workflow after M3 collaboration feedback. -->
-   **M4:** <!-- What you tried or improved this milestone. -->

### Reflection

```{=html}
<!-- Standard (see General Guidelines): what the dashboard does well, current limitations,
     any intentional deviations from DSCI 531 visualization best practices. -->
```

<!-- Trade-offs: one sentence on feedback prioritization - full rationale is in #<issue> and ### Changed above. -->

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
