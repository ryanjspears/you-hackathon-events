> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Research Task Status

GET https://api.you.com/v1/research/{task_id}

Retrieve the current status of a background research task. While the task is in progress, the `result` field is `null`. Once the task reaches `completed`, the full research result is returned in `result`. If the task fails, `status` is `failed` and `error` contains a diagnostic message.

Reference: https://you.com/docs/api-reference/research/v1-research-task

## Authentication

- `X-API-Key` header (required) — A unique API Key is required to authorize API access. [Get your API Key with free credits](https://you.com/platform).

## Request

### Path parameters

- `task_id` (string, required) — The unique identifier of the background research task.

## Response

### 200

The current status and, if completed, the result of the task.

- `id` (string, required) — Unique identifier for the background research task.
- `task_type` (enum, required) — The task type.
  - Allowed values: `research`
- `status` (enum, required) — The status of a background research task.
  - Allowed values: `queued`, `running`, `completed`, `failed`, `cancelled`
- `created_at` (datetime, required) — When the task was created, in RFC 3339 format.
- `updated_at` (datetime, required, nullable) — When the task was last updated, in RFC 3339 format. `null` if the task has not yet started running.
- `completed_at` (datetime, required, nullable) — When the task reached a terminal status, in RFC 3339 format. `null` if the task has not yet completed, failed, or been cancelled.
- `error` (string, required, nullable) — A diagnostic message when `status` is `failed`. `null` for all other statuses.
- `input` (object, required) — The original request parameters submitted for the background research task.
  - `input` (string, required) — The research question that was submitted.
  - `research_effort` (enum, required) — The research effort level that was submitted.
    - Allowed values: `lite`, `standard`, `deep`, `exhaustive`, `frontier`
  - `background` (boolean, required) — Whether background mode was requested.
  - `output_schema` (map from string to any, required, nullable) — The structured output schema that was submitted, if any.
  - `source_control` (object, required, nullable) — The source control configuration that was submitted, if any.
  - `type` (enum, required) — The task type.
    - Allowed values: `research`
- `result` (object, required, nullable) — The final research result when `status` is `completed`. `null` while the task is queued or running.
  - `output` (object, required) — An object containing the content, content type, and source list.
    - `content` (string or map from string to any, required) — The comprehensive response with inline citations. By default, content is a Markdown string with numbered citations that reference the items in the sources array. When `output_schema` is provided, content is a JSON object that conforms to the requested schema.
    - `content_type` (enum, required) — The format of the content field.
      - Allowed values: `text`, `object`
    - `sources` (list of object, required) — A list of web sources used to generate the answer.
      - `url` (string, required) — The URL of the source webpage.
      - `title` (string, optional) — The title of the source webpage.
      - `snippets` (list of string, optional) — Relevant excerpts from the source page that were used in generating the answer.
  - `warnings` (list of string, required) — A list of warnings generated during research, such as source access issues or partial results. Empty when no warnings occurred.

## Examples

**Response**

```json
{
  "id": "f1e2d3c4-0000-0000-0000-000000000000",
  "task_type": "research",
  "status": "completed",
  "created_at": "2026-06-26T00:00:00Z",
  "updated_at": "2026-06-26T00:00:30Z",
  "completed_at": "2026-06-26T00:00:30Z",
  "error": null,
  "input": {
    "input": "Compare 'Acme Logistics LLC' (DE) and 'Acme Logistics' (NJ). Are they the same business?",
    "research_effort": "frontier",
    "background": true,
    "output_schema": null,
    "source_control": null,
    "type": "research"
  },
  "result": {
    "output": {
      "content": "Acme Logistics LLC (DE) and Acme Logistics (NJ) are two distinct entities...",
      "content_type": "text",
      "sources": []
    }
  },
  "warnings": []
}
```

**SDK Code**

```python
# Poll a background research task until it reaches a terminal state
from youdotcom import You
from youdotcom.research_helpers import poll_research_task

task_id = "f1e2d3c4-0000-0000-0000-000000000000"

with You() as you:
    # Returns a TaskDetail with status == completed once the task lands.
    # Raises RuntimeError on failed/cancelled, TimeoutError after timeout_s.
    task = poll_research_task(you, task_id, timeout_s=600)

    print(f"Status: {task.status.value}")
    print(task.result.output.content)

    # When the task failed before completion, raise on the call above.
    # When it succeeded, each source carries a title and a URL you can cite.
    for source in task.result.output.sources:
        print(f"{source.title or 'Untitled'}: {source.url}")

```

```javascript
const url = 'https://api.you.com/v1/research/f1e2d3c4-0000-0000-0000-000000000000';
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

	url := "https://api.you.com/v1/research/f1e2d3c4-0000-0000-0000-000000000000"

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

HttpResponse<String> response = Unirest.get("https://api.you.com/v1/research/f1e2d3c4-0000-0000-0000-000000000000")
  .header("X-API-Key", "<apiKey>")
  .asString();
```

```csharp
using RestSharp;

var client = new RestClient("https://api.you.com/v1/research/f1e2d3c4-0000-0000-0000-000000000000");
var request = new RestRequest(Method.GET);
request.AddHeader("X-API-Key", "<apiKey>");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["X-API-Key": "<apiKey>"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/research/f1e2d3c4-0000-0000-0000-000000000000")! as URL,
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