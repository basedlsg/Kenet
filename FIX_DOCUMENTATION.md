# Vector Database Query Method Fix

## Problem Summary

An `AttributeError: 'list' object has no attribute 'id'` occurred in `tests/test_vector_db.py:43` during geometric pruning tests.

## Root Cause

The `query` method returns a list of `ScoredPoint` objects. The test was attempting to access the `.id` attribute directly on this list (`results.id`) instead of on the first element of the list (`results[0].id`).

## Solution

The fix was applied in `tests/test_vector_db.py:43`.

**Before:**
```python
self.assertEqual(results.id, 100)
```

**After:**
```python
self.assertEqual(results[0].id, 100)
```

## Verification

All tests in `tests/test_vector_db.py` now pass successfully.