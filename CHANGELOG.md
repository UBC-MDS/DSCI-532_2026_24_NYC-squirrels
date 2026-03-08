# CHANGELOG

All notable changes to this project are documented in this file.

## [0.3.0] - 2026-03-08

### Added
- Added a new AI Analysis tab powered by QueryChat.
- Added chat interface for natural-language filtering.
- Added chat-filtered data table.
- Added charts based on chat-filtered dataframe.
- Added CSV download for chat-filtered data.

![Chat feature](img/chat_feature.png)

### Changed
- Updated app to support both regular filtering and AI-driven filtering.
- Configured AI client to use GitHub Models via environment variables.

### Fixed
- Improved empty-state handling for AI outputs.

[![Prompt](img/sample_prompt.png)]
[![Output Data](img/prompt_output.png)]

### Known Issues
- AI filters may occasionally be inconsistent.
- API rate limits can slow responses.

### Reflection
- AI tab improves usability and exploration workflow.
