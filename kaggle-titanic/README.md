# Titanic: Machine Learning from Disaster

This project aims to predict the survival of passengers aboard the Titanic using machine learning algorithms. The dataset includes information about passengers such as their class, age, sex, and the fare they paid, and the goal is to predict whether a passenger survived or not.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Data](#data)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Model](#model)
6. [Results](#results)
7. [Contributing](#contributing)
8. [License](#license)

## Project Overview

The Titanic dataset is a classic problem for binary classification. We will use the dataset to train a machine learning model that predicts survival based on a set of passenger features. The project involves:

- Data Preprocessing
- Feature Engineering
- Model Training
- Evaluation
- Prediction

## Data

The project uses the Titanic dataset from the Kaggle competition [Titanic: Machine Learning from Disaster](https://www.kaggle.com/c/titanic). The dataset is split into training and testing datasets.

### Files:

- `train.csv`: Contains training data with passenger information and survival status.
- `test.csv`: Contains test data with passenger information for prediction.
- `gender_submission.csv`: A submission file format example.

## Installation

To set up the project, you will need to install the required dependencies. You can do this using `pip` or `conda`.

### Using `pip`:
1. Create a virtual environment:
    ```
    python -m venv venv
    ```
2. Activate the virtual environment:
    - On Windows:
        ```
        .\venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```
        source venv/bin/activate
        ```
3. Install the required packages:
    ```
    pip install -r requirements.txt
    ```

### Dependencies:
- `pandas`
- `numpy`
- `scikit-learn`
- `matplotlib`

## Usage

To run the code, follow these steps:

1. Clone the repository:
    ```
    git clone https://github.com/ShtankoAlexandr/AI-Lab/tree/main/kaggle-titanic
    ```
2. Navigate to the project directory:
    ```
    cd titanic-machine-learning
    ```
3. Train the model and make predictions:
    - Execute the main script:
        ```
        python titanic_model.py
        ```

This will train the model, print the validation accuracy, and generate predictions for the test dataset.

## Model

In this project, we used the following machine learning pipeline:

1. **Preprocessing**:
   - Imputation for missing values (using the mean for numerical features and most frequent for categorical features).
   - Standard scaling for numerical features.
   - One-hot encoding for categorical features.
2. **Model**:
   - Logistic Regression with a maximum of 500 iterations.

## Results

After training the model, the accuracy on the validation set is displayed. The goal is to achieve a high accuracy score on the validation set to ensure good generalization to unseen data.



## Contributing

If you would like to contribute to this project, feel free to fork the repository, make your changes, and submit a pull request.

