> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Research Task Stream

GET https://api.you.com/v1/research/{task_id}/stream

Stream real-time progress for a background research task using Server-Sent Events (SSE). The stream starts with a `connected` event, followed by periodic ping comments to keep the connection alive, and closes when the task reaches a terminal status (`completed`, `failed`, or `cancelled`), at which point a terminal event matching the status name is sent. To replay events after reconnecting, pass `?from_id=N` with the last event ID you received. After the stream closes, call `GET /v1/research/{task_id}` to retrieve the full `result` object.

Reference: https://you.com/docs/api-reference/research/v1-research-task-stream

## Authentication

- `X-API-Key` header (required) — A unique API Key is required to authorize API access. [Get your API Key with free credits](https://you.com/platform).

## Request

### Path parameters

- `task_id` (string, required) — The unique identifier of the background research task.

### Query parameters

- `from_id` (integer, optional, default: 0) — Optional event ID to replay events from after reconnecting.

## Response

### 200

A Server-Sent Events stream of task progress updates.

- Streaming response of `string`.

## Examples

**Response**

```json
"id: 0\nevent: connected\ndata: {\"type\": \"connected\", \"task_id\": \"f1e2d3c4-0000-0000-0000-000000000000\", \"status\": \"running\"}\n\n: ping - 2026-06-26T00:00:15Z\n\n: ping - 2026-06-26T00:00:30Z\n\nevent: completed\ndata: {\"type\": \"completed\", \"data\": {\"message\": \"Task completed\", \"error\": null}, \"sequence\": 0, \"task_id\": \"f1e2d3c4-0000-0000-0000-000000000000\"}\n"
```

**SDK Code**

```python
# Iterate Server-Sent Events from a background research task
from youdotcom import You
from youdotcom.research_helpers import stream_research

task_id = "f1e2d3c4-0000-0000-0000-000000000000"

with You() as you:
    for event in stream_research(you, task_id):
        # event.id is the SSE id directive, event.event is the raw event name,
        # event.data is the parsed JSON payload (or the raw string when not JSON).
        print(f"[id={event.id}] {event.event}: {event.data}")

        # The stream closes when the task hits a terminal status.
        if event.event == "completed":
            break
        if event.event in {"failed", "cancelled"}:
            raise RuntimeError(f"Research task ended in non-completed state: {event.event}")

```

```javascript
const url = 'https://api.you.com/v1/research/f1e2d3c4-0000-0000-0000-000000000000/stream';
const options = {method: 'GET', headers: {'X-API-Key': '<apiKey>'}};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go
package main

import (
	"fmt"
	"net/http"
	"io"
)

func main() {

	url := "https://api.you.com/v1/research/f1e2d3c4-0000-0000-0000-000000000000/stream"

	req, _ := http.NewRequest("GET", url, nil)

	req.Header.Add("X-API-Key", "<apiKey>")

	res, _ := http.DefaultClient.Do(req)

	defer res.Body.Close()
	body, _ := io.ReadAll(res.Body)

	fmt.Println(res)
	fmt.Println(string(body))

}
```

```java
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.get("https://api.you.com/v1/research/f1e2d3c4-0000-0000-0000-000000000000/stream")
  .header("X-API-Key", "<apiKey>")
  .asString();
```

```csharp
using RestSharp;

var client = new RestClient("https://api.you.com/v1/research/f1e2d3c4-0000-0000-0000-000000000000/stream");
var request = new RestRequest(Method.GET);
request.AddHeader("X-API-Key", "<apiKey>");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["X-API-Key": "<apiKey>"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/research/f1e2d3c4-0000-0000-0000-000000000000/stream")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "GET"
request.allHTTPHeaderFields = headers

let session = URLSession.shared
let dataTask = session.dataTask(with: request as URLRequest, completionHandler: { (data, response, error) -> Void in
  if (error != nil) {
    print(error as Any)
  } else {
    let httpResponse = response as? HTTPURLResponse
    print(httpResponse)
  }
})

dataTask.resume()
```