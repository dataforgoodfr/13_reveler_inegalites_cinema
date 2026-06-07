# Allocine Scraper: Browser Closure Error Fix

**Owner:** Data Team DataForGood

**Last reviewed:** 2026-05-16

**Status:** implemented

## Issue Description

The Allocine scraper was failing with repeated errors:

```
[Recuperer les donnees Allocine] Allocine scraping issue: 
  status=error 
  source_record_id=132433 
  title='Les conquerants' 
  reason=Page.goto: Target page, context or browser has been closed
```

This error occurred during the `fetch_html()` operation when the browser/page/context was unexpectedly closed while scraping was in progress.

## Root Causes

1. **Incomplete error handling in `__aexit__`**: The browser resource cleanup was not wrapped in try-except blocks. If one resource failed to close, subsequent operations would fail unpredictably.

2. **Missing page load wait state**: The `page.goto()` call had no `wait_until` parameter, so navigation could return before the page was fully loaded, leaving the page in an unstable state.

3. **No timeout on goto operation**: The `page.goto()` could hang indefinitely if the network was unstable.

4. **Premature resource cleanup**: If any exception occurred during scraping, the context manager would close all resources, but if another record was still pending in the async queue, it would fail when trying to use the now-closed page.

## Fixes Applied

### 1. **Robust Resource Cleanup in `__aexit__` (browser.py)**

Each resource closure is now wrapped in a try-except block with individual error handling:

```python
async def __aexit__(self, exc_type, exc, tb):
    """Gracefully close all browser resources with proper error handling."""
    if self.page:
        try:
            await self.page.close()
        except Exception as close_exc:
            if self.verbose:
                print(f"  [browser] Warning: Failed to close page: {close_exc}")
    
    # ... similar for context, browser, playwright
```

**Impact**: Even if one resource fails to close, others will still be properly cleaned up, preventing cascade failures.

### 2. **Page Load State Waiting (browser.py - fetch_html)**

Added explicit load state waiting to ensure pages are fully loaded:

```python
response = await self.page.goto(url, wait_until="networkidle", timeout=30000)

# Ensure page has settled before proceeding
try:
    await self.page.wait_for_load_state("networkidle", timeout=5000)
except Exception as e:
    if self.verbose:
        print(f"  [browser] Warning: Failed to wait for networkidle: {e}")
```

**Impact**: Pages now wait until network traffic settles before proceeding with scrolling/consent dismissal.

### 3. **Better Error Detection and Reporting (browser.py - fetch_html)**

Wrapped the entire `fetch_html` method in try-except to detect browser closure and provide clear diagnostics:

```python
try:
    # ... existing fetch_html logic
except (RuntimeError, Exception) as e:
    error_msg = str(e).lower()
    if any(phrase in error_msg for phrase in ["closed", "target page", "context", "browser"]):
        raise RuntimeError(
            f"Browser connection lost while fetching {url}: {e}. "
            "This may indicate the browser session was terminated unexpectedly."
        ) from e
    raise
```

**Impact**: Browser closure errors are now clearly identified and reported, making debugging easier.

## Testing Recommendations

1. **Single record scraping**: Test scraping a single film to ensure basic functionality works.
   
   ```bash
   PLAYWRIGHT_WS_ENDPOINT="your-endpoint" python -m ingestion.scraping.allocine.main sync --config config.json
   ```

2. **Batch scraping**: Test with multiple records to ensure robust cleanup between records.

3. **Network interruption simulation**: If possible, test with a network that simulates instability to ensure the timeout handling works correctly.

4. **Verbose logging**: Enable verbose mode to see detailed browser lifecycle logging:
   
   ```json
   {
     "verbose": true,
     "parallel_sessions": 1
   }
   ```

## Files Modified

- [ingestion/scraping/browser.py](ingestion/scraping/browser.py): Browser lifecycle management improvements

## Related Configuration

The following connector config parameters are relevant:

- `playwright_ws_endpoint`: The CDP endpoint (required)
- `parallel_sessions`: Number of concurrent browser sessions (default: 1)
- `verbose`: Enable detailed logging for debugging
- `headless`: Run in headless mode (default: true)

## Future Improvements

1. **Implement browser reconnection logic**: If a browser session dies, attempt to reconnect rather than fail immediately.

2. **Add circuit breaker pattern**: After N consecutive failures, pause and alert rather than repeatedly failing.

3. **Page reuse**: Reuse pages across records instead of creating/destroying pages frequently.

4. **CDT connection pooling**: If using remote CDT endpoints, implement connection pooling to avoid exhausting resources.
