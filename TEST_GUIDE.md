# Testing Guide for SAM

## Running Tests

### Prerequisites
```bash
pip install pytest pytest-asyncio pytest-cov
```

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_ai_engine.py -v
```

### Run with Coverage
```bash
pytest --cov=backend tests/
```

## Test Structure

### Unit Tests
- `test_ai_engine.py` - AI Engine tests
- `test_voice_processor.py` - Voice processing tests
- `test_memory_manager.py` - Memory management tests
- `test_api_manager.py` - API management tests
- `test_task_executor.py` - Task execution tests
- `test_scheduler.py` - Task scheduling tests

### Test Categories

#### 1. AI Engine Tests
- Initialization
- Activation/Deactivation
- Task command detection
- Model selection
- Mood analysis
- Processing workflow

#### 2. Voice Processor Tests
- Initialization
- Speech-to-text
- Text-to-speech
- Microphone listing
- Voice properties

#### 3. Memory Manager Tests
- History storage
- Context retrieval
- Statistics
- History cleanup

#### 4. API Manager Tests
- API initialization
- Response generation
- Failover mechanism
- Statistics tracking

#### 5. Task Executor Tests
- Safety checks
- Blocked keywords
- Dangerous patterns
- Task execution

#### 6. Scheduler Tests
- Task addition/removal
- Task execution
- Frequency handling

## Test Execution Examples

### Run tests with markers
```bash
# Run only async tests
pytest -m asyncio

# Run specific test class
pytest tests/test_ai_engine.py::TestSAMEngine -v

# Run specific test method
pytest tests/test_ai_engine.py::TestSAMEngine::test_engine_activation -v
```

### Coverage Report
```bash
pytest --cov=backend --cov-report=html
# Open htmlcov/index.html in browser
```

## Mocking in Tests

Tests use `unittest.mock` for:
- Mocking API calls
- Simulating voice input
- Testing failover scenarios
- Isolating components

## Debugging Tests

### Enable verbose output
```bash
pytest -vv tests/
```

### Run with print statements
```bash
pytest -s tests/
```

### Drop into debugger
```bash
pytest --pdb tests/
```

## Continuous Integration

Setup GitHub Actions for automated testing:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest --cov=backend tests/
```

## Performance Testing

```bash
# Test with timing
pytest --durations=10 tests/
```

## Assertion Examples

```python
# Basic assertions
assert engine.is_active == True
assert response == "expected"

# Collection assertions
assert len(history) == 5
assert "key" in dictionary

# Exception assertions
with pytest.raises(ValueError):
    function_that_raises()

# Async assertions
assert result is not None
```

## Best Practices

1. **One test per method** - Focus tests on single functionality
2. **Use fixtures** - Reuse common setup code
3. **Mock external calls** - Don't make real API calls
4. **Test edge cases** - Error conditions, empty inputs
5. **Descriptive names** - test_engine_should_raise_error_on_invalid_input

## Troubleshooting

### Tests timing out
- Check for infinite loops
- Verify mock setup
- Increase timeout: `@pytest.mark.timeout(300)`

### Import errors
- Ensure conftest.py is in tests directory
- Check PYTHONPATH
- Verify relative imports

### Async test failures
- Use `@pytest.mark.asyncio` decorator
- Ensure event loop setup in conftest.py
- Check for concurrent modification errors
