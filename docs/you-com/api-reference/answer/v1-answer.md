> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Answer

POST https://api.you.com/v1/answer
Content-Type: application/json

Returns a synthesized natural-language answer with citations and the web results used to generate it. Provide a `query` and optional freshness, locale, domain, and explicit-content controls.

Reference: https://you.com/docs/api-reference/answer/v1-answer

## Authentication

- `X-API-Key` header (required) — The unique API Key required to authorize API access. Learn how to get yours in the ["Get your API key" section of the documentation](https://you.com/docs/quickstart#get-your-api-key).

## Request

### Body (application/json)

- `query` (string, required) — The search query used to retrieve relevant web results.
- `freshness` (enum or string, optional) — Specifies the freshness of the results to return. Provide either one of `day`, `week`, `month`, `year`, or a date range string in the format `YYYY-MM-DDtoYYYY-MM-DD`. When your search query includes a temporal keyword and you also set a freshness parameter, the search will use the broader timeframe. For example, if you use `query=news+this+week&freshness=month`, the results will use a freshness of month.
- `country` (enum, optional) — A supported country code that determines the geographical focus of the web results.
  - Allowed values: `AR`, `AU`, `AT`, `BE`, `BR`, `CA`, `CL`, `DK`, `FI`, `FR`, `DE`, `HK`, `IN`, `ID`, `IT`, `JP`, `KR`, `MY`, `MX`, `NL`, `NZ`, `NO`, `CN`, `PL`, `PT`, `PH`, `RU`, `SA`, `ZA`, `ES`, `SE`, `CH`, `TW`, `TR`, `GB`, `US`
- `language` (enum, optional) — A supported BCP 47 language tag that determines the language of the web results.
  - Allowed values: `AR`, `EU`, `BN`, `BG`, `CA`, `HR`, `CS`, `DA`, `NL`, `EN`, `EN-GB`, `ET`, `FI`, `FR`, `GL`, `DE`, `EL`, `GU`, `HE`, `HI`, `HU`, `IS`, `IT`, `KN`, `KO`, `LV`, `LT`, `MS`, `ML`, `MR`, `NB`, `PL`, `PA`, `RO`, `RU`, `SR`, `SK`, `SL`, `ES`, `SV`, `TA`, `TE`, `TH`, `TR`, `UK`, `VI`
- `safesearch` (enum, optional, default: moderate) — Configures the safesearch filter for content moderation. This allows you to decide whether to return NSFW content or not.
  - Allowed values: `off`, `moderate`, `strict`
- `include_domains` (list of string, optional) — Domains to exclusively include in web results. This is a strict allowlist, not a ranking boost. Supports up to 500 domains. Cannot be combined with `exclude_domains` or `boost_domains`.
- `exclude_domains` (list of string, optional) — Domains to exclude from web results. Supports up to 500 domains. Cannot be combined with `include_domains`. Can be combined with `boost_domains`.
- `boost_domains` (list of string, optional) — Domains to prefer in search ranking without excluding results from other domains. Supports up to 500 domains. Can be combined with `exclude_domains`, but not with `include_domains`.

## Response

### 200

A JSON object containing a synthesized answer with citations and supporting search results

- `answer` (string, required) — The synthesized response with numbered inline citations that reference items in the `citations` array.
- `citations` (list of object, required) — The sources cited in the answer, in citation order. Each item includes the source URL and verbatim excerpts that support the answer.
  - `source` (string, required) — The URL of the cited source.
  - `excerpts` (list of string, required) — Verbatim excerpts from the cited source that support the answer.
- `results` (object, required) — Search results grouped by result type. All current search results are grouped under `web`.
  - `web` (list of object, required) — All web search results considered during answer synthesis, whether cited or not.
    - `url` (string, required) — The URL of the source webpage.
    - `title` (string, required) — The title of the source webpage.
    - `snippets` (list of string, optional, default: []) — Text snippets from the search result that preview its content.
    - `description` (string, optional) — A brief description of the content of the search result.
    - `thumbnail_url` (string, optional) — URL of the thumbnail.
    - `page_age` (string, optional) — The age of the search result.

## Examples

### What causes the aurora borealis

**Request**

```json
{
  "query": "what causes the aurora borealis"
}
```

**Response**

```json
{
  "answer": "The aurora borealis is caused by charged particles ejected from the Sun—carried by the solar wind and often intensified by solar flares or coronal mass ejections—that travel to Earth, are funneled by Earth's magnetic field toward the polar regions, and collide with oxygen and nitrogen atoms in the upper atmosphere. These collisions excite the atoms, which then release photons of light, creating the visible northern lights. [[1, 2, 3]]",
  "citations": [
    {
      "source": "https://www.jpl.nasa.gov/nmp/st5/SCIENCE/aurora.html",
      "excerpts": [
        "Auroras are brilliant ribbons of light weaving across Earth's northern or southern polar regions. These natural light shows are caused by magnetic storms that have been triggered by solar activity, such as solar flares (explosions on the Sun) or coronal mass ejections (ejected gas bubbles). Energetic charged particles from these events are carried from the Sun by the solar wind.",
        "When these particles seep through Earth's magnetosphere, they cause substorms. Then fast moving particles slam into our thin, high atmosphere, colliding with Earth's oxygen and nitrogen particles. As these air particles shed the energy they picked up from the collision, each atom starts to glow in a different color."
      ]
    },
    {
      "source": "https://www.valofinland.com/what-causes-the-colours-in-aurora-borealis/",
      "excerpts": [
        "The Aurora Borealis is a result of interactions between solar wind and the Earth's atmosphere. Solar wind is a stream of charged particles released from the sun's upper atmosphere, known as the corona. When these particles reach Earth, they collide with gases in our atmosphere, such as oxygen and nitrogen. These collisions excite the gas particles, causing them to emit light."
      ]
    },
    {
      "source": "https://triplefatgoose.com/blogs/down-time/understanding-the-aurora-borealis",
      "excerpts": [
        "When electrons fly through space, two things can happen: they are reflected away by the Earth's magnetic field, or they follow it to the poles. Because the magnetic field is weaker at the poles, the electrons are able to freely enter the atmosphere without being reflected away."
      ]
    }
  ],
  "results": {
    "web": [
      {
        "url": "https://www.jpl.nasa.gov/nmp/st5/SCIENCE/aurora.html",
        "title": "How Auroras Form",
        "snippets": [
          "Auroras are brilliant ribbons of light weaving across Earth's northern or southern polar regions. These natural light shows are caused by magnetic storms that have been triggered by solar activity."
        ],
        "description": "Auroras are brilliant ribbons of light weaving across Earth's northern or southern polar regions."
      },
      {
        "url": "https://auroraqueenresort.fi/what-causes-the-northern-lights-to-appear/",
        "title": "What causes the northern lights to appear? - Aurora Queen Resort",
        "snippets": [
          "The northern lights, also known as aurora borealis, are a mesmerising natural light display that occurs when charged particles from the sun collide with gases in Earth's atmosphere."
        ],
        "description": "Discover what causes the northern lights to appear and why these mesmerizing displays illuminate Arctic skies in various colors. Learn when and where to witness this celestial phenomenon.",
        "thumbnail_url": "https://auroraqueenresort.fi/wp-content/uploads/2024/09/Aurora-Queen-Resort-1024x768.jpg",
        "page_age": "2025-06-13T04:55:47"
      },
      {
        "url": "https://triplefatgoose.com/blogs/down-time/understanding-the-aurora-borealis",
        "title": "The Aurora Borealis",
        "snippets": [
          "When millions of photons of light are emitted at the same time, it causes the sky to light up and creates the Aurora Borealis."
        ],
        "description": "Learn how charged particles from the sun produce the aurora borealis."
      }
    ]
  }
}
```

**SDK Code**

```python What causes the aurora borealis
# Use our official Python SDK to get a cited answer
from youdotcom import You

with You() as you:
    res = you.answer(query="what causes the aurora borealis")

    print(res.answer)

    # Every claim is backed by a source in the citations array
    for i, citation in enumerate(res.citations or [], 1):
        print(f"[{i}] {citation.source}")

```

```javascript What causes the aurora borealis
const url = 'https://api.you.com/v1/answer';
const options = {
  method: 'POST',
  headers: {'X-API-Key': '<apiKey>', 'Content-Type': 'application/json'},
  body: '{"query":"what causes the aurora borealis"}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go What causes the aurora borealis
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.you.com/v1/answer"

	payload := strings.NewReader("{\n  \"query\": \"what causes the aurora borealis\"\n}")

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

```java What causes the aurora borealis
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://api.you.com/v1/answer")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"query\": \"what causes the aurora borealis\"\n}")
  .asString();
```

```csharp What causes the aurora borealis
using RestSharp;

var client = new RestClient("https://api.you.com/v1/answer");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"query\": \"what causes the aurora borealis\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift What causes the aurora borealis
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = ["query": "what causes the aurora borealis"] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/answer")! as URL,
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

### Current federal funds rate with monthly freshness

**Request**

```json
{
  "query": "what is the current federal funds rate",
  "freshness": "month"
}
```

**Response**

```json
{
  "answer": "The current federal funds rate target range is 3.50% to 3.75%, with the effective overnight rate around 3.63–3.64%. [[1, 2, 3]]",
  "citations": [
    {
      "source": "https://www.usatoday.com/story/money/economy/2026/06/17/fed-rate-decision-meeting-updates--live/90569737007/",
      "excerpts": [
        "The federal funds rate, a benchmark for interest rates across the country, remains at a range of 3.5% to 3.75%, as it has so far this year and in line with forecasters' expectations for the June meeting."
      ]
    },
    {
      "source": "https://www.nerdwallet.com/banking/news/what-is-the-fed-rate",
      "excerpts": [
        "The current target range is 3.50% to 3.75%"
      ]
    },
    {
      "source": "https://www.cbsnews.com/news/fed-meeting-fomc-today-kevin-warsh-interest-rates/",
      "excerpts": [
        "The current federal funds rate target range is 3.50%-3.75%, set by the FOMC at its March 18-19, 2026 meeting."
      ]
    }
  ],
  "results": {
    "web": [
      {
        "url": "https://fred.stlouisfed.org/series/FEDFUNDS",
        "title": "Federal Funds Effective Rate (FEDFUNDS)",
        "snippets": [
          "May 2026: 3.63, Apr 2026: 3.64, Mar 2026: 3.64, Feb 2026: 3.64, Jan 2026: 3.64"
        ]
      },
      {
        "url": "https://tradingeconomics.com/united-states/interest-rate",
        "title": "United States Fed Funds Interest Rate",
        "snippets": [
          "The benchmark interest rate in the United States was last recorded at 3.75 percent."
        ]
      },
      {
        "url": "https://fred.stlouisfed.org/series/DFF",
        "title": "Federal Funds Effective Rate (DFF)",
        "snippets": [
          "2026-06-26: 3.63, 2026-06-25: 3.63, 2026-06-24: 3.63, 2026-06-23: 3.63, 2026-06-22: 3.63"
        ]
      }
    ]
  }
}
```

**SDK Code**

```python Current federal funds rate with monthly freshness
# Restrict the sources behind the answer to the last month
from youdotcom import You

with You() as you:
    res = you.answer(
        query="what is the current federal funds rate",
        freshness="month",
    )

    print(res.answer)

```

```javascript Current federal funds rate with monthly freshness
const url = 'https://api.you.com/v1/answer';
const options = {
  method: 'POST',
  headers: {'X-API-Key': '<apiKey>', 'Content-Type': 'application/json'},
  body: '{"query":"what is the current federal funds rate","freshness":"month"}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go Current federal funds rate with monthly freshness
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.you.com/v1/answer"

	payload := strings.NewReader("{\n  \"query\": \"what is the current federal funds rate\",\n  \"freshness\": \"month\"\n}")

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

```java Current federal funds rate with monthly freshness
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://api.you.com/v1/answer")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"query\": \"what is the current federal funds rate\",\n  \"freshness\": \"month\"\n}")
  .asString();
```

```csharp Current federal funds rate with monthly freshness
using RestSharp;

var client = new RestClient("https://api.you.com/v1/answer");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"query\": \"what is the current federal funds rate\",\n  \"freshness\": \"month\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift Current federal funds rate with monthly freshness
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "query": "what is the current federal funds rate",
  "freshness": "month"
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/answer")! as URL,
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

### Top local news in the UK

**Request**

```json
{
  "query": "top local news today",
  "country": "GB",
  "language": "EN",
  "boost_domains": [
    "leicestermercury.co.uk"
  ]
}
```

**Response**

```json
{
  "answer": "Today's top local news from Leicestershire Live includes a police chase on the A46 that ended in a serious collision and a stolen van crash into a BMW, a multi-vehicle crash on the M1 causing injuries, a major road closure after a serious collision, an investigation finding higher baby death rates at city hospitals, concerns over the Cultural Quarter's future, and a fresh bid to demolish a local shopping centre. Additionally, 16 Leicester City players are set to leave with two transfers already confirmed, and an Indian restaurant that survived a fire is now thriving after seven years. [[1]]",
  "citations": [
    {
      "source": "https://www.leicestermercury.co.uk/",
      "excerpts": [
        "Stolen van in police chase crashed into BMW in A46 horror crash",
        "Man charged and named after A46 police chase leads to serious collision",
        "Two men injured after serious multi-vehicle Leicestershire M1 crash",
        "16 players leaving Leicester City today as two transfers already confirmed and contract awaiting"
      ]
    }
  ],
  "results": {
    "web": [
      {
        "url": "https://www.leicestermercury.co.uk/",
        "title": "Leicestershire Live - Latest local news, sport & business from ...",
        "snippets": [
          "Man charged and named after A46 police chase leads to serious collision. Two men injured after serious multi-vehicle Leicestershire M1 crash."
        ]
      },
      {
        "url": "https://www.mylondon.news/",
        "title": "MyLondon - The latest London news, sport, entertainment and more",
        "snippets": [
          "A4 Cranford closure live as police incident closes road near Heathrow Airport. Second London heatwave timeline and how high temperatures will rise."
        ]
      },
      {
        "url": "https://www.glasgowtimes.co.uk/",
        "title": "Glasgow News, Sport, Events",
        "snippets": [
          "Protesters unveil cardboard bus at rally over transport fares and reliability. Police issue update two days after teen girl raped in Glasgow park."
        ]
      }
    ]
  }
}
```

**SDK Code**

```python Top local news in the UK
# Focus the answer on a region and language, and prefer a local source
from youdotcom import You

with You() as you:
    res = you.answer(
        query="top local news today",
        country="GB",
        language="EN",
        boost_domains=["leicestermercury.co.uk"],
    )

    print(res.answer)

```

```javascript Top local news in the UK
const url = 'https://api.you.com/v1/answer';
const options = {
  method: 'POST',
  headers: {'X-API-Key': '<apiKey>', 'Content-Type': 'application/json'},
  body: '{"query":"top local news today","country":"GB","language":"EN","boost_domains":["leicestermercury.co.uk"]}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go Top local news in the UK
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.you.com/v1/answer"

	payload := strings.NewReader("{\n  \"query\": \"top local news today\",\n  \"country\": \"GB\",\n  \"language\": \"EN\",\n  \"boost_domains\": [\n    \"leicestermercury.co.uk\"\n  ]\n}")

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

```java Top local news in the UK
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://api.you.com/v1/answer")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"query\": \"top local news today\",\n  \"country\": \"GB\",\n  \"language\": \"EN\",\n  \"boost_domains\": [\n    \"leicestermercury.co.uk\"\n  ]\n}")
  .asString();
```

```csharp Top local news in the UK
using RestSharp;

var client = new RestClient("https://api.you.com/v1/answer");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"query\": \"top local news today\",\n  \"country\": \"GB\",\n  \"language\": \"EN\",\n  \"boost_domains\": [\n    \"leicestermercury.co.uk\"\n  ]\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift Top local news in the UK
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "query": "top local news today",
  "country": "GB",
  "language": "EN",
  "boost_domains": ["leicestermercury.co.uk"]
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/answer")! as URL,
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

### FDA-approved GLP-1 agonists restricted to government sources

**Request**

```json
{
  "query": "What are the FDA-approved GLP-1 receptor agonists?",
  "include_domains": [
    "fda.gov",
    "nih.gov"
  ]
}
```

**Response**

```json
{
  "answer": "The FDA-approved GLP-1 receptor agonists are exenatide, liraglutide, dulaglutide, lixisenatide, semaglutide and tirzepatide (the dual GIP/GLP-1 agonist). [[1, 2, 3, 4, 5]]",
  "citations": [
    {
      "source": "https://pubmed.ncbi.nlm.nih.gov/38531038/",
      "excerpts": [
        "Several FDA-approved short-acting and long-acting GLP-1 receptor agonists (GLP-1 RAs) are available in the United States for the treatment of T2DM. These are liraglutide, exenatide, dulaglutide, and semaglutide, all administered via subcutaneous injection."
      ]
    },
    {
      "source": "https://www.ncbi.nlm.nih.gov/books/NBK572151/",
      "excerpts": [
        "The FDA approved the first GLP-1RA exenatide in 2005."
      ]
    },
    {
      "source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12060260/",
      "excerpts": [
        "Currently, there are six FDA-approved GLP-1 RAs that have different properties, particularly in terms of administration, weight loss, and cardiovascular (CV) benefits: exenatide, liraglutide, dulaglutide, lixisenatide, semaglutide, and tirzepatide"
      ]
    }
  ],
  "results": {
    "web": [
      {
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5401818/",
        "title": "Glucagon-like peptide-1 and glucagon-like peptide-1 receptor agonists in the treatment of type 2 diabetes",
        "snippets": [
          "Exenatide, Brand name: Byetta, Dosing frequency: Twice daily, US FDA approved: Apr, 28. 2005"
        ]
      },
      {
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK551568/",
        "title": "Glucagon-Like Peptide-1 Receptor Agonists - StatPearls",
        "snippets": [
          "GLP-1 receptor agonists are a class of medications used in the management of type 2 diabetes mellitus and, more recently, for weight management."
        ]
      },
      {
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12847739/",
        "title": "Comprehensive evaluation of GLP-1 receptor agonist therapies",
        "snippets": [
          "The currently approved GLP-1 RAs include exenatide, liraglutide, lixisenatide, dulaglutide, and semaglutide"
        ]
      }
    ]
  }
}
```

**SDK Code**

```python FDA-approved GLP-1 agonists restricted to government sources
# Answer only from sources you trust
from youdotcom import You

with You() as you:
    res = you.answer(
        query="What are the FDA-approved GLP-1 receptor agonists?",
        include_domains=["fda.gov", "nih.gov"],
    )

    print(res.answer)

    for citation in res.citations or []:
        print(citation.source)

```

```javascript FDA-approved GLP-1 agonists restricted to government sources
const url = 'https://api.you.com/v1/answer';
const options = {
  method: 'POST',
  headers: {'X-API-Key': '<apiKey>', 'Content-Type': 'application/json'},
  body: '{"query":"What are the FDA-approved GLP-1 receptor agonists?","include_domains":["fda.gov","nih.gov"]}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go FDA-approved GLP-1 agonists restricted to government sources
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.you.com/v1/answer"

	payload := strings.NewReader("{\n  \"query\": \"What are the FDA-approved GLP-1 receptor agonists?\",\n  \"include_domains\": [\n    \"fda.gov\",\n    \"nih.gov\"\n  ]\n}")

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

```java FDA-approved GLP-1 agonists restricted to government sources
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://api.you.com/v1/answer")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"query\": \"What are the FDA-approved GLP-1 receptor agonists?\",\n  \"include_domains\": [\n    \"fda.gov\",\n    \"nih.gov\"\n  ]\n}")
  .asString();
```

```csharp FDA-approved GLP-1 agonists restricted to government sources
using RestSharp;

var client = new RestClient("https://api.you.com/v1/answer");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"query\": \"What are the FDA-approved GLP-1 receptor agonists?\",\n  \"include_domains\": [\n    \"fda.gov\",\n    \"nih.gov\"\n  ]\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift FDA-approved GLP-1 agonists restricted to government sources
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "query": "What are the FDA-approved GLP-1 receptor agonists?",
  "include_domains": ["fda.gov", "nih.gov"]
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/answer")! as URL,
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

### Quantum computing with domain exclusions and boosts

**Request**

```json
{
  "query": "What is the current state of quantum computing?",
  "exclude_domains": [
    "reddit.com",
    "quora.com"
  ],
  "boost_domains": [
    "nature.com",
    "science.org",
    "arxiv.org"
  ]
}
```

**Response**

```json
{
  "answer": "The current state of quantum computing is that it is still an early-stage, noisy technology operating in the so-called NISQ (Noisy Intermediate-Scale Quantum) era. Today's devices, ranging from dozens to over a thousand qubits, are not error-corrected and suffer from short coherence times (only microseconds) and scaling challenges, making them noisy, fragile, and expensive. Nonetheless, the field is moving beyond hype-driven demos toward practical hybrid HPC workflows, with quantum processors treated as accelerators for specialized tasks such as optimization, risk analysis, materials simulation and post-quantum cryptography. [[1, 2]]",
  "citations": [
    {
      "source": "https://www.newelectronics.co.uk/content/features/the-state-of-quantum-technology",
      "excerpts": [
        "Experts still believe we are at least five years away from a usable fault-tolerant quantum computer (FTC).",
        "Despite progress, quantum systems remain noisy, fragile and expensive."
      ]
    },
    {
      "source": "https://www.bluequbit.io/blog/how-does-quantum-computing-work",
      "excerpts": [
        "These systems are not yet error-corrected and remain limited by noise, decoherence, and shallow circuit depths.",
        "Quantum computing is currently in the Noisy Intermediate-Scale Quantum (NISQ) era, where devices range from a few dozen to over a thousand qubits."
      ]
    }
  ],
  "results": {
    "web": [
      {
        "url": "https://www.newelectronics.co.uk/content/features/the-state-of-quantum-technology",
        "title": "What's the current state of quantum? - New Electronics",
        "snippets": [
          "Qubit coherence times still last only microseconds, and scaling remains a major drawback. Today's quantum ecosystem is made up of 1,000 companies."
        ]
      },
      {
        "url": "https://builtin.com/articles/current-status-quantum-technology",
        "title": "What Is the Current Status of Quantum Technology?",
        "snippets": [
          "The slow-then-sudden path generative AI took to consumers is playing out differently in quantum computers, which have yet to reach mass adoption."
        ]
      },
      {
        "url": "https://thequantuminsider.com/2026/02/23/understanding-the-quantum-computing-hardware-landscape/",
        "title": "Understanding the Quantum Computing Hardware Landscape",
        "snippets": [
          "There has been tangible progress. Research groups have demonstrated small logical qubits and improvements in error correction fidelity."
        ]
      },
      {
        "url": "https://www.bluequbit.io/blog/how-does-quantum-computing-work",
        "title": "What Is Quantum Computing and How Does It Work?",
        "snippets": [
          "Quantum computing is currently in the Noisy Intermediate-Scale Quantum (NISQ) era, where devices range from a few dozen to over a thousand qubits."
        ]
      }
    ]
  }
}
```

**SDK Code**

```python Quantum computing with domain exclusions and boosts
# Drop unreliable sources and prefer authoritative ones
from youdotcom import You

with You() as you:
    res = you.answer(
        query="What is the current state of quantum computing?",
        exclude_domains=["reddit.com", "quora.com"],
        boost_domains=["nature.com", "science.org", "arxiv.org"],
    )

    print(res.answer)

```

```javascript Quantum computing with domain exclusions and boosts
const url = 'https://api.you.com/v1/answer';
const options = {
  method: 'POST',
  headers: {'X-API-Key': '<apiKey>', 'Content-Type': 'application/json'},
  body: '{"query":"What is the current state of quantum computing?","exclude_domains":["reddit.com","quora.com"],"boost_domains":["nature.com","science.org","arxiv.org"]}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go Quantum computing with domain exclusions and boosts
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.you.com/v1/answer"

	payload := strings.NewReader("{\n  \"query\": \"What is the current state of quantum computing?\",\n  \"exclude_domains\": [\n    \"reddit.com\",\n    \"quora.com\"\n  ],\n  \"boost_domains\": [\n    \"nature.com\",\n    \"science.org\",\n    \"arxiv.org\"\n  ]\n}")

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

```java Quantum computing with domain exclusions and boosts
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://api.you.com/v1/answer")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"query\": \"What is the current state of quantum computing?\",\n  \"exclude_domains\": [\n    \"reddit.com\",\n    \"quora.com\"\n  ],\n  \"boost_domains\": [\n    \"nature.com\",\n    \"science.org\",\n    \"arxiv.org\"\n  ]\n}")
  .asString();
```

```csharp Quantum computing with domain exclusions and boosts
using RestSharp;

var client = new RestClient("https://api.you.com/v1/answer");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"query\": \"What is the current state of quantum computing?\",\n  \"exclude_domains\": [\n    \"reddit.com\",\n    \"quora.com\"\n  ],\n  \"boost_domains\": [\n    \"nature.com\",\n    \"science.org\",\n    \"arxiv.org\"\n  ]\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift Quantum computing with domain exclusions and boosts
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "query": "What is the current state of quantum computing?",
  "exclude_domains": ["reddit.com", "quora.com"],
  "boost_domains": ["nature.com", "science.org", "arxiv.org"]
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/answer")! as URL,
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

### AI regulation in 2025 with a date range filter

**Request**

```json
{
  "query": "What were the major AI regulation developments in 2025?",
  "freshness": "2025-01-01to2025-12-31"
}
```

**Response**

```json
{
  "answer": "In 2025 AI regulation moved quickly at federal, state, and international levels. Key developments included the start of California's training-data transparency law AB 2013 (Jan 1) and Texas HB 149 (Jan 1), the creation of the DOJ AI Litigation Task Force (early Jan), an FTC pre-emption policy statement (Mar), the federal TAKE IT DOWN Act (May 19) and the FCC's federal disclosure-standard proceeding (Jun), Colorado's algorithmic-discrimination law SB 24-205 (Jun 30), and California's SB 942 (Aug 1). [[1]]",
  "citations": [
    {
      "source": "https://www.mondaq.com/unitedstates/new-technology/1725466/ai-wrapped-2025-the-year-hypothetical-ai-risks-became-operational-reality",
      "excerpts": [
        "California passed the Transparency in Frontier Artificial Intelligence Act (TFAIA) and New York introduced the RAISE Act."
      ]
    }
  ],
  "results": {
    "web": [
      {
        "url": "https://www.promptfoo.dev/blog/ai-regulation-2025/",
        "title": "How AI Regulation Changed in 2025",
        "snippets": [
          "California AB 2013 (training data transparency) effective Jan 1. Texas HB 149 effective Jan 1."
        ]
      },
      {
        "url": "https://fpf.org/blog/the-state-of-state-ai-legislative-approaches-to-ai-in-2025/",
        "title": "The State of State AI: Legislative Approaches to AI in 2025",
        "snippets": [
          "Frontier/foundation models regulation reintroduced: California and New York revived frontier model legislation (SB 53 and the RAISE Act)."
        ]
      },
      {
        "url": "https://www.bhfs.com/insight/states-can-continue-regulating-ai-for-now/",
        "title": "States Can Continue Regulating AI—For Now",
        "snippets": [
          "With the moratorium removed, states retain full authority to regulate artificial intelligence."
        ]
      },
      {
        "url": "https://clarkslegal.com/insights/articles/ai-and-data-protection-key-legal-developments-in-2025-2026/",
        "title": "AI and Data Protection: key legal developments in 2025",
        "snippets": [
          "As the EU AI Act continues to roll out, organizations must navigate evolving compliance requirements across jurisdictions."
        ]
      }
    ]
  }
}
```

**SDK Code**

```python AI regulation in 2025 with a date range filter
# Bound the answer to a specific date range
from youdotcom import You

with You() as you:
    res = you.answer(
        query="What were the major AI regulation developments in 2025?",
        freshness="2025-01-01to2025-12-31",
    )

    print(res.answer)

```

```javascript AI regulation in 2025 with a date range filter
const url = 'https://api.you.com/v1/answer';
const options = {
  method: 'POST',
  headers: {'X-API-Key': '<apiKey>', 'Content-Type': 'application/json'},
  body: '{"query":"What were the major AI regulation developments in 2025?","freshness":"2025-01-01to2025-12-31"}'
};

try {
  const response = await fetch(url, options);
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error(error);
}
```

```go AI regulation in 2025 with a date range filter
package main

import (
	"fmt"
	"strings"
	"net/http"
	"io"
)

func main() {

	url := "https://api.you.com/v1/answer"

	payload := strings.NewReader("{\n  \"query\": \"What were the major AI regulation developments in 2025?\",\n  \"freshness\": \"2025-01-01to2025-12-31\"\n}")

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

```java AI regulation in 2025 with a date range filter
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;

HttpResponse<String> response = Unirest.post("https://api.you.com/v1/answer")
  .header("X-API-Key", "<apiKey>")
  .header("Content-Type", "application/json")
  .body("{\n  \"query\": \"What were the major AI regulation developments in 2025?\",\n  \"freshness\": \"2025-01-01to2025-12-31\"\n}")
  .asString();
```

```csharp AI regulation in 2025 with a date range filter
using RestSharp;

var client = new RestClient("https://api.you.com/v1/answer");
var request = new RestRequest(Method.POST);
request.AddHeader("X-API-Key", "<apiKey>");
request.AddHeader("Content-Type", "application/json");
request.AddParameter("application/json", "{\n  \"query\": \"What were the major AI regulation developments in 2025?\",\n  \"freshness\": \"2025-01-01to2025-12-31\"\n}", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

```swift AI regulation in 2025 with a date range filter
import Foundation

let headers = [
  "X-API-Key": "<apiKey>",
  "Content-Type": "application/json"
]
let parameters = [
  "query": "What were the major AI regulation developments in 2025?",
  "freshness": "2025-01-01to2025-12-31"
] as [String : Any]

let postData = JSONSerialization.data(withJSONObject: parameters, options: [])

let request = NSMutableURLRequest(url: NSURL(string: "https://api.you.com/v1/answer")! as URL,
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