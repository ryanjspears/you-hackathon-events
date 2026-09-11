> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Contents Extraction

Hand the **Contents API** a list of URLs and get back clean Markdown (or HTML) plus page metadata—no headless browser, no parsing. It's the fastest way to turn arbitrary web pages into LLM-ready text without standing up your own crawler.

---

## What You'll Build

A one-call extractor that turns any URL into clean Markdown—title, body, and page metadata in a single response. The `formats` parameter lets you ask for Markdown, raw HTML, or both, and `crawl_timeout` caps the wait per page.

---

## Try It Live

Run a real Contents API request right here—no setup. Open the **Try It** panel below, paste your API key, drop in a URL, and send it against the live endpoint.

### Request

POST [https://ydc-index.io/v1/contents](https://ydc-index.io/v1/contents)

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

```curl
curl -X POST https://ydc-index.io/v1/contents \
     -H "X-API-Key: <apiKey>" \
     -H "Content-Type: application/json" \
     -d '{
  "urls": [
    "https://en.wikipedia.org/wiki/Main_Page"
  ],
  "formats": [
    "html",
    "metadata"
  ]
}'
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

### Response (200)

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

---

## Prerequisites

#### [Get a You.com API key](https://you.com/platform)

Sign up at you.com/platform. The free tier includes 100 requests/day.

```bash
pip install youdotcom        # Python ≥ 3.10
npm install @youdotcom-oss/sdk   # Node ≥ 20
```

---

## Walkthrough

#### Python

```python title="contents.py"
"""Contents — fetch clean Markdown from any URL via the You.com Contents API."""

import sys

from youdotcom import You, models

# take URL from command line, or use a default
url = sys.argv[1] if len(sys.argv) > 1 else "https://en.wikipedia.org/wiki/Retrieval-augmented_generation"

# initialize the client with your API key
with You() as you:
    pages = you.contents(
        urls=[url],
        formats=[models.ContentsFormats.MARKDOWN],
        crawl_timeout=15,
    )

# print the title and the first 500 chars of the markdown body
for page in pages:
    print(page.title)
    print(page.url)
    print()
    print((page.markdown or "")[:500] + "...")
```

```bash
export YDC_API_KEY="your-api-key-here"
python contents.py "https://en.wikipedia.org/wiki/Retrieval-augmented_generation"
```

#### TypeScript

```typescript title="contents.ts"
import { You } from "@youdotcom-oss/sdk";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY! });

const pages = await you.contents({
  urls: ["https://en.wikipedia.org/wiki/Retrieval-augmented_generation"],
  formats: ["markdown"],
  crawlTimeout: 15,
});

for (const page of pages) {
  console.log(page.title);
  console.log(page.url);
  console.log();
  console.log((page.markdown ?? "").slice(0, 500) + "...");
}
```

### Example Output

```markdown
# Retrieval-augmented generation

Retrieval-augmented generation (RAG) is a technique that grants generative
artificial intelligence models information retrieval capabilities. It modifies
interactions with a large language model so that the model responds to user
queries with reference to a specified set of documents…

(Returned alongside title, url, and metadata.site_name = "Wikipedia". Full
Markdown body is ~12,000 chars.)
```

---

## Next Steps

#### [Simple Search](/docs/examples/simple-search)

Find the URLs to extract, then feed them to Contents.

#### [Research Agent](/docs/examples/research)

Let the Research API search, read, and synthesize for you.

#### [Contents API Reference](/docs/api-reference/contents)

Full docs for formats, crawl timeouts, and metadata.

---

## Resources

* [Contents API Reference](/docs/api-reference/contents)
* [Python SDK](https://pypi.org/project/youdotcom/) · [TypeScript SDK](https://www.npmjs.com/package/@youdotcom-oss/sdk)
* [You.com OSS samples](https://github.com/youdotcom-oss)