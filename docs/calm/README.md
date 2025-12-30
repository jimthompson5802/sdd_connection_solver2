# CALM Architecture Documentation

This directory contains the FINOS CALM (Common Architecture Language Model) architecture definition for the NYT Connections Puzzle Solver application.

## Files

- `connection-solver.architecture.json` - Complete CALM architecture definition


## Validation

The architecture has been validated against FINOS CALM v1.1 schema:

```bash
utils/calm_validate_architecture.sh
```

## Generate artifacts for interactive view

```bash
utils/calm_generate_architecture_viewer.sh
```

## Viewing the Architecture

You can visualize and explore this architecture using:

#### first time after generation
```bash
cd docs/calm/html
npm install
npm start
```

### if artifacts have been generated

```bash
cd docs/calm/html
npm start
```


## Prompts used to update the CALM architecture files from the #codebase

Update CALM architecture file after application update (GHCP Agent Mode)
```text
update calm architecture definition on docs/calm/connection-solver.architecture.json to reflect new or changed nodes, interfaces and flows.
```


Identify gaps in the architecture coverage (GHCP Ask Mode)
```text
look at the metadata captured for the nodes and interfaces in docs/calm/connection_solver.architecture.json. Are there other kinds of metadata that should be captured in the architecture document?
```

Fill in high priority metadata gaps from the code base (GHCP Agent Mode)
```text
from the #codebase can you fill in the high priority gaps. If the information is not in the #codebase, state "Unknown".
```