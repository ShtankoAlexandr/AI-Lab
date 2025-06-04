# 📰 NLP News Scraper & Analyzer

This project provides a full pipeline for scraping financial and environmental news, classifying topics, enriching articles with NLP insights (sentiment, keywords, named entities), and detecting potential environmental scandals.

## ⚙️ Requirements

Set up a virtual environment and install dependencies:

```bash
pip install -r requirements.txt

Вот README.md для твоего проекта, оформленный в удобном формате:
# 📰 NLP News Scraper & Analyzer

This project provides a full pipeline for scraping financial and environmental news, classifying topics, enriching articles with NLP insights (sentiment, keywords, named entities), and detecting potential environmental scandals.

## ⚙️ Requirements

Set up a virtual environment and install dependencies:

```bash
pip install -r requirements.txt


🗄️ Database Configuration
The project uses a local MySQL database to store news data.
Install MySQL Server
Download and install MySQL:
🔗 MySQL Official Site
Create Database and User
Run these commands in MySQL shell or a client:
CREATE DATABASE newsdb;

CREATE USER 'myuser'@'localhost' IDENTIFIED BY 'mypassword';

GRANT ALL PRIVILEGES ON newsdb.* TO 'myuser'@'localhost';

FLUSH PRIVILEGES;

Configure .env File
Create .env in the root folder:
DB_HOST=localhost
DB_PORT=3306
DB_USER=myuser
DB_PASSWORD=mypassword
DB_NAME=newsdb

Usage
Run the scraper to fetch articles
python scraper_news.py

Stop manually if needed after enough data is collected.
Train and save the topic classifier mode
python topic_classifier.py

The trained model is saved as models/topic_classifier.pkl.
Perform NLP enrichment on scraped news
python nlp_enriched_news.py

his generates a dataset data/enriched_news.csv with enriched articles.
✅ Validation & Checks
- Scraper runs without errors and stores articles correctly.
- Topic classifier achieves accuracy >95% with no overfitting.
- NLP enrichment script produces a dataset with expected columns and processed data.
- The output includes topics, sentiment, scandal detection, and organization mentions.
- Top 10 flagged environmental scandals are detected based on similarity scores.
🔄 Running on Another Machine
To run the project on a different system:
- Install MySQL and set up the same database/user credentials.
- Copy or create the .env file with correct DB access.
- Install dependencies from requirements.txt.
- Copy the project files, including models/ if avoiding retraining.
- Run the scripts in order: scraper → topic classifier → NLP enrichment.

📩 Need help? Feel free to reach out!

👤 Author
Oleksandr (Alex) Shtanko
📍 Denham, Uxbridge, London
📧 al222ex@gmail.com
🔗 www.linkedin.com/in/oleksandr-shtanko

