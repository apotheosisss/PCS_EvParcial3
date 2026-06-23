# Evidencias Git (feature/c)

Generar al cerrar la entrega:
```bash
git log --oneline --graph --all --decorate > repo/git_log.txt
git branch -a > repo/branches.txt
```
Adjuntar capturas de Pull Requests e Issues en `repo/`.

## Flujo
`feature/c → develop → main`. Nunca `feature/c → main` directo.

## Commits de feature/c (convención del Notion)
- feat(modeling): train diabetes baseline classifiers
- feat(evaluation): generate metrics and model comparison report
- feat(dashboard): add Streamlit diabetes analytics dashboard
- feat(api): expose diabetes model prediction endpoint
- chore(docker): add Docker and compose services
- docs: complete final README and project documentation
