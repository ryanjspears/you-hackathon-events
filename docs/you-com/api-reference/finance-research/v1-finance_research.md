> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Finance Research

POST https://api.you.com/v1/finance_research
Content-Type: application/json

The Finance Research API is purpose-built for financial questions. Like the Research API, it runs multiple searches, reads through sources, and synthesizes everything into a thorough, well-cited answer — but its retrieval index is optimized for financial data: earnings reports, SEC filings, analyst coverage, market data, and financial news.
Use it when you need credible, sourced answers to financial questions: company fundamentals, market trends, competitive analysis, earnings summaries, or macroeconomic research.

Reference: https://you.com/docs/api-reference/finance-research/v1-finance_research

## Authentication

- `X-API-Key` header (required) — A unique API Key is required to authorize API access. [Get your API Key with free credits](https://you.com/platform).

## Request

### Body (application/json)

- `input` (string, required) — The financial research question or complex query requiring in-depth investigation and multi-step reasoning. Note: The maximum length of the input is 40,000 characters.
- `research_effort` (enum, optional, default: deep) — Controls how much time and effort the Finance Research API spends on your question. Higher effort levels run more searches and dig deeper into sources, at the cost of a longer response time. Available levels: - `deep`: The default. Spends more time researching and cross-referencing sources. Good for most financial questions, including multi-company comparisons, earnings analysis, and regulatory research. - `exhaustive`: The most thorough option. Explores the topic as fully as possible, best suited for complex financial research tasks where you want the highest quality result.
  - Allowed values: `deep`, `exhaustive`

## Response

### 200

A JSON object containing a comprehensive finance-grade answer with citations and supporting search results

- `output` (object, required) — The research output containing the answer and sources.
  - `content` (string, required) — The comprehensive finance-grade response with inline citations. Content is a Markdown string with numbered citations that reference the items in the sources array.
  - `content_type` (enum, required) — The format of the content field.
    - Allowed values: `text`
  - `sources` (list of object, required) — A list of web sources used to generate the answer.
    - `url` (string, required) — The URL of the source webpage.
    - `title` (string, optional) — The title of the source webpage.
    - `snippets` (list of string, optional) — Relevant excerpts from the source page that were used in generating the answer.

## Examples

### Earnings analysis

**Request**

```json
{
  "input": "What were the key drivers of NVIDIA's (NVDA) revenue growth in fiscal year 2025, and how did Blackwell contribute compared to Hopper?",
  "research_effort": "deep"
}
```

**Response**

```json
{
  "output": {
    "content": "NVIDIA's fiscal 2025 revenue growth was driven primarily by Data Center accelerated-computing and AI demand: total revenue was $130.5 billion, up 114%, and Data Center revenue was $115.2 billion, up 142% [[1]]. The key full-year driver was demand for the Hopper architecture accelerated-computing platform for large language models, recommendation engines, and generative AI; in segment terms, Data Center computing grew 162% and Data Center networking grew 51%, with networking helped by Ethernet for AI/Spectrum-X [[2]].\n\nBlackwell was a major late-year contributor, but not the main full-year driver: NVIDIA began shipping Blackwell production systems in Q4 FY2025, delivered $11.0 billion of Blackwell architecture revenue in that quarter, and called it the fastest product ramp in company history [[1]]. In short, Hopper powered most of fiscal 2025's growth, while Blackwell began contributing materially in Q4 and set up the next ramp.",
    "content_type": "text",
    "sources": [
      {
        "url": "https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2025",
        "title": "NVIDIA Announces Financial Results for Fourth Quarter and Fiscal 2025"
      },
      {
        "url": "https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2025",
        "title": "NVIDIA Announces Financial Results for Third Quarter Fiscal 2025"
      },
      {
        "url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581025000021/q4fy25cfocommentary.htm",
        "title": "CFO Commentary on Fourth Quarter and Fiscal 2025 Results"
      }
    ]
  }
}
```

**SDK Code**

```python Earnings analysis
# Use our official Python SDK to run finance-grade research
from youdotcom import You
from youdotcom.models import FinanceResearchEffort

with You() as you:
    res = you.finance_research(
        input=(
            "What were the key drivers of NVIDIA's (NVDA) revenue growth in fiscal year 2025, and how did Blackwell contribute compared to Hopper?"
        ),
        research_effort=FinanceResearchEffort.DEEP,
    )

    print(res.output.content)

    # Each source carries a title and a URL you can cite
    for source in res.output.sources:
        print(f"{source.title or 'Untitled'}: {source.url}")

```

```javascript Earnings analysis
const url = 'https://api.you.com/v1/finance_research';
const options = {
  method: 'POST',
  headers: {'X-API-Key': '<apiKey>', 'Content-Type': 'application/json'},
  body: '{"input":"What were the key drivers of NVIDIA\'s (NVDA) revenue growth in fiscal year 2025, and how did Blackwell contribute compared to Hopper?","research_effort":"deep"}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go Earnings analysis
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.you.com/v1/finance_research"

	payload := strings.NewReader("{\n  \"input\": \"What were the key drivers of NVIDIA's (NVDA) revenue growth in fiscal year 2025, and how did Blackwell contribute compared to Hopper?\",\n  \"research_effort\": \"deep\"\n}")

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

```java Earnings analysis
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://api.you.com/v1/finance_research")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"input\": \"What were the key drivers of NVIDIA's (NVDA) revenue growth in fiscal year 2025, and how did Blackwell contribute compared to Hopper?\",\n  \"research_effort\": \"deep\"\n}")
  .asString();
```

```csharp Earnings analysis
using RestSharp;

var client = new RestClient("https://api.you.com/v1/finance_research");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"input\": \"What were the key drivers of NVIDIA's (NVDA) revenue growth in fiscal year 2025, and how did Blackwell contribute compared to Hopper?\",\n  \"research_effort\": \"deep\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift Earnings analysis
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "input": "What were the key drivers of NVIDIA's (NVDA) revenue growth in fiscal year 2025, and how did Blackwell contribute compared to Hopper?",
  "research_effort": "deep"
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/finance_research")! as URL,
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

### Competitive benchmarking

**Request**

```json
{
  "input": "Compare the free cash flow generation and capital allocation strategies of Apple, Microsoft, and Alphabet over the past three fiscal years",
  "research_effort": "deep"
}
```

**Response**

```json
{
  "output": {
    "content": "Assumption: \"free cash flow\" = operating cash flow minus capital expenditures / purchases of PP&E. Amounts are in USD billions.\n\n| Company | Fiscal years compared | Operating cash flow trend | Capex trend | Free cash flow trend |\n|---|---:|---:|---:|---:|\n| Apple | FY2023–FY2025 | $110.5B → $118.3B → $111.5B | $11.0B → $9.4B → $12.7B | $99.6B → $108.8B → $98.8B, roughly stable and consistently highest quality after modest capex needs [[1]]. |\n| Microsoft | FY2023–FY2025 | $87.6B → $118.5B → $136.2B | $28.1B → $44.5B → $64.6B | $59.5B → $74.1B → $71.6B; operating cash flow rose strongly, but AI/cloud infrastructure capex absorbed much of the growth [[2]]. |\n| Alphabet | FY2023–FY2025 | $101.7B → $125.3B → $164.7B | $32.3B → $52.5B → $91.4B | $69.5B → $72.8B → $73.3B; cash generation surged, but nearly all incremental operating cash flow was reinvested into technical infrastructure [[3]]. |\n\n**Capital allocation comparison**\n\n- **Apple:** Most shareholder-return-oriented. Over FY2023–FY2025, Apple spent $77.6B, $94.9B, and $90.7B on buybacks, plus about $15.0B–$15.4B annually on dividends, while capex stayed comparatively low at $9.4B–$12.7B [[1]]. Strategy: mature cash machine, modest reinvestment, aggressive buybacks, steady dividends, and balance-sheet optimization.\n- **Microsoft:** Most balanced between reinvestment and shareholder returns. Capex rose sharply from $28.1B in FY2023 to $64.6B in FY2025, reflecting cloud/AI infrastructure investment; it also paid dividends of $20.2B, $21.8B, and $24.1B and repurchased $22.2B, $17.3B, and $18.4B of stock over FY2023–FY2025 [[2]]. Strategy: prioritize AI/cloud capacity first, continue dividends and moderate buybacks second.\n- **Alphabet:** Most reinvestment-heavy. Capex nearly tripled from $32.3B in FY2023 to $91.4B in FY2025; buybacks remained large at $61.5B, $62.2B, and $45.7B, and dividends began in FY2024 with $7.4B paid in FY2024 and $10.0B in FY2025 [[3]]. Strategy: fund massive AI/data-center buildout while still returning capital, with dividends now added but buybacks lower in FY2025.\n\n**Bottom line:** Apple generated the most durable \"excess\" free cash flow relative to capital needs and used it mainly for buybacks/dividends. Microsoft and Alphabet both produced rapidly rising operating cash flow, but their free cash flow was constrained by accelerating AI infrastructure capex; Microsoft kept a more dividend-balanced return profile, while Alphabet shifted more heavily toward infrastructure reinvestment in FY2025.",
    "content_type": "text",
    "sources": [
      {
        "url": "https://s2.q4cdn.com/470004039/files/doc_financials/2025/ar/_10-K-2025-As-Filed.pdf",
        "title": "Apple Inc. 10-K Annual Report FY2025"
      },
      {
        "url": "https://www.microsoft.com/investor/reports/ar25/index.html",
        "title": "Microsoft 2025 Annual Report"
      },
      {
        "url": "https://s206.q4cdn.com/479360582/files/doc_financials/2025/q4/GOOG-10-K-2025.pdf",
        "title": "Alphabet Inc. 10-K Annual Report FY2025"
      }
    ]
  }
}
```

**SDK Code**

```python Competitive benchmarking
# Compare several companies in one finance-grade research call
from youdotcom import You
from youdotcom.models import FinanceResearchEffort

with You() as you:
    res = you.finance_research(
        input=(
            "Compare the free cash flow generation and capital allocation strategies of Apple, Microsoft, and Alphabet over the past three fiscal years"
        ),
        research_effort=FinanceResearchEffort.DEEP,
    )

    print(res.output.content)
    print(f"{len(res.output.sources)} sources")

```

```javascript Competitive benchmarking
const url = 'https://api.you.com/v1/finance_research';
const options = {
  method: 'POST',
  headers: {'X-API-Key': '<apiKey>', 'Content-Type': 'application/json'},
  body: '{"input":"Compare the free cash flow generation and capital allocation strategies of Apple, Microsoft, and Alphabet over the past three fiscal years","research_effort":"deep"}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go Competitive benchmarking
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.you.com/v1/finance_research"

	payload := strings.NewReader("{\n  \"input\": \"Compare the free cash flow generation and capital allocation strategies of Apple, Microsoft, and Alphabet over the past three fiscal years\",\n  \"research_effort\": \"deep\"\n}")

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

```java Competitive benchmarking
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://api.you.com/v1/finance_research")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"input\": \"Compare the free cash flow generation and capital allocation strategies of Apple, Microsoft, and Alphabet over the past three fiscal years\",\n  \"research_effort\": \"deep\"\n}")
  .asString();
```

```csharp Competitive benchmarking
using RestSharp;

var client = new RestClient("https://api.you.com/v1/finance_research");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"input\": \"Compare the free cash flow generation and capital allocation strategies of Apple, Microsoft, and Alphabet over the past three fiscal years\",\n  \"research_effort\": \"deep\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift Competitive benchmarking
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "input": "Compare the free cash flow generation and capital allocation strategies of Apple, Microsoft, and Alphabet over the past three fiscal years",
  "research_effort": "deep"
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/finance_research")! as URL,
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