# Style Guide — data-files

Unique conventions:

- Canonical puzzle and word list data are CSV files under `/data` (e.g., `puzzle_YYYY_MM_DD.csv`, `word_list*.csv`).
- Treat CSVs as read-only inputs for analysis and testing. If a feature requires persistence, encapsulate writes behind a service.
- Ensure any CSV parsing handles common edge-cases (quoted commas, CRLF) and yields consistent data shapes for downstream services.

File examples: `data/puzzle_2025_10_09.csv`, `data/word_list1.csv`.
