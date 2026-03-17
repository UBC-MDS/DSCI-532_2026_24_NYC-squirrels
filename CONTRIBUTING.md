# Contributing

Contributions of all kinds are welcome here, and they are greatly appreciated! Every little bit helps, and credit will always be given.

## Contributions

You can contribute in many ways:

### Report Bugs

Report bugs by [filing an issue](https://github.com/UBC-MDS/DSCI-532_2026_24_NYC-squirrels/issues).

**If you are reporting a bug, please follow the template guidelines. The more detailed your report, the easier and thus faster we can help you.**

### Fix Bugs

Look through the GitHub issues for bugs. Anything labelled with `bug` and `help wanted` is open to whoever wants to implement it. Please assign yourself to the issue and add a comment stating you are working on it.

### Implement Features

Look through the GitHub issues for features. Anything labelled with `enhancement` and `help wanted` is open to whoever wants to implement it. Please assign yourself to the issue and add a comment stating you are working on it.

### Write Documentation

`NYC-squirrels` could always use more documentation, whether as part of the official documentation, in docstrings, or even on the web in blog posts. Just [open an issue](https://github.com/UBC-MDS/DSCI-532_2026_24_NYC-squirrels/issues) to let us know what you will be working on so that we can provide guidance.

### Submit Feedback

The best way to send feedback is to [file an issue](https://github.com/UBC-MDS/DSCI-532_2026_24_NYC-squirrels/issues).

## Get Started!

Ready to contribute? Here's how to set up ridge_remake for
local development.

1. Fork the https://github.com/UBC-MDS/DSCI-532_2026_24_NYC-squirrels repository on GitHub.
2. Clone your fork locally (_if you want to work locally_)

   ```shell
   git clone git@github.com:UBC-MDS/DSCI-532_2026_24_NYC-squirrels.git
   ```

3. Create a Branch Create a branch for local development using main as a starting point.

   ```shell
   git checkout main
   git checkout -b fix-name-of-your-bugfix
   ```

   Now you can make your changes locally.

4. Commit your changes and push your branch to GitHub. Please use [semantic commit messages](https://www.conventionalcommits.org/).

   ```shell
   git add .
   git commit -m "fix: summarize your changes"
   git push -u origin fix-name-of-your-bugfix
   ```

7. Open the link displayed in the message when pushing your new branch in order to submit a pull request.

### Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your
   new functionality into a function with a docstring.
3. Your pull request will automatically be checked by the full test suite.
   It needs to pass all of them before it can be considered for merging.

## Development tools and project practices

This project applies several development tools, GitHub infrastructures, and organizational practices introduced in the DSCI 532 course.

We use GitHub Issues to track bugs, feature requests, and documentation tasks, which helps organize development work and prioritize contributions. All code changes are submitted through pull requests and reviewed before being merged, following a collaborative development workflow.

Automated testing is performed using `pytest`, and continuous integration is implemented through GitHub Actions to ensure that all tests pass on every pull request and push to the main branch. This helps maintain code quality and prevents regressions.

The package documentation is built using Quarto and quartodoc, and is automatically deployed to GitHub Pages via GitHub Actions. This enables reproducible and up-to-date documentation to be published directly from the repository.

Environment management is handled using a reproducible environment specification file, allowing contributors to easily recreate the development environment.

These tools and practices reflect the software engineering and reproducibility principles emphasized in the course, including automation, testing, documentation, and transparent collaboration.

### Scaling considerations

If this project were to scale to a larger team or a production-level package, we would further adopt additional tools and practices such as code coverage reporting, automated linting and formatting (e.g., ruff or black), dependency update automation (e.g., Dependabot), and release automation with versioned package publishing.

For larger datasets or more computationally intensive workflows, we would also consider using containerization (e.g., Docker) and more advanced CI workflows to ensure consistent execution environments across different platforms.

These tools and practices would improve maintainability, reliability, and collaboration as the project grows.

## Milestone Retrospectives and Norms

### Milestone 3 Retrospective
* **What worked:** Our team successfully transitioned from a static dashboard to a complex, AI-integrated product by utilizing parallel development tracks for the Map UI and the AI Analysis tab.
* **What didn't work(Environment):** We initially relied on a `environment.yml` file, but realized that Conda environments were inconsistent across different operating systems, this might lead to errors during local testing and deployment.
* **What didn't work (Deployment):** We faced multiple failures when republishing to Posit Connect Cloud because of the Token and permission restrictions for the GitHub Models.
* **Improvement:** We have pivoted to a `requirements.txt` workflow and updated the permission for models to ensure all environment variables are set before pushing to production.

### Milestone 4 Collaboration Norms
To ensure a high-quality production release, our team is committing to the following norms for M4:
1. **Environment Standardization:** To ensure the project is "runnable with a single command," we have moved to a unified dependency management system that guarantees parity between local development and cloud production.

2. **Quality Assurance (QA):** We are now enforcing a strict testing-first policy where Playwright and Pytest suites must pass before any feature is merged into the main branch.

3. **Design-Before-Code:** We have committed to a "Documentation First" workflow, ensuring that specification documents and PR descriptions explain intent and design logic before any implementation begins.

4. **Distributed Ownership:** To prevent single-contributor bottlenecks, we have distributed feedback resolution and code reviews equally across the team, ensuring everyone touches both the source code and the documentation.

## Code of conduct

By contributing to this project, you are agreeing to abide by our Code of Conduct, which can be found here [Code of Conduct](https://github.com/UBC-MDS/DSCI-532_2026_24_NYC-squirrels/blob/main/CODE_OF_CONDUCT.md).