# Testing

Run all frontend tests:

```bash
pytest -q hintzCompiler/tests
```

Pipeline integration test:
- Located at `hintzCompiler/tests/test_mlir_pipeline.py`
- Skips automatically if MLIR/LLVM tools are missing

## Notes

- The test suite expects the repo layout as checked in.
- The web testbed has its own tests in `hintzCompiler/tests/test_web_samples.py`.
