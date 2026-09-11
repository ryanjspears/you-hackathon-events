> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Rate Limits

## Default Rate Limits

Each endpoint has its own per-second limit. These are the defaults for self-serve accounts created through [You.com Platform](https://you.com/platform):

| API                                        | Endpoint               | Default limit      |
| ------------------------------------------ | ---------------------- | ------------------ |
| Web Search API                             | `/v1/search`           | 10 requests/second |
| Contents API                               | `/v1/contents`         | 10 requests/second |
| Answer API                                 | `/v1/answer`           | 10 requests/second |
| Research API (including `background` mode) | `/v1/research`         | 10 requests/second |
| Finance Research API                       | `/v1/finance-research` | 5 requests/second  |

Enterprise plans run on custom limits set in your contract. If you're on an enterprise agreement, those limits apply instead of the defaults above.

## Rate Limit Headers

API usage is subject to rate limits based on your subscription tier. Every response includes three headers that describe your current limit:

* `X-RateLimit-Limit`—total requests allowed in the window
* `X-RateLimit-Remaining`—requests remaining in the current window
* `X-RateLimit-Reset`—Unix timestamp when the window resets

Read these headers to throttle client-side before you hit the limit, rather than waiting for a `429`.

## The 429 Response

When you exceed the limit, the API returns `429 Too Many Requests`. Honor the `Retry-After` header when present—it tells you exactly how long to wait before the next request.

## Exponential Backoff

For retries, use exponential backoff with a cap so a sustained burst does not lock you out for a long time. This example retries up to five times, doubling the wait between attempts up to a 60-second ceiling:

```python
import time
from youdotcom import You, errors

def exponential_backoff(attempt):
    return min(2 ** attempt, 60)  # Max 60 seconds

with You() as you:
    for attempt in range(5):
        try:
            response = you.search(query="test")
            break
        except errors.YouError as e:
            if e.status_code == 429 and attempt < 4:
                wait_time = exponential_backoff(attempt)
                time.sleep(wait_time)
            else:
                raise
```

## Raising Your Limits

Higher limits come with a custom plan. Book a meeting with our team to set yours, or email [api@you.com](mailto:api@you.com).