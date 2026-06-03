# AI Health Prediction System

## Overview

This project is an AI-powered Health Prediction System developed using Python, Streamlit, FastAPI, SQLite, and Machine Learning.

The application allows users to:

* Add patient records
* Validate patient information
* Store records in SQLite database
* Perform CRUD operations
* Generate disease risk predictions through API integration
* Display prediction results in the Remarks field

## Features

### Patient Management

* Create patient records
* View patient records
* Update patient email
* Delete patient records

### Validations

* Email validation
* Date of Birth validation
* Duplicate record detection

### AI/ML Prediction

* Predicts health risk based on:

  * Glucose
  * Haemoglobin
  * Cholesterol

### Technologies Used

* Python
* Streamlit
* FastAPI
* SQLite
* Pandas
* Scikit-learn
* Requests

## Installation

Install dependencies:

pip install -r requirements.txt

## Run FastAPI Server

uvicorn api:app --reload

## Run Streamlit Application

streamlit run app.py

## Project Workflow

1. User enters patient details.
2. Application validates data.
3. Data is sent to API endpoint.
4. API generates health risk prediction.
5. Prediction result is stored in Remarks.
6. Patient record is saved into SQLite database.

## Author

Nutan Agare
