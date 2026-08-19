# Rapport de Projet — CHU Platform

## Plateforme d'analyse de données conversationnelle pilotée par Intelligence Artificielle

---

## Introduction Générale

L'essor récent des grands modèles de langage (Large Language Models, LLMs) a profondément transformé le paysage de l'interaction homme-machine. Des modèles tels que GPT-4, Claude, Llama et leurs dérivés ont démontré des capacités remarquables dans des tâches allant de la génération de texte à la résolution de problèmes complexes, en passant par le raisonnement sur des données structurées. Parallèlement, l'analyse de données — discipline fondamentale dans les secteurs scientifique, commercial et industriel — demeure largement tributaire de compétences techniques spécialisées, nécessitant la maîtrise de langages de programmation (Python, R), de bibliothèques statistiques et d'outils de visualisation.

Le présent rapport détaille la conception, l'architecture et la mise en œuvre de la **CHU Platform**, une plateforme modulaire d'analyse de données conversationnelle qui fusionne ces deux tendances. En combinant un framework d'agents intelligents basé sur LangGraph, un moteur d'analyse purement computationnel (pandas, matplotlib) et une interface utilisateur réactive construite avec SvelteKit 5, cette plateforme permet à des utilisateurs non spécialistes d'interroger leurs jeux de données en langage naturel, d'obtenir des analyses statistiques rigoureuses et de visualiser les résultats sous forme de graphiques publiables.

Ce document s'articule autour de six sections principales. Après avoir posé le contexte technologique et scientifique du projet, nous exposons la problématique adressée, les objectifs poursuivis, la méthodologie adoptée pour la conception et le développement, et enfin l'organisation du présent rapport.

---

## Contexte du projet

### 2.1. L'analyse de données à l'ère de l'IA générative

L'analyse de données constitue un pilier central de la prise de décision dans les organisations contemporaines. Qu'il s'agisse d'identifier des tendances de vente, de détecter des anomalies dans des processus industriels, ou de produire des indicateurs de performance, la capacité à extraire des connaissances à partir de données brutes est devenue un avantage compétitif déterminant.

Cependant, les outils traditionnels d'analyse de données présentent plusieurs barrières à l'entrée significatives :

- **Barrière technique** : l'utilisation de bibliothèques telles que pandas, NumPy ou d'outils comme Jupyter Notebook requiert des compétences avancées en programmation Python.
- **Courbe d'apprentissage** : la maîtrise des méthodes statistiques, de la visualisation de données et de l'interprétation des résultats nécessite une formation spécialisée.
- **Fragmentation des outils** : les analystes doivent naviguer entre multiples environnements (scripts Python, outils BI, tableurs) pour réaliser une analyse complète.

L'émergence des LLMs a ouvert une voie prometteuse pour démocratiser l'accès à l'analyse de données. Des travaux récents ont démontré qu'il est possible d'utiliser des modèles de langage comme interface entre un utilisateur non technique et des moteurs d'analyse computationnels. Cependant, les approches existantes souffrent souvent de limitations importantes : manque de transparence dans le raisonnement, absence de vérifiabilité des résultats, ou dépendance excessive à l'égard du modèle pour l'exécution des calculs.

### 2.2. État de l'art

Plusieurs paradigmes coexistent dans le domaine de l'analyse de données assistée par IA :

1. **Les agents autonomes** : des systèmes comme Code Interpreter (OpenAI) ou Gemini Data Scientist exploitent la capacité des LLMs à générer et exécuter du code Python. Cette approche, bien que puissante, présente des risques en termes de fiabilité et de répétabilité des résultats.

2. **Les interfaces en langage naturel** : des outils tels que Tableau Ask Data ou ThoughtSpot permettent d'interroger des bases de données en langage naturel, mais restent limités à des requêtes prédéfinies et ne supportent pas des workflows analytiques complexes.

3. **Les pipelines orchestrés** : des frameworks comme LangGraph ou CrewAI permettent de décomposer des tâches complexes en séquences d'étapes exécutées par des agents spécialisés. Cette approche offre une meilleure traçabilité et un contrôle plus fin sur le processus d'analyse.

