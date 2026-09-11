> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Account Balance

GET https://api.you.com/v1/billing/account_balance

Returns the remaining credit balance for the billing entity associated with the API key used in the request.

The billing entity is determined by the account context:
- **Organization members** — the balance reflects the shared credit pool
  for the entire organization (tenant).

- **Individual users** — the balance reflects the credits available on
  the individual user account.


Balance values are expressed in cents, so a value of `718924.5` corresponds to **$7,189.24** in remaining credits.

Reference: https://you.com/docs/api-reference/billing/get-account-balance

## Authentication

- `X-API-Key` header (required) — The unique API Key required to authorize API access. Learn how to get yours in the ["Get your API key" section of the documentation](/docs/quickstart#get-your-api-key).

## Response

### 200

A JSON object containing the credit balance for the billing entity associated with the API key.

- `data` (object, required)
  - `type` (string, required) — The type of billing entity. Always `"account"`.
  - `id` (string, required) — A hashed identifier for the billing entity (user or organization). This value is stable for the lifetime of the entity.
  - `attributes` (object, required)
    - `balance` (double, required) — Remaining credit balance in cents. Divide by 100 to convert to USD. For example, `718924.5` equals $7,189.24.

## Examples

**Response**

```json
{
  "data": {
    "type": "account",
    "id": "e48a0acc172f1bd716527b65dcae373cf6d7a532dfb9fa6a1f962799eeaca84f",
    "attributes": {
      "balance": 718924.5
    }
  }
}
```

**SDK Code**

```python
import requests

url = "https://api.you.com/v1/billing/account_balance"

headers = {"X-API-Key": "<apiKey>"}

response = requests.get(url, headers=headers)

print(response.json())
```

```javascript
const url = 'https://api.you.com/v1/billing/account_balance';
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

	url := "https://api.you.com/v1/billing/account_balance"

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

HttpResponse<String> response = Unirest.get("https://api.you.com/v1/billing/account_balance")
  .header("X-API-Key", "<apiKey>")
  .asString();
```

```csharp
using RestSharp;

var client = new RestClient("https://api.you.com/v1/billing/account_balance");
var request = new RestRequest(Method.GET);
request.AddHeader("X-API-Key", "<apiKey>");
IRestResponse response = client.Execute(request);
```

```swift
import Foundation

let headers = ["X-API-Key": "<apiKey>"]

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/billing/account_balance")! as URL,
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