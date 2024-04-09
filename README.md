![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
[![Machine Learning Client CI](https://github.com/software-students-spring2024/4-containerized-app-exercise-team-proj4/actions/workflows/machine_learning_client.yml/badge.svg)](https://github.com/software-students-spring2024/4-containerized-app-exercise-team-proj4/actions/workflows/machine_learning_client.yml)
[![Web App CI/CD](https://github.com/software-students-spring2024/4-containerized-app-exercise-team-proj4/actions/workflows/web_app.yml/badge.svg)](https://github.com/software-students-spring2024/4-containerized-app-exercise-team-proj4/actions/workflows/web_app.yml)


# Containerized App Exercise

Build a containerized app that uses machine learning. See [instructions](./instructions.md) for details.

## Project Description

This project is a containerized voice-to-text conversion application comprising three main components: a MongoDB database, a machine learning client, and a web application. The system is designed to automatically transcribe audio files uploaded by users into text using machine learning technology, with the results stored in the database for viewing and management through the web application interface.

**MongoDB Database**: Serves as the storage and management hub for the transcribed text data. It is the project's data backbone, allowing for efficient querying and updating of transcription texts.

**Machine Learning Client**: The heart of the system, responsible for processing audio files and converting them into text. It utilizes advanced speech recognition technologies to achieve the transcription from audio to text.

**Web Application**: Provides a user-friendly interface for users to upload audio files for transcription, view historical transcription records, and manage the transcribed texts stored in the database.

Overall, the project aims to provide a simple, efficient, and easily deployable and scalable voice-to-text conversion service, suitable for individuals needing quick access to written versions of audio content.

## Configuration/Run Instructions

To run the project, you should do as following:

* Clone the repository, and make sure Docker is installed and running on your local machine

* Run ```docker-compose up --build -d``` in the main directory of this project

* Access the web-app from ```http://localhost:3000```

* Click on the **record** button and allow the access to your microphone to record your voice!

If you want to pull from Docker Hub: ```docker pull zijiezhao/project4-web-app```