La CHU Platform s'inscrit dans ce troisième paradigme, en proposant une architecture où l'orchestration des étapes analytiques est confiée à un graphe d'états LangGraph, tandis que l'exécution des calculs reste déléguée à un moteur d'analyse déterministe et vérifiable.

### 2.3. Technologies mobilisées

Le projet s'appuie sur un écosystème technologique moderne et cohérent :

| Couche | Technologies | Rôle |
|--------|-------------|------|
| **Backend API** | FastAPI, SQLAlchemy (async), Alembic, PostgreSQL | Serveur HTTP, persistance, migrations |
| **Framework agent** | LangGraph, LangChain, LangGraph Checkpoint | Orchestration, mémoire, persistance des conversations |
| **Moteur d'analyse** | pandas, NumPy, matplotlib, seaborn | Calculs statistiques, visualisation |
| **Frontend** | SvelteKit 5, Svelte 5 (runes), Tailwind CSS 4, TypeScript | Interface utilisateur réactive |
| **Infrastructure** | Docker, Docker Compose, uv (Astral) | Conteneurisation, gestion des dépendances |
| **LLM** | API OpenAI-compatible (configurable) | Génération de plans, synthèse, raisonnement |

---

## Problématique

La problématique centrale que ce projet entend résoudre peut être formulée ainsi :

> **Comment concevoir et développer une plateforme d'analyse de données qui combine la flexibilité du langage naturel pour l'interaction avec la rigueur des méthodes computationnelles pour l'exécution, tout en garantissant la transparence, la vérifiabilité et la reproductibilité des résultats ?**

Cette problématique se décline en plusieurs sous-questions :

1. **Décomposition du raisonnement analytique** : comment structurer le processus d'analyse (de la formulation de la requête à la production du rapport final) en étapes distinctes, traçables et auditables ?

2. **Séparation des préoccupations** : comment concevoir une architecture où la couche d'orchestration pilotée par l'IA est strictement séparée de la couche d'exécution computationnelle, afin que cette dernière reste déterministe et vérifiable ?

3. **Interaction en temps réel** : comment offrir une expérience utilisateur fluide où les résultats intermédiaires (plans, graphiques, étapes) sont diffusés progressivement plutôt qu'attendus en bloc ?

4. **Persistance et continuité** : comment assurer la persistance des conversations et des artefacts (graphiques, rapports) à travers les sessions, avec une flexibilité permettant de passer d'un environnement de développement (mémoire volatile) à un environnement de production (base de données durable) ?

5. **Extensibilité et modularité** : comment concevoir un système où de nouveaux outils d'analyse, de nouveaux types de graphiques ou de nouveaux agents peuvent être ajoutés sans modifier l'infrastructure existante ?

### Enjeux

Les enjeux du projet sont multiples :

- **Enjeu scientifique** : démontrer qu'une architecture à base de graphes d'états peut orchestrer efficacement des workflows analytiques complexes, en produisant des résultats dont la qualité n'est pas inférieure à celle d'une analyse manuelle menée par un data scientist.

- **Enjeu technique** : prouver la viabilité d'une approche modulaire où l'IA générative est utilisée pour la planification et la synthèse, tandis que les calculs sont délégués à un moteur déterministe, éliminant ainsi les risques d'hallucination numérique.

- **Enjeu pratique** : fournir un outil opérationnel permettant à des utilisateurs non spécialistes d'effectuer des analyses de données rigoureuses, réduisant ainsi la dépendance aux experts techniques pour les analyses exploratoires courantes.

---

## Objectifs du projet

### 4.1. Objectif général

L'objectif général de ce projet est de **concevoir, développer et déployer une plateforme modulaire d'analyse de données conversationnelle** permettant à des utilisateurs de dialoguer en langage naturel avec leurs jeux de données et d'obtenir des analyses statistiques rigoureuses, des visualisations pertinentes et des rapports synthétiques.

