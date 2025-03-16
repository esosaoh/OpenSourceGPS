<div align="center">
 

<h3 align="center">GitMentor</h3>

  <p align="center">
    Effortlessly contribute to GitHub repositories with AI-powered guidance.
    <br />
     <a href="https://github.com/esosaoh/gitmentor">github.com/esosaoh/gitmentor</a>
  </p>
</div>

## Table of Contents

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#key-features">Key Features</a></li>
      </ul>
    </li>
    <li><a href="#architecture">Architecture</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project

GitMentor is a tool designed to help developers easily contribute to GitHub repositories. It provides AI-powered analysis of repositories and generates implementation plans for specific features, making it easier to understand the codebase and contribute effectively. The project consists of a frontend built with Next.js and a backend built with FastAPI, communicating through REST APIs.

### Key Features

- **Repository Analysis:** Analyzes GitHub repositories to understand their structure and functionality.
- **Feature Implementation Plans:** Generates step-by-step implementation plans for specific features, including setup instructions, implementation steps, and potential challenges.
- **Relevant File Identification:** Identifies the most relevant files for implementing a feature, along with their importance and reason for relevance.
- **Interactive UI:** Provides a user-friendly interface for submitting repository URLs and feature descriptions, and for viewing the generated implementation plans.
- **Health Check Endpoint:** Provides a health check endpoint to monitor the status of the application and its dependencies.

## Architecture

![Architecture Diagram](https://github.com/user-attachments/assets/75adc7aa-7719-4c4f-a9bb-3ba847e12e9f)

The project follows a microservices architecture with a clear separation between the frontend and backend.

- **Frontend:**
    - Built with Next.js, a React framework for building web applications.
    - Uses Framer Motion for animations and React Markdown for rendering markdown content.
    - Interacts with the backend API to fetch repository analysis and implementation plans.
- **Backend:**
    - Built with FastAPI, a modern, high-performance web framework for building APIs with Python.
    - Uses `gitingest` to fetch repository content.
    - Uses Google Gemini AI to analyze the repository and generate implementation plans.
    - Uses Redis for caching.
- **CI/CD:**
    - Uses GitHub Actions for continuous integration and continuous deployment.
    - Lints the backend code with flake8.
- **Infrastructure:**
    - Uses Docker and Docker Compose for containerization and orchestration.
    - Deploys Redis as a separate container.

## Getting Started

To get started with GitMentor, follow these steps:

### Prerequisites

- Docker:
  ```sh
  # Installation instructions for Docker can be found at https://docs.docker.com/get-docker/
  ```
- Node.js (version 18 or higher):
  ```sh
  # Installation instructions for Node.js can be found at https://nodejs.org/
  ```
- Python (version 3.11 or higher):
  ```sh
  # Installation instructions for Python can be found at https://www.python.org/
  ```

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/esosaoh/gitmentor.git
   cd gitmentor
   ```

2. Set up environment variables:
   - Create a `.env` file in the `backend/app/core/` directory and add the following variables:
     ```
     GITHUB_TOKEN=<your_github_token> # Optional, but recommended for higher API rate limits
     GEMINI_API_KEY=<your_gemini_api_key>
     REDIS_HOST=redis
     REDIS_PORT=6379
     REDIS_PASSWORD=
     ```
   - Obtain a Gemini API key from Google AI Studio.
   - Obtain a GitHub token if you plan to analyze many repositories.

3. Build and run the application using Docker Compose:
   ```sh
   docker-compose up --build
   ```

4. Access the frontend at `http://localhost:3000`.

