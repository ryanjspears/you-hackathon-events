> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Images

GET https://api.you.com/v1/images

**Beta and unmaintained.** This endpoint works, but it is not under active development. The response shape and its availability can change without notice, so do not build a production dependency on it.

Returns the URLs of images associated to the user query.

Access is limited to early access partners. To request access, email [api@you.com](mailto:api@you.com).

Reference: https://you.com/docs/api-reference/images/images

## Authentication

- `X-API-Key` header (required) — A unique API Key is required to authorize API access. For details, see how to [get your API Key](/quickstart#get-your-api-key).

## Request

### Query parameters

- `q` (string, required, default: The image you are searching for) — The search query used to retrieve relevant image results from the web.

## Response

### 200

A JSON object containing an array of image search results.

- `images` (object, optional)
  - `results` (list of object, optional)
    - `title` (string, optional) — The title of the image result.
    - `page_url` (string, optional) — The URL of the webpage containing the image.
    - `image_url` (string, optional) — The direct URL to the image.
- `metadata` (object, optional)
  - `query` (string, optional) — Returns the original query submitted.
  - `search_uuid` (string, optional) — The unique identifier for the search request.

## Examples

**Response**

```json
{
  "images": {
    "results": [
      {
        "title": "8 Test Day Tips for Success",
        "page_url": "https://www.c2educate.com/8-test-day-tips-success/",
        "image_url": "https://s26378.pcdn.co/wp-content/uploads/sat-or-act-test-1030x519.jpg"
      }
    ]
  },
  "metadata": {
    "query": "The image you are searching for",
    "search_uuid": "c6c8f8cf-b6fc-4248-9828-24fc0dcf7be5"
  }
}
```

**SDK Code**

```python
import requests

url = "https://api.you.com/v1/images"

querystring = {"q":"The image you are searching for"}

headers = {"X-API-Key": "<apiKey>"}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())
```

```javascript
const url = 'https://api.you.com/v1/images?q=The+image+you+are+searching+for';
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

	url := "https://api.you.com/v1/images?q=The+image+you+are+searching+for"

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

HttpResponse<String> response = Unirest.get("https://api.you.com/v1/images?q=The+image+you+are+searching+for")
  .header("X-API-Key", "<apiKey>")
  .asString();
```

```csharp
using RestSharp;

var client = new RestClient("https://api.you.com/v1/images?q=The+image+you+are+searching+for");
var request = new RestRequest(Method.GET);
request.AddHeader("X-API-Key", "<apiKey>");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["X-API-Key": "<apiKey>"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/images?q=The+image+you+are+searching+for")! as URL,
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