### 4.2. Objectifs spécifiques

1. **Conception d'un framework agent générique et réutilisable** (`packages/ai/`)
   - Développer un framework d'agent intelligent basé sur LangGraph, ignorant le domaine de l'analyse de données, capable d'appeler un LLM, d'exécuter des outils et de maintenir un état de conversation.
   - Implémenter un système de checkpointer interchangeable (InMemory ↔ Postgres) pour la persistance des conversations.
   - Assurer la gestion des erreurs, la journalisation structurée et la traçabilité des appels d'outils.

2. **Développement d'un moteur d'analyse purement computationnel** (`packages/analysis/`)
   - Implémenter un moteur d'analyse de données sans aucune dépendance à l'IA, reposant exclusivement sur pandas, NumPy et matplotlib.
   - Supporter plusieurs formats de fichiers (CSV, TSV, XLSX, Parquet, JSON, Feather) avec détection automatique de l'encodage et du délimiteur.
   - Fournir des fonctionnalités de profilage, de statistiques descriptives, de nettoyage, d'agrégation, de corrélation et de visualisation.

3. **Création d'un catalogue d'outils d'analyse** (`packages/tools/`)
   - Développer 22 outils LangChain couvrant l'inspection, les statistiques, le nettoyage, l'agrégation, les relations et la visualisation.
   - Implémenter un registre centralisé avec décorateur `@register_tool` pour l'enregistrement automatique.
   - Assurer la validation des paramètres via des schémas Pydantic.

4. **Implémentation d'un orchestrateur en trois phases** (`packages/agents/data_analyst/`)
   - **Phase 1 — Planification** : générer un plan d'exécution structuré (liste d'étapes ordonnées) à partir de la requête utilisateur.
   - **Phase 2 — Exécution** : exécuter chaque étape séquentiellement dans des sous-threads LangGraph isolés, avec détection et agrégation des artefacts (graphiques, rapports).
   - **Phase 3 — Synthèse** : produire un rapport final de type article de recherche, intégrant les résultats, les graphiques et les interprétations.

5. **Développement d'une API REST avec streaming SSE** (`apps/api/`)
   - Implémenter une API FastAPI avec endpoints CRUD pour les conversations.
   - Assurer le streaming en temps réel des événements (plan, étapes, tokens, graphiques) via Server-Sent Events (SSE).
   - Servir les graphiques générés en tant que fichiers statiques.

