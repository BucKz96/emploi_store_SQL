# Contributing to Emploi Store

Merci de votre intérêt pour ce projet ! Voici comment contribuer :

## 🚀 Pour commencer

1. Fork le repository
2. Clone votre fork : `git clone https://github.com/votre-username/emploi-store.git`
3. Créez une branche : `git checkout -b feature/votre-feature`

## 📝 Guidelines

### Code

- Suivez PEP 8
- Utilisez black pour le formatage : `black emploi_store/`
- Ajoutez des type hints
- Écrivez des tests pour les nouvelles fonctionnalités

### Commits

- Utilisez des messages clairs en français ou anglais
- Format : `type(scope): description`
  - Ex: `feat(api): add pagination to offers endpoint`
  - Ex: `fix(parser): handle missing salary data`

### Tests

```bash
pytest emploi_store/tests/
pytest --cov=emploi_store
```

### Pull Requests

1. Assurez-vous que les tests passent
2. Mettez à jour le README si nécessaire
3. Décrivez clairement les changements

## 🐛 Signaler un bug

Ouvrez une issue avec :
- Description du problème
- Étapes pour reproduire
- Comportement attendu vs actuel
- Version Python et OS

## 💡 Suggestions

Les idées d'amélioration sont les bienvenues ! Ouvrez une issue pour en discuter.

## 📧 Contact

Pour toute question : [votre-email@example.com]
