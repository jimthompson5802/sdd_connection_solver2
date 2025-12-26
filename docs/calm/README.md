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

# first time after generation
```bash
cd docs/calm/html
npm install
npm start
```

# if artifacts have been generated

```bash
cd docs/calm/html
npm start
```
