> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Research

POST https://api.you.com/v1/research
Content-Type: application/json

Research goes beyond a single web search. In response to your question, it runs multiple searches, reads through the sources, and synthesizes everything into a thorough, well-cited answer. Use it when a question is too complex for a simple lookup, and when you need a response you can actually trust and verify.

Reference: https://you.com/docs/api-reference/research/v1-research

## Authentication

- `X-API-Key` header (required) — A unique API Key is required to authorize API access. [Get your API Key with free credits](https://you.com/platform).

## Request

### Body (application/json)

- `input` (string, required) — The research question or complex query requiring in-depth investigation and multi-step reasoning. Note: The maximum length of the input is 40,000 characters.
- `research_effort` (enum, optional, default: standard) — Controls how much time and effort the Research API spends on your question. Higher effort levels run more searches and dig deeper into sources, at the cost of a longer response time. Available levels: - `lite`: Returns answers quickly. Good for straightforward questions that just need a fast, reliable answer. - `standard`: The default. Balances speed and depth, a good fit for most questions. - `deep`: Spends more time researching and cross-referencing sources. Use this when accuracy and thoroughness matter more than speed. - `exhaustive`: The most thorough option. Explores the topic as fully as possible, best suited for complex research tasks where you want the highest quality result. - `frontier`: Designed for long-running, deep research tasks that require the maximum compute budget. Latency ranges from 30s to 12000s (p50: 300s). Requires `background: true` — synchronous requests with `research_effort: "frontier"` return `422`.
  - Allowed values: `lite`, `standard`, `deep`, `exhaustive`, `frontier`
- `source_control` (object, optional) — Beta. Controls which web sources the research agent searches and visits. Use this to allow specific domains, block specific domains, boost specific domains, filter by recency, or focus web results by country. `include_domains` and `exclude_domains` cannot be used together in the same request. Each domain list is capped at 500 entries. `exclude_domains` also blocks the research agent from visiting pages on those domains during browsing. `boost_domains` gives matching domains a relative ranking boost without filtering out other domains. It can be combined with `exclude_domains` but cannot be combined with `include_domains` (returns `422`).
  - `include_domains` (list of string, optional) — A list of domains to restrict search results to. Only results from these domains will be returned. Supports up to 500 domains. This is a strict allowlist, not a boost — results are limited exclusively to the specified domains. Cannot be combined with `exclude_domains`; passing both will return a `422` error.
  - `exclude_domains` (list of string, optional) — A list of domains to exclude from search results. Results from these domains will be filtered out. Supports up to 500 domains. Cannot be combined with `include_domains`; passing both will return a `422` error.
  - `boost_domains` (list of string, optional) — A list of domains to boost in search ranking. Matching results from these domains receive a fixed relative ranking boost, but this is not a filter. If the boosted domains do not have matching results, results from other domains can still appear. Supports up to 500 domains. Boosted domains are not guaranteed to appear in the final answer — the research agent may still select other sources if they are a better fit for the response. Can be combined with `exclude_domains`. Cannot be combined with `include_domains`. Passing both `boost_domains` and `include_domains` will return a `422` error.
  - `freshness` (enum or string, optional) — Specifies the freshness of the results to return. Provide either one of `day`, `week`, `month`, `year`, or a date range string in the format `YYYY-MM-DDtoYYYY-MM-DD`. When your search query includes a temporal keyword and you also set a freshness parameter, the search will use the broader (i.e., less restrictive) of the two timeframes. For example, if you use `query=news+this+week&freshness=month`, the results will use a freshness of month.
  - `country` (enum, optional) — The country code that determines the geographical focus of the web results.
    - Allowed values: `AR`, `AU`, `AT`, `BE`, `BR`, `CA`, `CL`, `DK`, `FI`, `FR`, `DE`, `HK`, `IN`, `ID`, `IT`, `JP`, `KR`, `MY`, `MX`, `NL`, `NZ`, `NO`, `CN`, `PL`, `PT`, `PH`, `RU`, `SA`, `ZA`, `ES`, `SE`, `CH`, `TW`, `TR`, `GB`, `US`
- `output_schema` (map from string to any, optional) — Beta. Requests structured JSON output in `output.content` using a supported JSON Schema subset. Supported with `research_effort` values `standard`, `deep`, `exhaustive`, and `frontier`. Sending `output_schema` with `research_effort: "lite"` returns `422`. Limits are enforced before model execution. The request fails with `422` if any limit is exceeded: * Max nesting depth: 5. - Max total properties: 100. - Max total enum values: 500. - Max large-enum string budget (enums over 250 values): 7,500. - Max total schema string budget: 25,000. The schema string budget counts property names, `$defs` names, enum values, and `const` values. Schema rules: * Root must be a JSON object. Top-level `anyOf` is not allowed. - Every object must define `properties` and set `additionalProperties: false`. - Every property must be listed in `required`. To make a field optional, keep it in `required` and add `"null"` to its type, for example `["string", "null"]`. - Recursive schemas are not supported. - A property's type may not be a bare `{"type": "null"}`. Use a nullable array form such as `["string", "null"]`, or a `null` branch inside an `anyOf`. See [Structured Output](/docs/guides/research#structured-output) for full rules, supported patterns, the optional-via-nullable pattern, conditional structure, and examples.
- `background` (boolean, optional, default: false) — When `true`, runs the request asynchronously as a background task. The API returns a task handle immediately instead of waiting for the final answer. Poll `GET /v1/research/{task_id}` or stream progress via `GET /v1/research/{task_id}/stream` to retrieve the result. Useful for `deep` or `exhaustive` research that can exceed client-side timeouts, or when you want to decouple submission from retrieval. Required for `research_effort: "frontier"`.

## Response

### 200

In synchronous mode (`background: false`, the default), a JSON object containing a comprehensive answer with citations and supporting search results. In background mode (`background: true`), a JSON object with a task handle that you can poll or stream for the final result.

- `object or object`
  - ResearchOutput
    - `output` (object, required) — An object containing the content, content type, and source list.
      - `content` (string or map from string to any, required) — The comprehensive response with inline citations. By default, content is a Markdown string with numbered citations that reference the items in the sources array. When `output_schema` is provided, content is a JSON object that conforms to the requested schema.
      - `content_type` (enum, required) — The format of the content field.
        - Allowed values: `text`, `object`
      - `sources` (list of object, required) — A list of web sources used to generate the answer.
        - `url` (string, required) — The URL of the source webpage.
        - `title` (string, optional) — The title of the source webpage.
        - `snippets` (list of string, optional) — Relevant excerpts from the source page that were used in generating the answer.
    - `warnings` (list of string, required) — A list of warnings generated during research, such as source access issues or partial results. Empty when no warnings occurred.
  - ResearchTask
    - `task_id` (string, required) — Unique identifier for the background research task.
    - `type` (enum, required) — The task type.
      - Allowed values: `research`
    - `status` (enum, required) — The status of a background research task.
      - Allowed values: `queued`, `running`, `completed`, `failed`, `cancelled`
    - `stream_url` (string, required) — The URL path for the Server-Sent Events stream for this task.
    - `created_at` (datetime, required) — When the task was created, in RFC 3339 format.

## Examples

### Basic example

**Request**

```json
{
  "input": "Which global cities improved air quality the most over the past 10 years, and what measurable actions contributed?",
  "research_effort": "lite"
}
```

**Response**

```json
{
  "output": {
    "content": "Over the past decade, some global cities have shown improvements in air quality due to specific actions. Beijing, for example, made significant strides in improving its air quality through coordinated control measures with surrounding areas, collaborative planning, unified standards, joint emergency responses, and information sharing [[1]]. These efforts, including a five-year action plan for air pollution prevention and control, have helped to substantially improve air quality in the Jing-Jin-Ji region [[2]].\n\nParis has also seen improvements, with a 50% reduction in Nitrogen dioxide pollution and a 55% decrease in particulate matter citywide since 2005. This was achieved through its climate strategy, which included adding more bike lanes and increasing cycling networks [[3]]. Wellington, New Zealand, improved air quality in one of its busiest districts by increasing the percentage of electric buses from 5% to over 50% between 2022 and 2023, leading to a 50% reduction in black carbon and a 29% drop in nitrogen dioxide levels [[3]]. Mexico City, once known as the world's most polluted city in the early 1990s, has vastly improved its air quality, with the daily concentration of SO2 declining significantly by 2018 [[2]].\n\nWhile many cities globally have experienced persistently high or even rising levels of air pollution, especially concerning PM2.5 concentrations, NO2 exposures have shown an encouraging trend, with 211 more cities meeting the WHO guideline in 2019 compared to 2010 [[4]]. Local policies have been instrumental in these improvements [[4]].",
    "content_type": "text",
    "sources": [
      {
        "snippets": [
          "However, Beijing has made remarkable strides in recent years to improve its air quality, setting an example for other cities grappling with similar challenges. The root causes Comparing the past 20 years of its development to the 20 before, Beijing's GDP, population, and vehicles sharply increased by 1078%, 74%, and 335% respectively (UNEP, 2019).",
          "The city actively coordinated air pollution control measures with surrounding areas, such as the Beijing-Tianjin-Hebei region. Collaborative planning, unified standards, joint emergency responses, and information sharing significantly improved the air quality in this broader region.",
          "While Beijing has made significant strides, challenges remain. The average PM2.5 level is still six times higher than the World Health Organization's (WHO) guideline, and the 2021-22 improvement may be partially attributed to measures taken for the Winter Olympics.",
          "As China emerged as the world's largest automobile producer and consumer, it grappled with the detrimental impacts of increased oil consumption. Furthermore, the high level of coal consumption, especially during the winter heating season, contributed to the city's deteriorating air quality, reaching an average of 101.56 micrograms of PM2.5 particles per cubic meter in 2013 (Statista, 2023)."
        ],
        "title": "Clearing the skies: how Beijing tackled air pollution & what lies ...",
        "url": "https://sustainablemobility.iclei.org/air-pollution-beijing/"
      },
      {
        "snippets": [
          "The latest World Bank report, Clearing the Air: A Tale of Three Cities, chose Beijing, New Delhi and Mexico City to assess how current and past efforts improved air quality. In the early 1990s, Mexico City was known as the world's most polluted city and while there are still challenges, air quality has vastly improved. Daily concentration of SO2 – a contributor to PM2.5 concentrations – declined from 300 µg/m3 in the 1990s to less than 100 µg/m3 in 2018.",
          "In China, the ministries of Environmental Protection (now the Ministry of Ecology and Environment), Industry and Information Technology, Finance, Housing and Rural Development, along with the National Development and Reform Commission and National Energy Administration, worked together to issue a five-year action plan for air pollution prevention and control for the entire Jing-Jin-Ji region that surrounds Beijing and includes the municipality of Beijing, municipality of Tianjin, the province of Hebei, and small parts of Henan, Shanxi, inner Mongolia, and Shandong. What's encouraging about this new work is that it shows that with the right policies, incentives and information, air quality can be improved substantially, particularly as countries work to grow back cleaner after the pandemic.",
          "Failure to provide such incentives in India in the late 1990s resulted in the government developing plans but not implementing them. This led to India's Supreme Court stepping in to force the government to implement policy measures. A recent government of India program to provide performance-based grants to cities to reward improvements in air quality is a step in the right direction.",
          "The cost associated with health impacts of outdoor PM2.5 air pollution is estimated to be US$5.7 trillion, equivalent to 4.8 percent of global GDP, according to World Bank research. The COVID-19 pandemic further highlights why addressing air pollution is so important, with early research pointing to links between air pollution, illness and death due to the virus. On the flip side, the economic lockdowns caused by the pandemic, while devastating for communities, did result in some noticeable improvements in air quality but these improvements were inconsistent, particularly when it came to PM2.5."
        ],
        "title": "Tackling poor air quality: Lessons from three cities",
        "url": "https://blogs.worldbank.org/en/voices/tackling-poor-air-quality-lessons-three-cities"
      },
      {
        "snippets": [
          "Comprehensive cycling networks improve air quality while also transforming urban mobility. Paris has added more bike lanes to its cityscape in recent years. Between 2022 and 2023 alone, bike path usage doubled during rush hour and cyclists now outnumber cars on many of the city's streets. The results of Paris' growing cycling network are promising. Alongside other elements of Paris's climate strategy, cycling has contributed to a 50% reduction in Nitrogen dioxide pollution and 55% decrease in particulate matter citywide since 2005.",
          "In 2025, the alliance and members of the Global New Mobility Coalition will launch a new workstream on Transport and Urbanism that aims to speed up cross-sector collaboration on implementing proven mobility options to improve air quality and drive sustainable growth.",
          "Air pollution has been estimated to cause 4.2 million premature deaths worldwide per year, according to the World Health Organization, and nearly half of urban airborne contamination comes from city transport. While vehicles are essential to the vitality of cities, without the right policies in place, transport will continue to be a major contributor to harmful air pollution.",
          "In Wellington, New Zealand, the percentage of electric buses travelling across the city's heavily trafficked Golden Mile corridor rose from 5% to over 50% between 2022 and 2023. This shift led to a 50% reduction in black carbon and a 29% drop in nitrogen dioxide levels throughout the district. This has significantly improved air quality in one of the busiest parts of Wellington, as well as lowering noise pollution."
        ],
        "title": "Boosting clean air strategies in cities around the world | World ...",
        "url": "https://www.weforum.org/stories/2025/06/urban-mobility-improving-cities-air-quality/"
      },
      {
        "snippets": [
          "Globally, NO2 exposures are heading in an encouraging direction as 211 more cities met the WHO guideline of 10 µg/m3 in 2019 compared to 2010. However, NO2 pollution is worsening in some other regions. Percentage of cities by population-weighted annual average pollutant concentration in 2010 and 2019. However, interventions targeting pollution at the local scale have successfully improved air quality in some cities.",
          "Local policies have improved air quality in some cities, while pollution has worsened in others. Overall, many cities have seen persistently high — and even rising — levels of air pollution over the past decade. PM2.5 exposures remained stagnant in many cities from 2010 to 2019.",
          "Cities are often hotspots for poor air quality. As rapid urbanization increases the number of people breathing dangerously polluted air, city-level data can help inform targeted efforts to curb urban air pollution and improve public health.",
          "Explore air quality and health data for your city using our new interactive app here. Most cities have polluted air, but the type of pollution varies from place to place. Local policies have improved air quality in some cities, while pollution has worsened in others."
        ],
        "title": "Air Pollution and Health in Cities | State of Global Air",
        "url": "https://www.stateofglobalair.org/resources/health-in-cities"
      }
    ]
  }
}
```

**SDK Code**

```python Basic example
from youdotcom import You
from youdotcom.models import ResearchEffort

you = You()

res = you.research(
    input="Which global cities improved air quality the most over the past 10 years, and what measurable actions contributed?",
    research_effort=ResearchEffort.LITE,
)

print(res.output.content)

for i, source in enumerate(res.output.sources, 1):
    print(f"[{i}] {source.title or 'Untitled'}: {source.url}")

```

```typescript Basic example
import { You } from "@youdotcom-oss/sdk";
import type { ResearchRequest } from "@youdotcom-oss/sdk/models/operations";
import { ResearchEffort } from "@youdotcom-oss/sdk/models/operations";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const request: ResearchRequest = {
  input: "Which global cities improved air quality the most over the past 10 years, and what measurable actions contributed?",
  researchEffort: ResearchEffort.Lite,
};

const result = await you.research(request);

console.log(result.output.content);

result.output.sources.forEach((s, i) => {
  console.log(`[${i + 1}] ${s.title ?? s.url}: ${s.url}`);
});

```

```javascript Basic example
import { You } from "@youdotcom-oss/sdk";
import { ResearchEffort } from "@youdotcom-oss/sdk/models/operations";

const you = new You({ apiKeyAuth: process.env.YDC_API_KEY });

const result = await you.research({
  input: "Which global cities improved air quality the most over the past 10 years, and what measurable actions contributed?",
  researchEffort: ResearchEffort.Lite,
});

console.log(result.output.content);

result.output.sources.forEach((s, i) => {
  console.log(`[${i + 1}] ${s.title ?? s.url}: ${s.url}`);
});

```

```go Basic example
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.you.com/v1/research"

	payload := strings.NewReader("{\n  \"input\": \"Which global cities improved air quality the most over the past 10 years, and what measurable actions contributed?\",\n  \"research_effort\": \"lite\"\n}")

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

```java Basic example
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://api.you.com/v1/research")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"input\": \"Which global cities improved air quality the most over the past 10 years, and what measurable actions contributed?\",\n  \"research_effort\": \"lite\"\n}")
  .asString();
```

```csharp Basic example
using RestSharp;

var client = new RestClient("https://api.you.com/v1/research");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"input\": \"Which global cities improved air quality the most over the past 10 years, and what measurable actions contributed?\",\n  \"research_effort\": \"lite\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift Basic example
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "input": "Which global cities improved air quality the most over the past 10 years, and what measurable actions contributed?",
  "research_effort": "lite"
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/research")! as URL,
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

### Source control

**Request**

```json
{
  "input": "What are the latest developments in quantum computing?",
  "research_effort": "deep",
  "source_control": {
    "include_domains": [
      "nature.com",
      "arxiv.org",
      "science.org"
    ]
  }
}
```

**Response**

```json
{
  "output": {
    "content": "Recent quantum computing developments include progress in error correction, processor scaling, and demonstrations from academic and industry labs [[1, 2]].",
    "content_type": "text",
    "sources": [
      {
        "snippets": [
          "Nature publishes peer-reviewed research across scientific disciplines."
        ],
        "title": "Nature",
        "url": "https://www.nature.com/"
      },
      {
        "snippets": [
          "arXiv hosts preprints across physics, computer science, and related fields."
        ],
        "title": "arXiv",
        "url": "https://arxiv.org/"
      }
    ]
  }
}
```

**SDK Code**

```python Source control
# Restrict the research to a curated set of trusted domains
from youdotcom import You
from youdotcom.models import ResearchEffort

with You() as you:
    res = you.research(
        input="What are the latest developments in quantum computing?",
        research_effort=ResearchEffort.DEEP,
        source_control={"include_domains": ["nature.com", "arxiv.org", "science.org"]},
    )

    print(res.output.content)

    for source in res.output.sources:
        print(f"{source.title or 'Untitled'}: {source.url}")

```

```javascript Source control
const url = 'https://api.you.com/v1/research';
const options = {
  method: 'POST',
  headers: {'X-API-Key': '<apiKey>', 'Content-Type': 'application/json'},
  body: '{"input":"What are the latest developments in quantum computing?","research_effort":"deep","source_control":{"include_domains":["nature.com","arxiv.org","science.org"]}}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go Source control
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.you.com/v1/research"

	payload := strings.NewReader("{\n  \"input\": \"What are the latest developments in quantum computing?\",\n  \"research_effort\": \"deep\",\n  \"source_control\": {\n    \"include_domains\": [\n      \"nature.com\",\n      \"arxiv.org\",\n      \"science.org\"\n    ]\n  }\n}")

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

```java Source control
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://api.you.com/v1/research")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"input\": \"What are the latest developments in quantum computing?\",\n  \"research_effort\": \"deep\",\n  \"source_control\": {\n    \"include_domains\": [\n      \"nature.com\",\n      \"arxiv.org\",\n      \"science.org\"\n    ]\n  }\n}")
  .asString();
```

```csharp Source control
using RestSharp;

var client = new RestClient("https://api.you.com/v1/research");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"input\": \"What are the latest developments in quantum computing?\",\n  \"research_effort\": \"deep\",\n  \"source_control\": {\n    \"include_domains\": [\n      \"nature.com\",\n      \"arxiv.org\",\n      \"science.org\"\n    ]\n  }\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift Source control
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "input": "What are the latest developments in quantum computing?",
  "research_effort": "deep",
  "source_control": ["include_domains": ["nature.com", "arxiv.org", "science.org"]]
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/research")! as URL,
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

### Structured output

**Request**

```json
{
  "input": "What are the FDA-approved GLP-1 receptor agonists and their indications?",
  "research_effort": "standard",
  "source_control": {
    "include_domains": [
      "fda.gov",
      "nih.gov",
      "pubmed.ncbi.nlm.nih.gov"
    ],
    "freshness": "year"
  },
  "output_schema": {
    "additionalProperties": false,
    "properties": {
      "drugs": {
        "items": {
          "additionalProperties": false,
          "properties": {
            "approval_year": {
              "type": "string"
            },
            "approved_indications": {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            "brand_name": {
              "type": "string"
            },
            "generic_name": {
              "type": "string"
            },
            "manufacturer": {
              "type": "string"
            }
          },
          "required": [
            "brand_name",
            "generic_name",
            "manufacturer",
            "approved_indications",
            "approval_year"
          ],
          "type": "object"
        },
        "type": "array"
      },
      "summary": {
        "type": "string"
      }
    },
    "required": [
      "drugs",
      "summary"
    ],
    "type": "object"
  }
}
```

**Response**

```json
{
  "output": {
    "content": {
      "drugs": [
        {
          "approval_year": "2005",
          "approved_indications": [
            "Type 2 diabetes mellitus as an adjunct to diet and exercise"
          ],
          "brand_name": "Byetta",
          "generic_name": "exenatide",
          "manufacturer": "Amylin and Eli Lilly"
        },
        {
          "approval_year": "2010",
          "approved_indications": [
            "Type 2 diabetes mellitus as an adjunct to diet and exercise"
          ],
          "brand_name": "Victoza",
          "generic_name": "liraglutide",
          "manufacturer": "Novo Nordisk"
        },
        {
          "approval_year": "2014",
          "approved_indications": [
            "Chronic weight management in adults with obesity or overweight with at least one weight-related condition, as an adjunct to a reduced-calorie diet and increased physical activity"
          ],
          "brand_name": "Saxenda",
          "generic_name": "liraglutide",
          "manufacturer": "Novo Nordisk"
        },
        {
          "approval_year": "2017",
          "approved_indications": [
            "Type 2 diabetes mellitus as an adjunct to diet and exercise",
            "To reduce the risk of major adverse cardiovascular events in adults with type 2 diabetes mellitus and established cardiovascular disease"
          ],
          "brand_name": "Ozempic",
          "generic_name": "semaglutide",
          "manufacturer": "Novo Nordisk"
        },
        {
          "approval_year": "2019",
          "approved_indications": [
            "Type 2 diabetes mellitus as an adjunct to diet and exercise"
          ],
          "brand_name": "Rybelsus",
          "generic_name": "semaglutide",
          "manufacturer": "Novo Nordisk"
        },
        {
          "approval_year": "2021",
          "approved_indications": [
            "Chronic weight management in adults with obesity or overweight with at least one weight-related condition, as an adjunct to a reduced-calorie diet and increased physical activity",
            "Chronic weight management in pediatric patients aged 12 years and older with obesity",
            "To reduce the risk of major adverse cardiovascular events in adults with established cardiovascular disease and either obesity or overweight"
          ],
          "brand_name": "Wegovy",
          "generic_name": "semaglutide",
          "manufacturer": "Novo Nordisk"
        }
      ],
      "summary": "FDA-approved GLP-1 receptor agonists include exenatide, liraglutide, semaglutide, and others. In the context provided, the clearest FDA-approved products and indications are Byetta (exenatide) for type 2 diabetes; Victoza (liraglutide) for type 2 diabetes; Saxenda (liraglutide) for chronic weight management; Ozempic (semaglutide) for type 2 diabetes and cardiovascular risk reduction; Rybelsus (semaglutide) for type 2 diabetes; and Wegovy (semaglutide) for chronic weight management and related cardiovascular-risk indications."
    },
    "content_type": "object",
    "sources": [
      {
        "snippets": [
          "Glucagon-like peptide-1 receptor (GLP-1R) agonists have been receiving a tremendous amount of attention recently because of their ability to help individuals with obesity reduce their body weight substantially—up to 20 percent or more of total body weight in many cases (Campbell, 2023).\nAfter those preclinical studies in 1996, it was not until 2014 that the Food and Drug Administration (FDA) approved the first GLP-1R agonist, liraglutide, for use in treating obesity in humans. Another GLP-1R agonist, exenatide, had been approved for type 2 diabetes in 2005.\nThe result, Drucker said, is that a number of benefits of GLP-1R agonists have been well established for a number of different diseases or disorders. The most exciting to date have been the benefits for people with obesity, where tirzepatide has allowed many people to lose an unprecedented 20 percent or more of their body weight, he added, and understanding how all this works has tremendous potential for improving human health (Aronne et al., 2024; Garvey et al., 2016; Jastreboff et al., 2022; Wadden et al., 2023).\nHow many are weight loss dependent? One recent cardiovascular outcome trial with the GLP-1R agonist semaglutide has indicated, for example, that at least some of the benefits may not be strictly dependent on weight loss (Lincoff et al., 2023; Ryan et al., 2024).\nBut today, a decade after FDA approval of liraglutide to treat obesity, there are many highly effective GLP-1R agonists available for clinical use, and dozens of these medicines are in clinical trials. “If you feel like you missed the last 30 years and you’re getting into this late, we’re really only just starting a new era of GLP-1 medicines in the clinic,” Drucker said, adding that there are still opportunities for additional investigation."
        ],
        "title": "Introduction and Background - Examining Glucagon-Like Peptide-1 ...",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK615014/"
      },
      {
        "snippets": [
          "Liraglutide is not considered a first-line therapy for the treatment of type-2 diabetes. Guidelines from the ADA/European Association for the Study of Diabetes (EASD) and AACE guidelines were published before the FDA’s approval of liraglutide. In the 2009 ADA/EASD consensus statement, the GLP-1 agonist exenatide is considered a tier 2 therapy in combination with the use of metformin and lifestyle modifications.\nLiraglutide (Victoza) is the second agent in the incretin mimetic class of drugs approved for patients with type-2 diabetes and is the first incretin mimetic with a pharmacokinetic profile for once-daily administration.\nThus, product development has focused primarily on GLP-1 for type-2 diabetes. The incretin mimetic liraglutide (Victoza, Novo Nordisk) was approved in the U.S.\n9.Amylin and Lilly announce FDA approval of Byetta (Exenatide) injection, April 29, 2005. Available at: www2.prnewswire.com."
        ],
        "title": "Liraglutide (Victoza): The First Once-Daily Incretin Mimetic ...",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2957743/"
      },
      {
        "snippets": [
          "FDA approved Victoza (liraglutide) as an adjunct to diet and exercise to improve glycemic control in adults with type 2 diabetes mellitus. Victoza is not recommended as first-line therapy for patients who have inadequate glycemic control on diet and exercise.\nQuestions and Answers - Safety Requirements for Victoza (liraglutide)\nLiraglutide (marketed as Victoza) Information"
        ],
        "title": "Liraglutide (marketed as Victoza) Information | FDA",
        "url": "https://www.fda.gov/drugs/postmarket-drug-safety-information-patients-and-providers/liraglutide-marketed-victoza-information"
      },
      {
        "snippets": [
          "A. FDA is approving Victoza (liraglutide), a once-daily injection to treat type 2 diabetes mellitus (T2DM) in adults. Victoza is intended to help lower blood sugar (glucose) levels, along with diet and exercise.\nAnimal data that showed a rare type of thyroid cancer known as medullary thyroid cancer associated with liraglutide, although the relevance of this finding to humans remains unknown (see Q5). To ensure that the benefits of Victoza continue to outweigh any risks, FDA has required a Risk Evaluation and Mitigation Strategy (REMS) as part of the Victoza approval.\nQ5. What information did FDA review about medullary thyroid cancer and Victoza? A. Studies were done in mice and in rats to look for any evidence that liraglutide might cause cancer in animals. Results of the studies showed that liraglutide caused malignant tumors of the thyroid gland, especially at doses that were 8-times higher than what humans would receive.\nThis specific type of thyroid cancer is very rare in humans (about 600 cases per year in the United States) so even if liraglutide increased the risk for a patient to develop it, cases still might not be detected during the clinical trials. As a result of the animal study results, the clinical development program for Victoza included blood tests for a biomarker for medullary thyroid cancer—a blood calcitonin test.\nQ2. Should healthcare professionals be aware of any safety issues associated with Victoza? A. FDA approved Victoza because the Agency believes that the benefits of this drug to patients with T2DM outweigh potential risks associated with its use. There were, however, several safety concerns identified during the Victoza review that had to be evaluated in light of its benefits."
        ],
        "title": "Questions and Answers - Safety Requirements for Victoza (liraglutide) ...",
        "url": "https://www.fda.gov/drugs/postmarket-drug-safety-information-patients-and-providers/questions-and-answers-safety-requirements-victoza-liraglutide"
      },
      {
        "snippets": [
          "FDA approves Wegovy (semaglutide) injection for chronic weight management in adults with obesity or overweight with at least one weight-related condition.\nToday, the U.S. Food and Drug Administration approved Wegovy (semaglutide) injection (2.4 mg once weekly) for chronic weight management in adults with obesity or overweight with at least one weight-related condition (such as high blood pressure, type 2 diabetes, or high cholesterol), for use in addition to a reduced calorie diet and increased physical activity.\nLosing 5% to 10% of body weight through diet and exercise has been associated with a reduced risk of cardiovascular disease in adult patients with obesity or overweight. Wegovy works by mimicking a hormone called glucagon-like peptide-1 (GLP-1) that targets areas of the brain that regulate appetite and food intake. The medication dose must be increased gradually over 16 to 20 weeks to 2.4 mg once weekly to reduce gastrointestinal side effects. Wegovy should not be used in combination with other semaglutide-containing products, other GLP-1 receptor agonists, or other products intended for weight loss, including prescription drugs, over-the-counter drugs, or herbal products.\nIf Wegovy is used with insulin or a substance that causes insulin secretion, patients should speak to their health care provider about potentially lowering the dose of insulin or the insulin-inducing drug to reduce the risk of low blood sugar. Healthcare providers should monitor patients with kidney disease, diabetic retinopathy and depression or suicidal behaviors or thoughts. The FDA granted the approval to Novo Nordisk. Semaglutide 1 mg injection (Ozempic) was first approved as a treatment for type 2 diabetes in 2017.\nThis under-the-skin injection is the first approved drug for chronic weight management in adults with general obesity or overweight since 2014. The drug is indicated for chronic weight management in patients with a body mass index (BMI) of 27 kg/m2 or greater who have at least one weight-related ailment or in patients with a BMI of 30 kg/m2 or greater. “Today’s approval offers adults with obesity or overweight a beneficial new treatment option to incorporate into a weight management program,” said John Sharretts, M.D., deputy director of the Division of Diabetes, Lipid Disorders, and Obesity in the FDA’s Center for Drug Evaluation and Research."
        ],
        "title": "FDA Approves New Drug Treatment for Chronic Weight Management, ...",
        "url": "https://www.fda.gov/news-events/press-announcements/fda-approves-new-drug-treatment-chronic-weight-management-first-2014?amp="
      },
      {
        "snippets": [
          "Notice of Unlawful Sale of Unapproved Drugs to United States Consumers Over the Internet\nFDA-approved semaglutide tablets marketed under the brand name Rybelsus are indicated as an adjunct to diet and exercise to improve glycemic control in adults with type 2 diabetes mellitus. FDA-approved semaglutide injection marketed under the brand name Wegovy is indicated as an adjunct to a reduced calorie diet and increased physical activity for chronic weight management in certain adult and pediatric patients.\nFDA has observed that www.24hreup.biz offers “Ozempic 0.5mg,” “Ozempic 1mg,” and “Rybelsus Semaglutide 14mg” for sale without a prescription. Because these drugs are prescription drugs intended for conditions that are not amenable to self-diagnosis and treatment by a layperson, adequate directions cannot be written such that a layperson can use the products safely for their intended use. Consequently, the labeling for these drugs fails to bear adequate directions for use, causing them to be misbranded under section 502(f)(1) of the FD&C Act.\nAs discussed below, FDA has observed that www.24hreup.biz introduces into interstate commerce unapproved and misbranded semaglutide drug products. There are inherent risks to consumers who purchase unapproved and misbranded drug products. Unapproved new drugs do not carry the same assurances of safety and effectiveness as those drugs subject to FDA oversight.\nFurthermore, under U.S. law, prescription drugs can be dispensed only pursuant to a prescription from a healthcare practitioner licensed by law to administer prescription drugs. By offering “Ozempic 0.5mg,” “Ozempic 1mg,” and “Rybelsus Semaglutide 14mg” without requiring a prescription, www.24hreup.biz jeopardizes patient safety and misbrands the drugs under section 503(b)(1) of the FD&C Act."
        ],
        "title": "www.24hreup.biz - 700358 - 04/23/2025 | FDA",
        "url": "https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/www24hreupbiz-700358-04232025"
      },
      {
        "snippets": [
          "Attention: Jigisha Varia · Director, Regulatory Affairs\nfor Rybelsus (semaglutide) tablets. These Prior Approval sNDAs provide for: S-024: • Addition of the new indication, “to reduce the risk of major adverse · cardiovascular events (cardiovascular death, non-fatal myocardial infarction or · non-fatal stroke) in adults with type 2 diabetes mellitus who are at high risk for ·\nThe SPL will be accessible from publicly available labeling repositories.\nAlso within 14 days, amend all pending supplemental applications that include labeling\naction letter, with the content of labeling [21 CFR 314.50(l)(1)(i)] in Microsoft Word"
        ],
        "title": "Rybelsus (semaglutide) tablets - accessdata.fda.gov",
        "url": "https://www.accessdata.fda.gov/drugsatfda_docs/appletter/2025/213051Orig1s024,s028,s029ltr.pdf"
      },
      {
        "snippets": [
          "Coverage and Prior Authorization Policies for Semaglutide and Tirzepatide in Medicare Part D Plans\nFor instance, injectable semaglutide was approved for type 2 diabetes on December 5, 2017, and for cardiovascular risk reduction on January 16, 2020; however, it did not appear on any plan formulary in our data until 2021 quarter (Q)2. Similarly, oral semaglutide, approved on September 20, 2019, was not observed in coverage data until 2021 Q2. In contrast, injectable tirzepatide, approved on May 13, 2022, first appeared in our dataset by 2022 Q3. These discrepancies reflect the lag between FDA approval and formulary adoption, rather than inconsistencies in regulatory timelines. MAPD, indicates Medicare Advantage Prescription Drug; PDPs, prescription drug plans; Q, quarter.\nFor instance, injectable semaglutide was approved for type 2 diabetes on December 5, 2017, and for cardiovascular risk reduction on January 16, 2020; however, it did not appear on any plan formulary in our data until 2021 quarter (Q)2. Similarly, oral semaglutide, approved on September 20, 2019, was not observed in coverage data until 2021 Q2. In contrast, injectable tirzepatide, approved on May 13, 2022, first appeared in our dataset by 2022 Q3. These discrepancies reflect the lag between FDA approval and formulary adoption, rather than inconsistencies in regulatory timelines. MAPD indicates Medicare Advantage Prescription Drug; PDPs, prescription drug plans; Q, quarter.\nSemaglutide eligibility across all current indications for US adults. JAMA Cardiol. 2025;10(1):96-98. doi: 10.1001/jamacardio.2024.4657 - DOI - PMC - PubMed · KFF. Gross Medicare spending on Ozempic and other GLP-1s is already skyrocketing—even though Medicare cannot cover the drugs for weight loss.\nThis cross-sectional study examines trends in coverage of glucagon-like peptide-1 receptor agonists, semaglutide and tirzepatide, and prior authorization requirements among Medicare Part D beneficiaries."
        ],
        "title": "Coverage and Prior Authorization Policies for Semaglutide and ...",
        "url": "https://pubmed.ncbi.nlm.nih.gov/40880091/"
      }
    ]
  }
}
```

**SDK Code**

```python Structured output
# Force a typed JSON response that matches a JSON Schema subset
from youdotcom import You
from youdotcom.models import ResearchEffort

GLUCAGON_SCHEMA = {
    "type": "object",
    "properties": {
        "drugs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "brand_name": {"type": "string"},
                    "generic_name": {"type": "string"},
                    "manufacturer": {"type": "string"},
                    "approved_indications": {"type": "array", "items": {"type": "string"}},
                    "approval_year": {"type": "string"},
                },
                "required": [
                    "brand_name",
                    "generic_name",
                    "manufacturer",
                    "approved_indications",
                    "approval_year",
                ],
                "additionalProperties": False,
            },
        },
        "summary": {"type": "string"},
    },
    "required": ["drugs", "summary"],
    "additionalProperties": False,
}

with You() as you:
    res = you.research(
        input="What are the FDA-approved GLP-1 receptor agonists and their indications?",
        research_effort=ResearchEffort.STANDARD,
        source_control={
            "include_domains": ["fda.gov", "nih.gov", "pubmed.ncbi.nlm.nih.gov"],
            "freshness": "year",
        },
        output_schema=GLUCAGON_SCHEMA,
    )

    payload = res.output.content
    print(f"{len(payload['drugs'])} drugs")
    print(payload["summary"])

```

```javascript Structured output
const url = 'https://api.you.com/v1/research';
const options = {
  method: 'POST',
  headers: {'X-API-Key': '<apiKey>', 'Content-Type': 'application/json'},
  body: '{"input":"What are the FDA-approved GLP-1 receptor agonists and their indications?","research_effort":"standard","source_control":{"include_domains":["fda.gov","nih.gov","pubmed.ncbi.nlm.nih.gov"],"freshness":"year"},"output_schema":{"additionalProperties":false,"properties":{"drugs":{"items":{"additionalProperties":false,"properties":{"approval_year":{"type":"string"},"approved_indications":{"items":{"type":"string"},"type":"array"},"brand_name":{"type":"string"},"generic_name":{"type":"string"},"manufacturer":{"type":"string"}},"required":["brand_name","generic_name","manufacturer","approved_indications","approval_year"],"type":"object"},"type":"array"},"summary":{"type":"string"}},"required":["drugs","summary"],"type":"object"}}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go Structured output
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.you.com/v1/research"

	payload := strings.NewReader("{\n  \"input\": \"What are the FDA-approved GLP-1 receptor agonists and their indications?\",\n  \"research_effort\": \"standard\",\n  \"source_control\": {\n    \"include_domains\": [\n      \"fda.gov\",\n      \"nih.gov\",\n      \"pubmed.ncbi.nlm.nih.gov\"\n    ],\n    \"freshness\": \"year\"\n  },\n  \"output_schema\": {\n    \"additionalProperties\": false,\n    \"properties\": {\n      \"drugs\": {\n        \"items\": {\n          \"additionalProperties\": false,\n          \"properties\": {\n            \"approval_year\": {\n              \"type\": \"string\"\n            },\n            \"approved_indications\": {\n              \"items\": {\n                \"type\": \"string\"\n              },\n              \"type\": \"array\"\n            },\n            \"brand_name\": {\n              \"type\": \"string\"\n            },\n            \"generic_name\": {\n              \"type\": \"string\"\n            },\n            \"manufacturer\": {\n              \"type\": \"string\"\n            }\n          },\n          \"required\": [\n            \"brand_name\",\n            \"generic_name\",\n            \"manufacturer\",\n            \"approved_indications\",\n            \"approval_year\"\n          ],\n          \"type\": \"object\"\n        },\n        \"type\": \"array\"\n      },\n      \"summary\": {\n        \"type\": \"string\"\n      }\n    },\n    \"required\": [\n      \"drugs\",\n      \"summary\"\n    ],\n    \"type\": \"object\"\n  }\n}")

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

```java Structured output
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://api.you.com/v1/research")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"input\": \"What are the FDA-approved GLP-1 receptor agonists and their indications?\",\n  \"research_effort\": \"standard\",\n  \"source_control\": {\n    \"include_domains\": [\n      \"fda.gov\",\n      \"nih.gov\",\n      \"pubmed.ncbi.nlm.nih.gov\"\n    ],\n    \"freshness\": \"year\"\n  },\n  \"output_schema\": {\n    \"additionalProperties\": false,\n    \"properties\": {\n      \"drugs\": {\n        \"items\": {\n          \"additionalProperties\": false,\n          \"properties\": {\n            \"approval_year\": {\n              \"type\": \"string\"\n            },\n            \"approved_indications\": {\n              \"items\": {\n                \"type\": \"string\"\n              },\n              \"type\": \"array\"\n            },\n            \"brand_name\": {\n              \"type\": \"string\"\n            },\n            \"generic_name\": {\n              \"type\": \"string\"\n            },\n            \"manufacturer\": {\n              \"type\": \"string\"\n            }\n          },\n          \"required\": [\n            \"brand_name\",\n            \"generic_name\",\n            \"manufacturer\",\n            \"approved_indications\",\n            \"approval_year\"\n          ],\n          \"type\": \"object\"\n        },\n        \"type\": \"array\"\n      },\n      \"summary\": {\n        \"type\": \"string\"\n      }\n    },\n    \"required\": [\n      \"drugs\",\n      \"summary\"\n    ],\n    \"type\": \"object\"\n  }\n}")
  .asString();
```

```csharp Structured output
using RestSharp;

var client = new RestClient("https://api.you.com/v1/research");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"input\": \"What are the FDA-approved GLP-1 receptor agonists and their indications?\",\n  \"research_effort\": \"standard\",\n  \"source_control\": {\n    \"include_domains\": [\n      \"fda.gov\",\n      \"nih.gov\",\n      \"pubmed.ncbi.nlm.nih.gov\"\n    ],\n    \"freshness\": \"year\"\n  },\n  \"output_schema\": {\n    \"additionalProperties\": false,\n    \"properties\": {\n      \"drugs\": {\n        \"items\": {\n          \"additionalProperties\": false,\n          \"properties\": {\n            \"approval_year\": {\n              \"type\": \"string\"\n            },\n            \"approved_indications\": {\n              \"items\": {\n                \"type\": \"string\"\n              },\n              \"type\": \"array\"\n            },\n            \"brand_name\": {\n              \"type\": \"string\"\n            },\n            \"generic_name\": {\n              \"type\": \"string\"\n            },\n            \"manufacturer\": {\n              \"type\": \"string\"\n            }\n          },\n          \"required\": [\n            \"brand_name\",\n            \"generic_name\",\n            \"manufacturer\",\n            \"approved_indications\",\n            \"approval_year\"\n          ],\n          \"type\": \"object\"\n        },\n        \"type\": \"array\"\n      },\n      \"summary\": {\n        \"type\": \"string\"\n      }\n    },\n    \"required\": [\n      \"drugs\",\n      \"summary\"\n    ],\n    \"type\": \"object\"\n  }\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift Structured output
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "input": "What are the FDA-approved GLP-1 receptor agonists and their indications?",
  "research_effort": "standard",
  "source_control": [
    "include_domains": ["fda.gov", "nih.gov", "pubmed.ncbi.nlm.nih.gov"],
    "freshness": "year"
  ],
  "output_schema": [
    "additionalProperties": false,
    "properties": [
      "drugs": [
        "items": [
          "additionalProperties": false,
          "properties": [
            "approval_year": ["type": "string"],
            "approved_indications": [
              "items": ["type": "string"],
              "type": "array"
            ],
            "brand_name": ["type": "string"],
            "generic_name": ["type": "string"],
            "manufacturer": ["type": "string"]
          ],
          "required": ["brand_name", "generic_name", "manufacturer", "approved_indications", "approval_year"],
          "type": "object"
        ],
        "type": "array"
      ],
      "summary": ["type": "string"]
    ],
    "required": ["drugs", "summary"],
    "type": "object"
  ]
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/research")! as URL,
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

### Background mode (frontier)

**Request**

```json
{
  "input": "Compare 'Acme Logistics LLC' (DE) and 'Acme Logistics' (NJ). Are they the same business?",
  "research_effort": "frontier",
  "output_schema": {
    "additionalProperties": false,
    "properties": {
      "confidence": {
        "type": "number"
      },
      "evidence": {
        "items": {
          "type": "string"
        },
        "type": "array"
      },
      "same_entity": {
        "type": "boolean"
      }
    },
    "required": [
      "same_entity",
      "confidence",
      "evidence"
    ],
    "type": "object"
  },
  "background": true
}
```

**Response**

```json
{
  "created_at": "2026-06-26T00:00:00Z",
  "status": "queued",
  "stream_url": "/v1/research/f1e2d3c4-0000-0000-0000-000000000000/stream",
  "task_id": "f1e2d3c4-0000-0000-0000-000000000000",
  "type": "research"
}
```

**SDK Code**

```python Background mode (frontier)
# research_and_wait() submits the background task and polls until
# it reaches a terminal status, raising on failure or timeout
from youdotcom import You
from youdotcom.models import ResearchEffort
from youdotcom.research_helpers import research_and_wait

with You() as you:
    task = research_and_wait(
        you,
        input="Compare 'Acme Logistics LLC' (DE) and 'Acme Logistics' (NJ). Are they the same business?",
        research_effort=ResearchEffort.FRONTIER,
        output_schema={
            "type": "object",
            "properties": {
                "same_entity": {"type": "boolean"},
                "confidence": {"type": "number"},
                "evidence": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["same_entity", "confidence", "evidence"],
            "additionalProperties": False,
        },
        timeout_s=600,
    )

    verdict = task.result.output["content"]
    print(f"Same entity: {verdict['same_entity']} (confidence: {verdict['confidence']})")

```

```javascript Background mode (frontier)
const url = 'https://api.you.com/v1/research';
const options = {
  method: 'POST',
  headers: {'X-API-Key': '<apiKey>', 'Content-Type': 'application/json'},
  body: '{"input":"Compare \'Acme Logistics LLC\' (DE) and \'Acme Logistics\' (NJ). Are they the same business?","research_effort":"frontier","output_schema":{"additionalProperties":false,"properties":{"confidence":{"type":"number"},"evidence":{"items":{"type":"string"},"type":"array"},"same_entity":{"type":"boolean"}},"required":["same_entity","confidence","evidence"],"type":"object"},"background":true}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go Background mode (frontier)
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.you.com/v1/research"

	payload := strings.NewReader("{\n  \"input\": \"Compare 'Acme Logistics LLC' (DE) and 'Acme Logistics' (NJ). Are they the same business?\",\n  \"research_effort\": \"frontier\",\n  \"output_schema\": {\n    \"additionalProperties\": false,\n    \"properties\": {\n      \"confidence\": {\n        \"type\": \"number\"\n      },\n      \"evidence\": {\n        \"items\": {\n          \"type\": \"string\"\n        },\n        \"type\": \"array\"\n      },\n      \"same_entity\": {\n        \"type\": \"boolean\"\n      }\n    },\n    \"required\": [\n      \"same_entity\",\n      \"confidence\",\n      \"evidence\"\n    ],\n    \"type\": \"object\"\n  },\n  \"background\": true\n}")

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

```java Background mode (frontier)
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://api.you.com/v1/research")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"input\": \"Compare 'Acme Logistics LLC' (DE) and 'Acme Logistics' (NJ). Are they the same business?\",\n  \"research_effort\": \"frontier\",\n  \"output_schema\": {\n    \"additionalProperties\": false,\n    \"properties\": {\n      \"confidence\": {\n        \"type\": \"number\"\n      },\n      \"evidence\": {\n        \"items\": {\n          \"type\": \"string\"\n        },\n        \"type\": \"array\"\n      },\n      \"same_entity\": {\n        \"type\": \"boolean\"\n      }\n    },\n    \"required\": [\n      \"same_entity\",\n      \"confidence\",\n      \"evidence\"\n    ],\n    \"type\": \"object\"\n  },\n  \"background\": true\n}")
  .asString();
```

```csharp Background mode (frontier)
using RestSharp;

var client = new RestClient("https://api.you.com/v1/research");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"input\": \"Compare 'Acme Logistics LLC' (DE) and 'Acme Logistics' (NJ). Are they the same business?\",\n  \"research_effort\": \"frontier\",\n  \"output_schema\": {\n    \"additionalProperties\": false,\n    \"properties\": {\n      \"confidence\": {\n        \"type\": \"number\"\n      },\n      \"evidence\": {\n        \"items\": {\n          \"type\": \"string\"\n        },\n        \"type\": \"array\"\n      },\n      \"same_entity\": {\n        \"type\": \"boolean\"\n      }\n    },\n    \"required\": [\n      \"same_entity\",\n      \"confidence\",\n      \"evidence\"\n    ],\n    \"type\": \"object\"\n  },\n  \"background\": true\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift Background mode (frontier)
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "input": "Compare 'Acme Logistics LLC' (DE) and 'Acme Logistics' (NJ). Are they the same business?",
  "research_effort": "frontier",
  "output_schema": [
    "additionalProperties": false,
    "properties": [
      "confidence": ["type": "number"],
      "evidence": [
        "items": ["type": "string"],
        "type": "array"
      ],
      "same_entity": ["type": "boolean"]
    ],
    "required": ["same_entity", "confidence", "evidence"],
    "type": "object"
  ],
  "background": true
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/research")! as URL,
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