6. **Conception d'une interface utilisateur réactive** (`apps/web/`)
   - Développer une interface SvelteKit 5 avec disposition à trois panneaux (barre latérale, contenu principal, panneau d'artefacts).
   - Implémenter le rendu progressif des étapes d'analyse et l'affichage en temps réel des graphiques.
   - Assurer le support des thèmes clair/sombre avec un système de design tokens personnalisé.

7. **Mise en place de l'infrastructure et de la persistance** (Docker, base de données)
   - Conteneuriser PostgreSQL et pgAdmin via Docker Compose.
   - Implémenter les migrations de base de données avec Alembic.
   - Assurer la persistance des conversations et des artefacts entre les sessions.

---

## Méthodologie adoptée

### 5.1. Architecture globale et principes de conception

La méthodologie de conception s'articule autour de **quatre principes fondamentaux** qui guident l'ensemble des choix architecturaux et d'implémentation :

#### Principe 1 : Séparation stricte des préoccupations (Separation of Concerns)

L'architecture du projet est organisée en couches indépendantes, chacune ayant une responsabilité unique et clairement définie :

```
┌─────────────────────────────────────────────────────────┐
│                 Interface Utilisateur                     │
│            (SvelteKit 5 — apps/web/)                      │
├─────────────────────────────────────────────────────────┤
│                   API REST + SSE                          │
│              (FastAPI — apps/api/)                        │
├─────────────────────────────────────────────────────────┤
│              Orchestration Agent (IA)                     │
│   (LangGraph — packages/agents/data_analyst/)             │
├─────────────────────────────────────────────────────────┤
│           Framework Agent Générique                       │
│          (LangGraph — packages/ai/)                       │
├─────────────────────────────────────────────────────────┤
│              Moteur d'Analyse (déterministe)              │
│     (pandas/matplotlib — packages/analysis/)              │
└─────────────────────────────────────────────────────────┘
```

Cette séparation présente plusieurs avantages :
- **Testabilité** : chaque couche peut être testée indépendamment.
- **Maintenabilité** : les modifications dans une couche n'affectent pas les autres.
- **Réutilisabilité** : le framework agent générique et le moteur d'analyse peuvent être réutilisés dans d'autres contextes.

#### Principe 2 : Orchestration par graphe d'états

L'innovation architecturale centrale réside dans l'utilisation de **LangGraph** comme moteur d'orchestration. Le workflow d'analyse est modélisé comme un graphe d'états orienté, où chaque nœud représente une phase du traitement :

```
                    ┌──────────┐
                    │  DÉBUT   │
                    └────┬─────┘
                         ▼
                    ┌──────────┐
                    │ PLANIFIER│  Phase 1 : Générer le plan d'exécution
                    └────┬─────┘
                         ▼
                    ┌──────────┐
               ┌───▶│ EXÉCUTER │  Phase 2 : Exécuter les étapes
               │    └────┬─────┘
               │         │
               │    ┌────▼──────┐
               │    │ Plus      │
               └────│ d'étapes? │
                    └────┬──────┘
                         │ Non
                         ▼
                    ┌──────────┐
                    │SYNTHÉTISER│  Phase 3 : Générer le rapport final
                    └────┬─────┘
                         ▼
                    ┌──────────┐
                    │   FIN    │
                    └──────────┘
```

Cette approche offre plusieurs avantages par rapport à une boucle agent-outil classique :
- **Visibilité** : chaque étape du raisonnement est explicitement représentée.
- **Traçabilité** : l'état complet est accessible à tout moment.
- **Contrôle** : des chemins conditionnels permettent d'adapter le flux en fonction des résultats intermédiaires.

#### Principe 3 : Streaming premier (Streaming-First)

Toutes les interactions avec le LLM sont streamées token par token via des **Server-Sent Events (SSE)**. L'orchestrateur émet des événements structurés à chaque étape du processus :

| Type d'événement | Déclencheur | Données |
|-----------------|-------------|---------|
| `plan` | Après la planification | Plan d'exécution JSON |
| `step_started` | Début d'une étape | Métadonnées de l'étape |
| `step_token` | Pendant l'exécution | Token de texte |
| `step_finished` | Fin d'une étape | Identifiant de l'étape |
| `image` | Graphique généré | URL du graphique |
| `chart_artifact` | Graphique généré | Métadonnées complètes |
| `token` | Pendant la synthèse | Token du rapport final |
| `tool_evidence` | Résultat d'outil | Preuve de calcul |
| `done` | Fin du stream | — |

Cette approche permet à l'interface utilisateur de **rendre progressivement** les résultats, offrant une expérience interactive où l'utilisateur peut voir le raisonnement se dérouler en temps réel.

#### Principe 4 : Modularité et extensibilité

Le projet adopte une structure de **monorepo modulaire** avec gestion des dépendances via **uv** (Astral). Les packages sont organisés comme suit :

- **`packages/ai/`** : Framework agent générique (0 connaissance du domaine d'analyse)
- **`packages/analysis/`** : Moteur d'analyse purement computationnel (0 dépendance IA)
- **`packages/tools/`** : Catalogue d'outils LangChain (22 outils au total)
- **`packages/agents/`** : Agent spécialisé par domaine (Data Analyst)
- **`apps/api/`** : Application FastAPI (workspace member)
- **`apps/web/`** : Application SvelteKit frontend

Cette modularité permet :
- L'ajout de nouveaux types de graphiques sans modifier l'infrastructure.
- La création de nouveaux agents spécialisés (Data Scientist, Business Analyst...) partageant le même framework.
- Le déploiement indépendant des différentes couches.

### 5.2. Cycle de développement

Le développement a suivi une méthodologie itérative en quatre phases :

#### Phase 1 : Fondations
- Mise en place de la structure du monorepo avec uv
- Développement du framework agent générique (`packages/ai/`)
- Implémentation du moteur d'analyse (`packages/analysis/`)

#### Phase 2 : Outils et agent
- Développement des 22 outils d'analyse (`packages/tools/`)
- Implémentation de l'agent Data Analyst (`packages/agents/data_analyst/`)
- Développement de l'orchestrateur en trois phases

#### Phase 3 : API et persistance
- Développement de l'API FastAPI avec endpoints REST et SSE
- Mise en place de la base de données PostgreSQL avec SQLAlchemy et Alembic
- Implémentation du système de checkpointer interchangeable

#### Phase 4 : Interface utilisateur et déploiement
- Développement de l'interface SvelteKit 5
- Mise en place de l'infrastructure Docker
- Tests d'intégration et déploiement

### 5.3. Technologies et outils de développement

| Outil | Usage |
|-------|-------|
| **uv** | Gestionnaire de packages et environnement virtuel (Astral) |
| **pytest** | Tests unitaires et d'intégration |
| **ruff** | Linter et formateur Python |
| **mypy** | Vérification statique des types |
| **Docker Compose** | Orchestration des services (PostgreSQL, pgAdmin) |
| **Git** | Contrôle de version |
| **Alembic** | Migrations de base de données |

### 5.4. Défis techniques et solutions apportées

| Défi | Solution |
|------|----------|
| **Contamination des appels d'outils entre étapes** | Isolation des étapes via des sous-threads LangGraph avec identifiants de thread composés (`{thread_id}_run_{run_id}_step_{step.id}`) |
| **Détection d'encodage de fichiers CSV** | Algorithme de détection progressive : UTF-8 → latin-1 → cp1252 → iso-8859-15, avec tentative de délimiteurs alternatifs (`,` → `;` → `\t` → `|`) |
| **Éviction des sessions inactives** | Cache TTL avec horodatage monotone et nettoyage à chaque accès |
| **Buffering SSE par nginx** | En-tête `X-Accel-Buffering: no` dans les réponses SSE |
| **Graphiques persistants entre sessions** | Répertoire de chartes dédié, monté comme dossier statique FastAPI, avec injection via `tools.visualization.visualization.CHARTS_DIR` |

---

## Organisation du rapport

Le présent rapport est structuré comme suit :

1. **Introduction Générale** _(section courante)_ — Présente le contexte général, la problématique, les objectifs, la méthodologie et l'organisation du document.

2. **Contexte du projet** — Détaille l'état de l'art, les technologies mobilisées et le positionnement du projet dans le paysage de l'analyse de données assistée par IA.

3. **Problématique** — Formule la question centrale de recherche, les sous-questions associées et les enjeux scientifiques, techniques et pratiques.

4. **Objectifs du projet** — Énonce l'objectif général et les sept objectifs spécifiques couvrant l'ensemble des couches de la plateforme.

5. **Méthodologie adoptée** _(section courante)_ — Expose les principes architecturaux, le cycle de développement, les choix technologiques et les défis rencontrés avec leurs solutions.

6. **Architecture technique détaillée** — Décrit l'architecture complète de chaque couche : backend, frontend, framework agent, moteur d'analyse, système d'outils et infrastructure. _(à développer)_

7. **Implémentation** — Présente les détails d'implémentation des composants clés. _(à développer)_

8. **Tests et validation** — Décrit la stratégie de test et les résultats de validation. _(à développer)_

9. **Discussion** — Analyse les résultats obtenus, les limites du système et les perspectives d'amélioration. _(à développer)_

10. **Conclusion et perspectives** — Synthétise les contributions du projet et propose des directions pour les travaux futurs. _(à développer)_

---

*Document généré dans le cadre du projet CHU Platform — Plateforme d'analyse de données conversationnelle pilotée par Intelligence Artificielle.*
