# ML Model training script
import pickle
from sklearn.tree import DecisionTreeClassifier
import numpy as np

# Example dataset (amount, location_flag)
X = np.array([[1000, 0], [15000, 1], [200, 0], [50000, 1]])
y = np.array([0, 1, 0, 1])  # 0 = Safe, 1 = Fraudulent

model = DecisionTreeClassifier()
model.fit(X, y)

# Save model
with open("ml/model.pkl", "wb") as f:
    pickle.dump(model, f)
