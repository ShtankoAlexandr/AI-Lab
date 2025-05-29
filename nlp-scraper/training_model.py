import pandas as pd
import matplotlib.pyplot as plt 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import learning_curve
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np
import pickle
from sklearn.metrics import classification_report, accuracy_score

# Load train/test dataset

df_train=pd.read_csv("data/bbc_news_train.csv")
df_test=pd.read_csv("data/bbc_news_tests.csv")

X_train = df_train['Text']
y_train = df_train['Category']

X_test = df_test['Text']
y_test = df_test['Category']

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=10000)),
    ("clf", MultinomialNB())
])
print("Training topic classifier...")
pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Test accuracy: {acc:.4f}")
print(classification_report(y_test, y_pred))

# Сохраняем модель
with open("results/topic_classifier.pkl", "wb") as f:
    pickle.dump(pipeline, f)

# Рисуем learning curve
train_sizes, train_scores, val_scores = learning_curve(
    pipeline, X_train, y_train, cv=5, scoring='accuracy',
    train_sizes=np.linspace(0.1, 1.0, 10)
)

plt.figure(figsize=(8,6))
plt.plot(train_sizes, np.mean(train_scores, axis=1), label='Training accuracy')
plt.plot(train_sizes, np.mean(val_scores, axis=1), label='Validation accuracy')
plt.xlabel('Training size')
plt.ylabel('Accuracy')
plt.title('Learning Curves')
plt.legend()
plt.grid(True)
plt.savefig("results/learning_curves.png")
plt.show()