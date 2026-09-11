> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Simple Search

If you're new to the You.com API, this is the right place to begin. Before building RAG pipelines or research agents, you need to understand the foundation: the **Search API**. Send a query. Get back accurate web and news results.

The Search API gives you direct access to You.com's search index—the same index that powers our Research API and our own search engine. You get titles, URLs, and descriptions for the most relevant pages on the web, fast. Then you decide what to do with them: filter them, rank them, display them in a UI, or feed them into a language model to synthesize an answer.

This example shows the simplest possible way to call it: a Python script and a small Next.js web app you can deploy to Vercel.

---

## Try It Live

Run a real Search API request right here—no setup, no separate app to deploy. Open the **Try It** panel below, paste your API key, edit the query, and send it against the live endpoint.

### Request

POST [https://ydc-index.io/v1/search](https://ydc-index.io/v1/search)

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

```curl Snippets
curl -X POST https://ydc-index.io/v1/search \
     -H "X-API-Key: <apiKey>" \
     -H "Content-Type: application/json" \
     -d '{
  "query": "What are the latest geopolitical updates from India",
  "count": 10,
  "include_domains": [
    "timesofindia.indiatimes.com",
    "ndtv.com",
    "thehindu.com"
  ]
}'
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

### Response (200)

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

---

## What You'll Build

The simplest possible example of the You.com Search API—pass a query, get back web results. No agents, no chaining, no extra dependencies. The `unified` endpoint returns title, URL, and description for the top results, ready to feed an LLM or render in a UI.

---

## Prerequisites

#### [Get a You.com API key](https://you.com/platform)

Sign up at you.com/platform to get your API key. The free tier includes 100 requests/day.

Install the SDK for your language:

```bash
pip install youdotcom        # Python ≥ 3.10
npm install @youdotcom-oss/sdk   # Node ≥ 20
```

---

## Run It

#### Python

The quickest way to see the API in action is the command line.

```python title="simple_search.py"
"""Simple Search — the "hello world" of the You.com Search API."""

import sys

from youdotcom import You

# take query from command line args, or use a default
query = sys.argv[1] if len(sys.argv) > 1 else "best programming languages 2026"

# initialize the client with your API key
you = You()

# run the search
response = you.search(query=query, count=5)

# print each result
for result in response.results.web:
    print(f"{result.title}")
    print(f"  {result.url}")
    print(f"  {result.description}")
    print()
```

Run it:

```bash
export YDC_API_KEY="your-api-key-here"
python simple_search.py "what is retrieval augmented generation"
```

No query? No problem—the example falls back to a default one, so `python simple_search.py` works too.

#### TypeScript

```typescript title="simple-search.ts"
import { You } from "@youdotcom-oss/sdk";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY! });

const response = await you.search({
  query: "best programming languages 2026",
  count: 5,
});

for (const result of response.results.web) {
  console.log(result.title);
  console.log(`  ${result.url}`);
  console.log(`  ${result.description}`);
  console.log();
}
```

The repo also includes a Next.js web app if you'd rather see it in a browser:

```bash
cp .env.example .env.local
# edit .env.local and add your key
npm install
npm run dev
```

Open [localhost:3000](http://localhost:3000), type a query, and the results show up as cards with favicons. The search happens server-side so your API key never touches the browser.

**Deploy to Vercel:**

#### Push to GitHub

Push this repo to your GitHub account.

#### Import on Vercel

Import it at [vercel.com/new](https://vercel.com/new).

#### Add your API key

Add `YDC_API_KEY` as an environment variable in your Vercel project settings.

#### Deploy

Hit deploy. Vercel auto-detects Next.js and handles the rest.

**What you get back:**

Each result has a title, URL, and a short description pulled from the page—clean, structured, and ready to use:

```
Title: What is RAG (Retrieval-Augmented Generation)? | IBM
  https://www.ibm.com/topics/retrieval-augmented-generation
  RAG is an AI framework that combines the strengths of traditional information
  retrieval systems with the capabilities of generative large language models.
```

---

## Next Steps

#### [Research Agent](/docs/examples/research)

Instead of raw results, get a synthesized, cited answer written by an agent that reads the web for you.

#### [Contents Extraction](/docs/examples/contents)

Turn any URL into clean Markdown—ideal for LLM ingestion.

#### [Search API Reference](/docs/api-reference/search/v1-search)

Full docs for filtering by freshness, country, language, and more.

---

## Resources

* [Search API Reference](/docs/api-reference/search/v1-search)
* [Python SDK on PyPI](https://pypi.org/project/youdotcom/) (`pip install youdotcom`)
* [TypeScript SDK on npm](https://www.npmjs.com/package/@youdotcom-oss/sdk) (`npm install @youdotcom-oss/sdk`)
* [GitHub: ydc-simple-search-sample](https://github.com/youdotcom-oss/ydc-simple-search-sample)
* [Try the Search API in your browser](/docs/api-reference/search/v1-search)