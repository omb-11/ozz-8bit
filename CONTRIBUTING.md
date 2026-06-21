# Contributing

## Workflow

1. Create a branch for your change.
2. Run the test suite.
3. Update documentation when behavior changes.
4. Keep legacy MK1 assets intact unless the change explicitly targets legacy preservation or migration.

## Local Checks

```powershell
python -m unittest discover -s tests -v
cd web-visualizer
npm install
npm run build
```

## Commit Style

Use focused commit messages such as:

- `feat: add indexed addressing to assembler and emulator`
- `docs: expand instruction set reference`
- `test: cover interrupt return flow`
