# Modelo — DiabetesNHANES (feature/c)

## Objetivo
Clasificar `diabetes_target` (0/1) a partir de variables demográficas, antropométricas
y de laboratorio de NHANES. **Uso educativo, no diagnóstico clínico.**

## Modelos entrenados
- `LogisticRegression(class_weight="balanced")`
- `RandomForestClassifier(class_weight="balanced")`
- `GradientBoostingClassifier`

El mejor modelo se elige automáticamente por **ROC-AUC** sobre el test set.

## Métricas reportadas
accuracy, precision, recall, f1, roc-auc, matriz de confusión y feature importance.
Como el target puede quedar desbalanceado, se prioriza recall/F1 y curva PR, y se usa
`class_weight="balanced"`.

## Artefactos (data/)
- `06_models/model.pkl` — bundle `{model, feature_cols, feature_means, model_version}`.
- `07_model_output/predictions.csv`
- `08_reporting/metrics.json`, `model_comparison.csv`, `confusion_matrix.{csv,png}`, `feature_importance.{csv,png}`

## Reproducir
```bash
python scripts/make_sample_model_input.py   # solo si no hay dato real de feature/b
kedro run --pipeline modeling
kedro run --pipeline reporting
```
