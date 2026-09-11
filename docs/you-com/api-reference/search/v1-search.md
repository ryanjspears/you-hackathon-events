> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Search

POST https://ydc-index.io/v1/search
Content-Type: application/json

This endpoint is designed to return LLM-ready web results based on a user's query. Based on a classification mechanism, it can return web results and news associated with your query. If you need to feed an LLM with the results of a query that sounds like `What are the latest geopolitical updates from India`, then this endpoint is the right one for you.Each result can carry three levels of content. **Snippets** come back by default—short, keyword-centered fragments that suit a person skimming a results page, though an agent grounding an answer usually needs more. **Full page content** gives you everything, which can be a lot for the model to read. **Highlights** sit in between, returning the passages of a page that address the query and nothing else. These are query-aware and token-efficient excerpts, which matter most for agents that run several searches per task and read every result rather than the top few. Both are available through the new `extraction` parameter, as `extraction_mode: "highlights"` or `extraction_mode: "full_page"`. `GET /v1/search` still works and existing integrations will keep running, but it will not receive new feature updates. New features will be added to `POST` only, and `extraction` is only available here.

Reference: https://you.com/docs/api-reference/search/v1-search

## Authentication

- `X-API-Key` header (required) — A unique API Key is required to authorize API access. [Get your API Key with free credits](https://you.com/platform).

## Request

### Body (application/json)

- `query` (string, required) — The search query used to retrieve relevant results from the web. You can also include [search operators](https://you.com/docs/guides/search-operators) to refine your search.
- `count` (integer, optional, default: 10) — Specifies the maximum number of search results to return per section (the sections are `web` and `news`. See the JSON response to visualize them).
- `freshness` (enum or string, optional) — Specifies the freshness of the results to return. Provide either one of `day`, `week`, `month`, `year`, or a date range string in the format `YYYY-MM-DDtoYYYY-MM-DD`. When your search query includes a temporal keyword and you also set a freshness parameter, the search will use the broader (i.e., less restrictive) of the two timeframes. For example, if you use `query=news+this+week&freshness=month`, the results will use a freshness of month.
- `offset` (integer, optional, default: 0) — Indicates the `offset` for pagination. The `offset` is calculated in multiples of `count`. For example, if `count = 5` and `offset = 1`, results 5–10 will be returned. Range `0 ≤ offset ≤ 9`.
- `country` (enum, optional) — The country code that determines the geographical focus of the web results.
  - Allowed values: `AR`, `AU`, `AT`, `BE`, `BR`, `CA`, `CL`, `DK`, `FI`, `FR`, `DE`, `HK`, `IN`, `ID`, `IT`, `JP`, `KR`, `MY`, `MX`, `NL`, `NZ`, `NO`, `CN`, `PL`, `PT`, `PH`, `RU`, `SA`, `ZA`, `ES`, `SE`, `CH`, `TW`, `TR`, `GB`, `US`
- `language` (enum, optional, default: EN) — The language of the web results that will be returned (BCP 47 format).
  - Allowed values: `AR`, `EU`, `BN`, `BG`, `CA`, `ZH-HANS`, `ZH-HANT`, `HR`, `CS`, `DA`, `NL`, `EN`, `EN-GB`, `ET`, `FI`, `FR`, `GL`, `DE`, `EL`, `GU`, `HE`, `HI`, `HU`, `IS`, `IT`, `JA`, `KN`, `KO`, `LV`, `LT`, `MS`, `ML`, `MR`, `NB`, `PL`, `PT-BR`, `PT-PT`, `PA`, `RO`, `RU`, `SR`, `SK`, `SL`, `ES`, `SV`, `TA`, `TE`, `TH`, `TR`, `UK`, `VI`
- `safesearch` (enum, optional, default: moderate) — Configures the safesearch filter for content moderation. This allows you to decide whether to return NSFW content or not.
  - Allowed values: `off`, `moderate`, `strict`
- `knowledge` (enum, optional) — Requests knowledge results alongside web and news search.
  - Allowed values: `core`
- `include_domains` (list of string, optional) — A list of domains to restrict search results to. Only results from these domains will be returned. Supports up to 500 domains. This is a strict allowlist, not a boost — results are limited exclusively to the specified domains. Cannot be combined with `exclude_domains`; passing both will return a `422` error.
- `exclude_domains` (list of string, optional) — A list of domains to exclude from search results. Results from these domains will be filtered out. Supports up to 500 domains. Cannot be combined with `include_domains`; passing both will return a `422` error.
- `boost_domains` (list of string, optional) — A list of domains to boost in search ranking. Matching results from these domains receive a fixed relative ranking boost, but this is not a filter. If the boosted domains do not have matching results, results from other domains can still appear. Supports up to 500 domains. Can be combined with `exclude_domains`. Cannot be combined with `include_domains`. Passing both `boost_domains` and `include_domains` will return a `422` error.
- `extraction` (object, optional) — Ask for content to be extracted from each search result. Available on `POST` only. Omit `extraction` for a plain search that returns snippets only. The recommended way to extract page content. Supersedes the deprecated `livecrawl` and `livecrawl_formats` parameters.
  - `extraction_mode` (enum, required) — Which kind of extraction to run. `highlights` returns the passages of each page that address your query in `contents.highlights`, sized for token-sensitive agent workflows. `full_page` crawls each result and returns the page content. Pass the optional `full_page` object to override its defaults.
    - Allowed values: `highlights`, `full_page`
  - `extraction_source` (enum, optional, default: blend) — Where `full_page` content comes from. Ignored when `extraction_mode` is `"highlights"`. `blend` serves cached content when it is available and crawls the page live when it is not. This is the default. `cache` returns cached content only. It is the fastest option, and `contents` is omitted for results that have no cached content. `fetch` always crawls the page live, which returns the freshest content at the cost of higher latency.
    - Allowed values: `blend`, `cache`, `fetch`
  - `full_page` (object, optional) — Tuning for `extraction_mode: "full_page"`.
    - `extraction_formats` (list of enum, optional, default: ["markdown"]) — Content formats to return, one or both of `markdown` and `html`.
      - Allowed values: `html`, `markdown`
- `crawl_timeout` (integer, optional, default: 10) — Maximum time in seconds to wait for page content when the request crawls pages, as `extraction_mode: "full_page"` or the deprecated `livecrawl` does. Must be between 1 and 60 seconds. Default is 10 seconds.
- `livecrawl` (enum, optional, deprecated) — Deprecated. Still works on both `GET` and `POST /v1/search` but is no longer developed. Use the `extraction` object on `POST /v1/search` instead—it supersedes `livecrawl` and returns query-relevant `highlights` or full-page content. Passing a value will turn on live crawling, which returns the full page content of each result in the specified section(s). This may add latency to the request. **Pricing:** Livecrawl is billed at \$1.00 per 1,000 pages, on top of the base Web Search API rate of \$5.00 per 1,000 calls. This is the same per-page rate as the Contents API. For example, a single call with `count=10` and `livecrawl=all` crawls up to 20 pages (10 web + 10 news), adding \$0.02 to the \$0.005 base call cost.
  - Allowed values: `web`, `news`, `all`
- `livecrawl_formats` (list of enum, optional, default: ["html"], deprecated) — Deprecated. Use `extraction.full_page.extraction_formats` on `POST /v1/search` instead. Indicates the format(s) of the livecrawled content. Pass one or both values (`html`, `markdown`) by repeating the parameter: `?livecrawl_formats=html&livecrawl_formats=markdown`.
  - Allowed values: `html`, `markdown`

## Response

### 200

A JSON object containing unified search results from web and news sources

- `results` (object, optional)
  - `web` (list of object, optional)
    - `url` (string, optional) — The URL of the specific search result.
    - `title` (string, optional) — The title or name of the search result.
    - `description` (string, optional) — A brief description of the content of the search result.
    - `snippets` (list of string, optional) — An array of short, keyword-centered text fragments from the search result, built for skimming. Omitted when the request asks for `extraction_mode: "highlights"`, which returns the query-ranked `contents.highlights` instead.
    - `thumbnail_url` (string, optional) — URL of the thumbnail.
    - `page_age` (string, optional) — The age of the search result.
    - `contents` (object, optional) — Contents of a web result. `html` and/or `markdown` is returned when the request extracts full page content, and `highlights` when it asks for highlights.
      - `html` (string, optional) — The HTML content of the page.
      - `markdown` (string, optional) — The Markdown content of the page.
      - `highlights` (list of string, optional) — Query-relevant passages from the page.
    - `favicon_url` (string, optional) — The URL of the favicon of the search result's domain.
  - `news` (list of object, optional)
    - `title` (string, optional) — The title of the news result.
    - `description` (string, optional) — A brief description of the content of the news result.
    - `page_age` (string, optional) — UTC timestamp of the article's publication date.
    - `thumbnail_url` (string, optional) — URL of the thumbnail.
    - `url` (string, optional) — The URL of the news result.
    - `contents` (object, optional) — Contents of the page, returned when the request retrieves full page content.
      - `html` (string, optional) — The HTML content of the page.
      - `markdown` (string, optional) — The Markdown content of the page.
  - `knowledge` (list of object, optional) — Results backed by licensed data providers. Up to 25 are returned, limited to those relevant to the query. When none are relevant the key is omitted rather than returned as an empty array.
    - `type` (string, required) — The kind of knowledge result retrieved. `answer` is the only value currently returned. Ignore a value you do not recognize rather than failing on it, since a new kind may populate a different set of fields.
    - `title` (string, required) — The title of the knowledge result.
    - `attribution` (list of object, required) — Display credit for the data behind the result. These are credits rather than citations: each entry names a provider and carries no URL.
      - `name` (string, required) — Data provider for the knowledge result.
      - `source_description` (string, optional) — Description of the provider.
    - `description` (string, optional) — Description of the knowledge result, drawn from proprietary licensed data. Required on `type: answer` results.
    - `as_of` (string, optional) — The date the result's underlying data covers, as `YYYY-MM-DD`. Optional, and omitted when the provider reports no date.
- `metadata` (object, optional)
  - `search_uuid` (string, optional)
  - `query` (string, optional) — Returns the search query used to retrieve the results.
  - `latency` (double, optional)

## Examples

### Snippets

**Request**

```json
{
  "query": "What are the latest geopolitical updates from India",
  "count": 10,
  "include_domains": [
    "timesofindia.indiatimes.com",
    "ndtv.com",
    "thehindu.com"
  ]
}
```

**Response**

```json
{
  "results": {
    "web": [
      {
        "url": "https://timesofindia.indiatimes.com/topic/geopolitics/news",
        "title": "Geopolitics News | Latest News on Geopolitics - Times of India",
        "description": "European nations, particularly Denmark and Norway, are scrutinizing Chinese-made Yutong buses over security fears. Operators worry that 'over-the-air' software updates could allow remote immobilization of the fleet, mirroring concerns over Chinese tech in 5G networks. This potential vulnerability, inherent in connected vehicles, raises geopolitical questions about reliance on foreign manufacturers. India ...",
        "snippets": [
          "European nations, particularly Denmark and Norway, are scrutinizing Chinese-made Yutong buses over security fears. Operators worry that 'over-the-air' software updates could allow remote immobilization of the fleet, mirroring concerns over Chinese tech in 5G networks. This potential vulnerability, inherent in connected vehicles, raises geopolitical questions about reliance on foreign manufacturers. India secures 3rd place in Oz think tank's Asia Power Index",
          "Nations like New Zealand, parts of Australia, Iceland, and select South American and African countries are frequently cited as potentially more resilient to widespread conflict and its devastating aftermath. India-EU summit: FTA, defence and connectivity among key outcomes, EU seeks Paris commitment ... Pheasant Island, a tiny river island between Spain and France, uniquely swaps sovereignty every six months. This geopolitical gem's alternating control stems from the 1659 Treaty of the Pyrenees, a testament to centuries of cooperation.",
          "Check out for the latest news on geopolitics along with geopolitics live news at Times of India",
          "Despite massive viewership, he feels his content tackling geopolitical issues is too risky for corporate partners, leading him to expect no further wins. Economy enters H2 on stable footing: Finance ministry ... India's economy enters the second half of FY26 on a stable footing, supported by contained inflation, resilient domestic demand, and supportive policies. While global uncertainties pose risks to exports and capital flows, strong public capital expenditure and firming rural and urban demand are expected to maintain growth momentum."
        ],
        "thumbnail_url": "https://static.toiimg.com/photo/47529300.cms",
        "favicon_url": "https://you.com/favicon?domain=timesofindia.indiatimes.com&size=128"
      },
      {
        "url": "https://www.ndtv.com/topic/geopolitical",
        "title": "Geopolitical: Latest News, Photos, Videos on Geopolitical - NDTV.COM",
        "description": "Find Geopolitical Latest News, Videos & Pictures on Geopolitical and see latest updates, news, information from NDTV.COM. Explore more on Geopolitical.",
        "snippets": [
          "Gold surged above $4,000 an ounce to hit a record on Wednesday, driven by investors seeking safety from mounting economic and geopolitical uncertainty, alongside expectations of further interest rate cuts by the US Federal Reserve. In a landmark development that could reshape regional geopolitics, Afghan Foreign Minister Amir Khan Muttaqi of the Taliban government is all set to visit India on October 9.",
          "IndiGo flight 6E1703 from Kolkata touched down in the southern Chinese city of Guangzhou shortly before 4:00 am, officially resuming nonstop air links that had been suspended since 2020 due to the pandemic and subsequent geopolitical tensions.",
          "China's new visa programme aimed at attracting foreign tech talent launches this week, a move seen boosting Beijing's fortunes in its geopolitical rivalry with Washington as a new US visa policy prompts would-be applicants to search for alternatives.",
          "India's defence manufacturing is not only about Atmanirbharta, but also about making in India and selling to the world, according to industry leaders at the NDTV Defence Summit 2025."
        ],
        "thumbnail_url": "https://cdn.ndtv.com/common/images/ogndtv.png",
        "favicon_url": "https://you.com/favicon?domain=www.ndtv.com&size=128"
      }
    ],
    "news": [
      {
        "title": "India entering golden era of defence innovation: Rajnath",
        "description": "New Delhi, Nov 25 (PTI) Amid a rapidly changing world and evolving geopolitics, India must move beyond a reactive approach and adopt a \"proactive\" outlook to make itself future-ready, Defence Minister Rajnath Singh said on Tuesday.",
        "page_age": "2025-11-25T12:31:29",
        "thumbnail_url": "https://static.theprint.in/wp-content/uploads/2023/06/theprint_default_image_new.jpg",
        "url": "https://theprint.in/india/india-entering-golden-era-of-defence-innovation-rajnath/2791865/"
      },
      {
        "title": "India-Pakistan Tensions: Geopolitical Fallout and Regional Stability",
        "description": "As tensions between India and Pakistan persist following recent military exchanges, analysts assess the broader geopolitical implications for South Asia and global powers.",
        "page_age": "2025-11-20T08:15:00",
        "thumbnail_url": "https://cdn.ndtv.com/common/images/ogndtv.png",
        "url": "https://www.ndtv.com/india-news/india-pakistan-tensions-geopolitical-fallout-2025"
      }
    ]
  },
  "metadata": {
    "search_uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "query": "What are the latest geopolitical updates from India",
    "latency": 0.6842031478881836
  }
}
```

**SDK Code**

```python Snippets
# Use our official Python SDK to run a web search with domain filtering
from youdotcom import You

with You() as you:
  results = you.search(
    query="What are the latest geopolitical updates from India",
    count=10,
    include_domains=["timesofindia.indiatimes.com", "ndtv.com", "thehindu.com"]
  )

  # Print web results with snippets
  # Snippets are query-relevant text excerpts extracted from each page,
  # highlighting the passages most relevant to your search query
  if results.results and results.results.web:
      for result in results.results.web:
          print(f"{result.title}")
          if result.snippets:
              print(f"  {result.snippets[0]}\n")

```

```typescript Snippets
// Run a web search with domain filtering.
// POST avoids URL length limits on long domain lists.
const response = await fetch("https://ydc-index.io/v1/search", {
  method: "POST",
  headers: {
    "X-API-Key": process.env.YDC_API_KEY!,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    query: "What are the latest geopolitical updates from India",
    include_domains: ["timesofindia.indiatimes.com", "ndtv.com", "thehindu.com"],
  }),
});

const result = await response.json();
console.log(result.metadata);
console.log(result.results?.web);

```

```javascript Snippets
// Run a web search with domain filtering.
// POST avoids URL length limits on long domain lists.
const response = await fetch("https://ydc-index.io/v1/search", {
  method: "POST",
  headers: {
    "X-API-Key": process.env.YDC_API_KEY,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    query: "What are the latest geopolitical updates from India",
    include_domains: ["timesofindia.indiatimes.com", "ndtv.com", "thehindu.com"],
  }),
});

const result = await response.json();
console.log(result.metadata);
console.log(result.results?.web);

```

```go Snippets
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://ydc-index.io/v1/search"

	payload := strings.NewReader("{\n  \"query\": \"What are the latest geopolitical updates from India\",\n  \"count\": 10,\n  \"include_domains\": [\n    \"timesofindia.indiatimes.com\",\n    \"ndtv.com\",\n    \"thehindu.com\"\n  ]\n}")

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

```java Snippets
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://ydc-index.io/v1/search")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"query\": \"What are the latest geopolitical updates from India\",\n  \"count\": 10,\n  \"include_domains\": [\n    \"timesofindia.indiatimes.com\",\n    \"ndtv.com\",\n    \"thehindu.com\"\n  ]\n}")
  .asString();
```

```csharp Snippets
using RestSharp;

var client = new RestClient("https://ydc-index.io/v1/search");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"query\": \"What are the latest geopolitical updates from India\",\n  \"count\": 10,\n  \"include_domains\": [\n    \"timesofindia.indiatimes.com\",\n    \"ndtv.com\",\n    \"thehindu.com\"\n  ]\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift Snippets
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "query": "What are the latest geopolitical updates from India",
  "count": 10,
  "include_domains": ["timesofindia.indiatimes.com", "ndtv.com", "thehindu.com"]
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://ydc-index.io/v1/search")! as URL,
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

### Highlights (NEW)

**Request**

```json
{
  "query": "what is the difference between JWT and session authentication",
  "count": 10,
  "extraction": {
    "extraction_mode": "highlights"
  }
}
```

**Response**

```json
{
  "results": {
    "web": [
      {
        "url": "https://blog.logto.io/token-based-authentication-vs-session-based-authentication",
        "title": "JWT vs Session authentication · Logto blog",
        "thumbnail_url": "https://uploads.strapi.logto.io/2/session_vs_jwt_authentication_213beab414.webp",
        "page_age": "2024-12-18T00:00:00",
        "contents": {
          "highlights": [
            "Session-based authentication requires the server to query a session store, which can be slow, especially if it relies on external or centralized databases. In contrast, JWT authentication is stateless, with all necessary information stored in the client token, and utilizing signature to ensure security. This eliminates the need for session management, making it faster and more scalable, especially in distributed systems",
            "Session-based workflows follow a similar process. However, after authentication, user information is stored on the server within a session, while JWTs rely on tokens sent to the client for storage and subsequent use"
          ]
        },
        "favicon_url": "https://you.com/favicon?domain=blog.logto.io&size=128"
      },
      {
        "url": "https://heynode.com/tutorial/what-difference-between-sessions-and-json-web-tokens-jwt-authentication/",
        "title": "What Is the Difference Between Sessions and JSON Web Tokens (JWT) Authentication?",
        "contents": {
          "highlights": [
            "The main difference between sessions and JWT is how they authorize access to data. Both methods usually use a standard POST request to authenticate username and password. Once the user is verified, they will have access to specific data. The JWT token contains all the information needed to grant them access, without doing a server call. Sessions store the session ID on the client side, but still have to talk to the server to grant authorization.",
            "The 2 most popular authentication methods are JSON web tokens (JWT) and Sessions. JWT are stateless, storing all authorization data in a token on the client-side. They are easier to implement if your application uses multiple domains and back-ends. Sessions are a stateful method that work by assigning the user a session ID that gets stored in a client-side cookie."
          ]
        },
        "favicon_url": "https://you.com/favicon?domain=heynode.com&size=128"
      }
    ]
  },
  "metadata": {
    "search_uuid": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
    "query": "what is the difference between JWT and session authentication",
    "latency": 0.7431029796600342
  }
}
```

**SDK Code**

```python Highlights (NEW)
# Attach query-relevant highlights to every web result
from youdotcom import You
from youdotcom.models import Extraction, ExtractionMode

with You() as you:
  results = you.search(
    query="what is the difference between JWT and session authentication",
    count=10,
    extraction=Extraction(
      extraction_mode=ExtractionMode.HIGHLIGHTS,
    ),
  )

  # Print highlights for each web result
  # Highlights are query-relevant passages extracted from each page,
  # sized for token-sensitive agent workflows
  if results.results and results.results.web:
      for result in results.results.web:
          print(f"{result.title}")
          if result.contents and result.contents.highlights:
              for highlight in result.contents.highlights:
                  print(f"  - {highlight}")

```

```typescript Highlights (NEW)
// Use the official TypeScript SDK to run a search with highlights on every web result.
import { You } from "@youdotcom-oss/sdk";
import type { SearchRequest } from "@youdotcom-oss/sdk/models/operations";
import { Extraction, ExtractionMode } from "@youdotcom-oss/sdk/models/components";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY! });

const request: SearchRequest = {
  query: "what is the difference between JWT and session authentication",
  count: 10,
  extraction: new Extraction({ extractionMode: ExtractionMode.Highlights }),
};

const result = await you.search(request);
console.log(result.results?.web?.length);

```

```javascript Highlights (NEW)
// Use the official JavaScript SDK to run a search with highlights on every web result.
import { You } from "@youdotcom-oss/sdk";
import { Extraction, ExtractionMode } from "@youdotcom-oss/sdk/models/components";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const request = {
  query: "what is the difference between JWT and session authentication",
  extraction: new Extraction({ extractionMode: ExtractionMode.Highlights }),
};

const result = await you.search(request);
console.log(result.results?.web?.length);

```

```go Highlights (NEW)
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://ydc-index.io/v1/search"

	payload := strings.NewReader("{\n  \"query\": \"what is the difference between JWT and session authentication\",\n  \"count\": 10,\n  \"extraction\": {\n    \"extraction_mode\": \"highlights\"\n  }\n}")

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

```java Highlights (NEW)
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://ydc-index.io/v1/search")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"query\": \"what is the difference between JWT and session authentication\",\n  \"count\": 10,\n  \"extraction\": {\n    \"extraction_mode\": \"highlights\"\n  }\n}")
  .asString();
```

```csharp Highlights (NEW)
using RestSharp;

var client = new RestClient("https://ydc-index.io/v1/search");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"query\": \"what is the difference between JWT and session authentication\",\n  \"count\": 10,\n  \"extraction\": {\n    \"extraction_mode\": \"highlights\"\n  }\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift Highlights (NEW)
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "query": "what is the difference between JWT and session authentication",
  "count": 10,
  "extraction": ["extraction_mode": "highlights"]
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://ydc-index.io/v1/search")! as URL,
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

### Knowledge

**Request**

```json
{
  "query": "Nvidia latest quarterly revenue",
  "count": 5,
  "knowledge": "core"
}
```

**Response**

```json
{
  "results": {
    "web": [
      {
        "url": "https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-first-quarter-fiscal-2027",
        "title": "NVIDIA Announces Financial Results for First Quarter Fiscal 2027",
        "description": "NVIDIA today reported revenue for the first quarter ended April 26, 2026.",
        "favicon_url": "https://you.com/favicon?domain=nvidianews.nvidia.com&size=128"
      }
    ],
    "knowledge": [
      {
        "type": "answer",
        "title": "NVIDIA Corporation Total Revenues (Normalized) (Quarterly)",
        "attribution": [
          {
            "name": "Fiscal.ai",
            "source_description": "Fiscal.ai is a financial data provider that publishes as-reported and standardized company financials, segments, KPIs, and ratios extracted from filings."
          }
        ],
        "description": "NVIDIA Corporation Total Revenues (Normalized) (Quarterly)'s latest value was $81,615,000,000 in Apr 2026, up 6,424.0% since Jan 2015. Quarterly data from Jan 2015 to Apr 2026, with a maximum of $81,615,000,000 in Apr 2026 and a minimum of $1,151,000,000 in Apr 2015.",
        "as_of": "2026-04-26"
      }
    ]
  },
  "metadata": {
    "search_uuid": "c3d4e5f6-a7b8-9012-cdef-345678901234",
    "query": "Nvidia latest quarterly revenue",
    "latency": 0.8123
  }
}
```

**SDK Code**

```python Knowledge
import requests

url = "https://ydc-index.io/v1/search"

payload = {
    "query": "Nvidia latest quarterly revenue",
    "count": 5,
    "knowledge": "core"
}
headers = {
    "X-API-Key": "<apiKey>",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())
```

```javascript Knowledge
const url = 'https://ydc-index.io/v1/search';
const options = {
  method: 'POST',
  headers: {'X-API-Key': '<apiKey>', 'Content-Type': 'application/json'},
  body: '{"query":"Nvidia latest quarterly revenue","count":5,"knowledge":"core"}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go Knowledge
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://ydc-index.io/v1/search"

	payload := strings.NewReader("{\n  \"query\": \"Nvidia latest quarterly revenue\",\n  \"count\": 5,\n  \"knowledge\": \"core\"\n}")

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

```java Knowledge
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://ydc-index.io/v1/search")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"query\": \"Nvidia latest quarterly revenue\",\n  \"count\": 5,\n  \"knowledge\": \"core\"\n}")
  .asString();
```

```csharp Knowledge
using RestSharp;

var client = new RestClient("https://ydc-index.io/v1/search");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"query\": \"Nvidia latest quarterly revenue\",\n  \"count\": 5,\n  \"knowledge\": \"core\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift Knowledge
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "query": "Nvidia latest quarterly revenue",
  "count": 5,
  "knowledge": "core"
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://ydc-index.io/v1/search")! as URL,
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

### Full Page

**Request**

```json
{
  "query": "what is the difference between JWT and session authentication",
  "count": 2,
  "extraction": {
    "extraction_mode": "full_page",
    "full_page": {
      "extraction_formats": [
        "markdown"
      ]
    }
  }
}
```

**Response**

```json
{
  "results": {
    "web": [
      {
        "url": "https://blog.logto.io/token-based-authentication-vs-session-based-authentication",
        "title": "JWT vs Session authentication · Logto blog",
        "description": "A comparison of token-based and session-based authentication, covering how each stores state and where each one fits.",
        "snippets": [
          "Session-based authentication stores user information on the server and hands the client a session ID, so every request costs a lookup in the session store.",
          "JWT authentication is stateless. The token carries the claims and a signature, so the server verifies it without hitting a database."
        ],
        "page_age": "2024-12-18T00:00:00",
        "contents": {
          "markdown": "# JWT vs Session authentication\n\nSession-based authentication requires the server to query a session store on every request. JWT authentication is stateless: the token itself carries the claims, signed so the server can verify them without a lookup...\n"
        },
        "favicon_url": "https://you.com/favicon?domain=blog.logto.io&size=128"
      }
    ],
    "news": [
      {
        "title": "Session or token? Auth choices for 2026 architectures",
        "description": "Why stateless tokens won the API tier and sessions never left the browser.",
        "page_age": "2026-01-14T09:20:00",
        "url": "https://www.infoworld.com/article/session-vs-token-auth-2026",
        "contents": {
          "markdown": "# Session or token? Auth choices for 2026 architectures\n\nThe split is mostly about where revocation lives. A session can be deleted server-side the moment it is compromised, while a JWT stays valid until it expires unless you keep a denylist...\n"
        }
      }
    ]
  },
  "metadata": {
    "search_uuid": "c3d4e5f6-a7b8-9012-cdef-345678901234",
    "query": "what is the difference between JWT and session authentication",
    "latency": 3.184920310974121
  }
}
```

**SDK Code**

```python Full Page
# Crawl each result and return full Markdown content
from youdotcom import You
from youdotcom.models import Extraction, ExtractionMode, ExtractionFormat

with You() as you:
  results = you.search(
    query="what is the difference between JWT and session authentication",
    count=2,
    extraction=Extraction(
      extraction_mode=ExtractionMode.FULL_PAGE,
      full_page={"extraction_formats": [ExtractionFormat.MARKDOWN]},
    ),
  )

  # Print page content for each web result
  # Markdown is the recommended format for downstream agent consumption
  if results.results and results.results.web:
      for result in results.results.web:
          print(f"{result.title}")
          if result.contents and result.contents.markdown:
              preview = result.contents.markdown[:120].replace("\n", " ")
              print(f"  Markdown preview: {preview}...")

```

```typescript Full Page
// Use the official TypeScript SDK to run a search with full-page content on every web result.
import { You } from "@youdotcom-oss/sdk";
import type { SearchRequest } from "@youdotcom-oss/sdk/models/operations";
import { Extraction, ExtractionMode, ExtractionFormat } from "@youdotcom-oss/sdk/models/components";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY! });

const request: SearchRequest = {
  query: "what is the difference between JWT and session authentication",
  count: 2,
  extraction: new Extraction({
    extractionMode: ExtractionMode.FullPage,
    fullPage: { extractionFormats: [ExtractionFormat.Markdown] },
  }),
};

const result = await you.search(request);
console.log(result.results?.web?.length);

```

```javascript Full Page
// Use the official JavaScript SDK to run a search with full-page content on every web result.
import { You } from "@youdotcom-oss/sdk";
import { Extraction, ExtractionMode, ExtractionFormat } from "@youdotcom-oss/sdk/models/components";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const request = {
  query: "what is the difference between JWT and session authentication",
  extraction: new Extraction({
    extractionMode: ExtractionMode.FullPage,
    fullPage: { extractionFormats: [ExtractionFormat.Markdown] },
  }),
};

const result = await you.search(request);
console.log(result.results?.web?.length);

```

```go Full Page
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://ydc-index.io/v1/search"

	payload := strings.NewReader("{\n  \"query\": \"what is the difference between JWT and session authentication\",\n  \"count\": 2,\n  \"extraction\": {\n    \"extraction_mode\": \"full_page\",\n    \"full_page\": {\n      \"extraction_formats\": [\n        \"markdown\"\n      ]\n    }\n  }\n}")

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

```java Full Page
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://ydc-index.io/v1/search")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"query\": \"what is the difference between JWT and session authentication\",\n  \"count\": 2,\n  \"extraction\": {\n    \"extraction_mode\": \"full_page\",\n    \"full_page\": {\n      \"extraction_formats\": [\n        \"markdown\"\n      ]\n    }\n  }\n}")
  .asString();
```

```csharp Full Page
using RestSharp;

var client = new RestClient("https://ydc-index.io/v1/search");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"query\": \"what is the difference between JWT and session authentication\",\n  \"count\": 2,\n  \"extraction\": {\n    \"extraction_mode\": \"full_page\",\n    \"full_page\": {\n      \"extraction_formats\": [\n        \"markdown\"\n      ]\n    }\n  }\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift Full Page
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "query": "what is the difference between JWT and session authentication",
  "count": 2,
  "extraction": [
    "extraction_mode": "full_page",
    "full_page": ["extraction_formats": ["markdown"]]
  ]
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://ydc-index.io/v1/search")! as URL,
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