# Data Layer — Deep Dive

## Overview

The project currently uses CSV files as primary data assets for puzzles and word lists (under `/data`). There's no evidence of an RDBMS or other database in config files — the data-layer is file-based and lightweight.

## Key files

- `data/puzzle_*.csv`, `data/word_list*.csv` — canonical puzzle inputs and word lists.
- Data loading and parsing utilities are expected to live in backend services (e.g., recommendation engine or helper modules).

## Patterns and constraints

- Treat CSV files as the canonical input source; do not assume transactional persistence.
- Any feature that needs persistence beyond CSV should encapsulate data access behind a service interface to allow future migration.

## Implementation guidance

- Add data access helpers under `backend/src/services/` (e.g., `data_service.py`) when reading CSVs so parsing and caching are centralized.
- Avoid writing to the CSV files directly from many places; centralize writes if required.

---
