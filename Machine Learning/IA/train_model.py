import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Carregar dados
data = pd.read_csv('letters_data.csv', header=None)

# Separar features e labels
X = data.iloc[:, 1:]
y = data.iloc[:, 0]

# Dividir em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Criar e treinar modelo
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Avaliar
accuracy = model.score(X_test, y_test)
print(f"Acurácia no teste: {accuracy * 100:.2f}%")

# Salvar modelo
joblib.dump(model, 'modelo_libras.pkl')
print("Modelo salvo como 'modelo_libras.pkl'.")