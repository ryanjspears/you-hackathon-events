> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Contents

POST https://ydc-index.io/v1/contents
Content-Type: application/json

Returns the HTML or Markdown of a target webpage.

Reference: https://you.com/docs/api-reference/contents

## Authentication

- `X-API-Key` header (required) — A unique API Key is required to authorize API access. [Get your API Key with free credits](https://you.com/platform).

## Request

### Body (application/json)

- `urls` (list of string, optional) — Array of URLs to fetch the contents from.
- `formats` (list of enum, optional) — Array of content formats to return. All included formats are returned in the response. Include "metadata" to get JSON-LD and OpenGraph information, if available.
  - Allowed values: `html`, `markdown`, `metadata`
- `crawl_timeout` (integer, optional, default: 10) — Maximum time in seconds to wait for page content. Must be between 1 and 60 seconds. Default is 10 seconds.
- `max_age` (integer, optional, nullable) — Maximum allowed age of cached content in seconds. When set, cached content older than this threshold is ignored and the page is re-fetched. Must be 0 or greater. Default is null (no age limit, cached content is returned regardless of age).

## Response

### 200

An array of JSON objects containing the page content of each web page

- `list of object`
  - `url` (string, optional) — The webpage URL whose content has been fetched.
  - `title` (string, optional) — The title of the web page.
  - `html` (string, optional, nullable) — The retrieved HTML content of the web page.
  - `markdown` (string, optional, nullable) — The retrieved Markdown content of the web page.
  - `metadata` (object, optional) — Metadata about the web page. Only returned when 'metadata' is included in the formats array.
    - `site_name` (string, optional, nullable) — The OpenGraph site name of the web page.
    - `favicon_url` (string, optional) — The URL of the favicon of the web page's domain.

## Examples

**Request**

```json
{
  "urls": [
    "https://en.wikipedia.org/wiki/Main_Page"
  ],
  "formats": [
    "html",
    "metadata"
  ]
}
```

**Response**

```json
[
  {
    "url": "https://en.wikipedia.org/wiki/Main_Page",
    "title": "Wikipedia, the free encyclopedia",
    "html": "Wikipedia was just a dream.\ndiv class=\"frb-subheader\">\n<span class=\"frb-replaced\">December 2</span>: Readers <span class=\"frb-replaced\">in the United States</span> deserve an explanation.\n</div>\n</div>\n<div class=\"frb-message-content\">\n<p>\nPlease don't skip this 1-minute read. It's <span class=\"frb-replaced\">Tuesday</span>, <span class=\"frb-replaced\">December 2</span>, and if you're like us, you've used Wikipedia countless times. To settle an argument with a friend. To satisfy a curiosity. Whether it's 3 in the morning or afternoon, Wikipedia is useful in your life. Please give <span class=\"frb-replaced\">$2.75</span>.\n</p>\n<p>\nWikipedia's been around since 2001. Back then, it was just a wildly ambitious, probably impossible dream. But it came together piece by piece—created by people, not machines. Wikipedia's not perfect, but it's always been free thanks to everyday readers.\n</p>\n<p>\nOnly 2% ever donate. But that small group makes a big difference. When you support Wikipedia, you're standing up for something simple",
    "metadata": {
      "site_name": "Wikipedia",
      "favicon_url": "https://api.ydc-index.io/favicon?domain=en.wikipedia.org&size=128"
    }
  }
]
```

**SDK Code**

```python
# Use our official Python SDK to fetch the contents of a web page
from youdotcom import You
from youdotcom.models import ContentsFormats

with You() as you:
    res = you.contents(
        urls=[
            "https://en.wikipedia.org/wiki/Main_Page",
        ],
        formats=[ContentsFormats.HTML],
    )

    # Print the fetched HTML content
    for page in res:
        print(f"Title: {page.title}")
        print(f"HTML: {page.html[:500]}...")  # First 500 chars

```

```typescript
// Use our official TypeScript SDK to fetch the contents of a web page
import { You } from "@youdotcom-oss/sdk";
import type { ContentsRequest } from "@youdotcom-oss/sdk/models/operations";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const request: ContentsRequest = {
  urls: ["https://en.wikipedia.org/wiki/Main_Page"],
  formats: ["html", "metadata"],
};

const result = await you.contents(request);
console.log(result);

```

```javascript
// Use our official JavaScript SDK to fetch the contents of a web page
import { You } from "@youdotcom-oss/sdk";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const request = {
  urls: ["https://en.wikipedia.org/wiki/Main_Page"],
  formats: ["html", "metadata"],
};

const result = await you.contents(request);
console.log(result);

```

```go
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://ydc-index.io/v1/contents"

	payload := strings.NewReader("{\n  \"urls\": [\n    \"https://en.wikipedia.org/wiki/Main_Page\"\n  ],\n  \"formats\": [\n    \"html\",\n    \"metadata\"\n  ]\n}")

	req, _ := http.NewRequest("POST", url, payload)

	req.Header.Add("X-API-Key", "<apiKey>")
	req.Header.Add("Content-Type", "application/json")

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

HttpResponse<String> response = Unirest.post("https://ydc-index.io/v1/contents")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"urls\": [\n    \"https://en.wikipedia.org/wiki/Main_Page\"\n  ],\n  \"formats\": [\n    \"html\",\n    \"metadata\"\n  ]\n}")
  .asString();
```

```csharp
using RestSharp;

var client = new RestClient("https://ydc-index.io/v1/contents");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"urls\": [\n    \"https://en.wikipedia.org/wiki/Main_Page\"\n  ],\n  \"formats\": [\n    \"html\",\n    \"metadata\"\n  ]\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "urls": ["https://en.wikipedia.org/wiki/Main_Page"],
  "formats": ["html", "metadata"]
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://ydc-index.io/v1/contents")! as URL,
                                        cachePolicy: .useProtocolCachePolicy,
                                    timeoutInterval: 10.0)
request.httpMethod = "POST"
request.allHTTPHeaderFields = headers
request.httpBody = postData as Data

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