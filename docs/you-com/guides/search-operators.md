> For clean Markdown of any page, append .md to the page URL.
> For a complete documentation index, see https://you.com/docs/llms.txt.
> For AI client integration (Claude Code, Cursor, etc.), connect to the MCP server at https://you.com/docs/_mcp/server.

# Search operators

> Discover the search operators and learn how to use them

Search operators are powerful modifiers that let you craft precise, targeted queries for the Web Search API. By combining operators like `site:`, `filetype:`, logical connectors (`AND`, `OR`, `NOT`), and inclusion/exclusion symbols (`+`, `-`), you can filter results by domain, file type, and content requirements. This enables you to run complex searches that get you exactly what you need.

Use the following search operators with the [Web Search API](/docs/api-reference/search/v1-search):

| Operator | Description                                                            | Example                 |
| -------- | ---------------------------------------------------------------------- | ----------------------- |
| site     | Searches for webpages from a particular domain (including subdomains)  | `site:uscourts.gov`     |
| filetype | Searches for webpages that are of the specified file type              | `filetype:pdf`          |
| +        | Searches for webpages that contain the exact term after the `+`        | `+GAAP`                 |
| -        | Searches for webpages that do not contain the exact term after the `-` | `-prs`                  |
| AND      | Logical operator to combine expressions                                | `guitar AND Fender`     |
| OR       | Logical operator to combine expressions                                | `guitar OR drum`        |
| NOT      | Negation of expressions                                                | `NOT site:uscourts.gov` |

Let's look at a complex example that combines multiple operators.

You are researching machine learning best practices and want to find tutorials or academic papers on either Python or PyTorch, in PDF format. You're focused on PyTorch, so you want to exclude results that mention TensorFlow. Here's how you'd construct your query:

```python
from youdotcom import You

with You() as you:
  res = you.search(
    query="machine learning best practices (Python OR PyTorch) -TensorFlow filetype:pdf",
    count=5
  )

  # Print PDF results with download links
  if res.results and res.results.web:
      for result in res.results.web:
          print(f"{result.title}")
          print(f"  Download: {result.url}\n")
```

```typescript
import { You } from "@youdotcom-oss/sdk";

const you = new You({
  apiKeyAuth: process.env.YDC_API_KEY,
});

async function run() {
  const result = await you.search({
    query: "machine learning best practices (Python OR PyTorch) -TensorFlow filetype:pdf",
    count: 5,
  });

  console.log(result);
}

run();
```

```curl
curl -X POST 'https://ydc-index.io/v1/search' \
  -H "X-API-Key: $YDC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning best practices (Python OR PyTorch) -TensorFlow filetype:pdf",
    "count": 5
  }'
```

You should get back something like this:

```json maxLines=50
{
  "results": {
    "web": [
      {
        "url": "https://hlevkin.com/hlevkin/45MachineDeepLearning/DL/Ketkar,Moolayil Deep Learning with Python.pdf",
        "title": "Deep Learning with Python Learn Best Practices of Deep",
        "description": "Chapter 1 Introduction to Machine Learning and Deep Learning ... There are limits to how much human effort can be thrown at the problem. ... Mechanical Turk). ... Python and some coursework in linear algebra, calculus, and probability. Readers should refer to the following in case they need to cover these ... PyTorch ...",
        "snippets": [
            "Chapter 1 Introduction to Machine Learning and Deep Learning ... There are limits to how much human effort can be thrown at the problem. ... Mechanical Turk). ... Python and some coursework in linear algebra, calculus, and probability. Readers should refer to the following in case they need to cover these ... PyTorch is not installed as a part of the Anaconda distribution.",
            "Chapter 1 Introduction to Machine Learning and Deep Learning ... N. Ketkar and J. Moolayil, Deep Learning with Python, ... PyTorch.",
            "You should install PyTorch, torchtext, and torchvision, along with the · Anaconda environment. Note that Python 3.6 (and above) is recommended for the exercises in · this book. We highly recommend creating a new Python environment after ... As human beings, we are intuitively aware of the concept of learning.",
            "Overall, PyTorch provides an excellent framework and · platform for researchers and developers to work on cutting-edge deep ... Figure 2-1. 0-n dimensional tensor ... To begin, let’s explore the multitude of ways to construct tensors. The most basic way is to construct a tensor using lists in Python. The · following exercise will demonstrate an array of tensor operations that · are commonly used in building deep learning applications."
        ],
        "favicon_url": "https://you.com/favicon?domain=hlevkin.com&size=128"
      },
      {
        "url": "https://isip.piconepress.com/courses/temple/ece_4822/resources/books/Deep-Learning-with-PyTorch.pdf",
        "title": "Deep Learning with PyTorch",
        "description": "Index of /courses/temple/ece_4822/resources/books · Name Last modified Size Description · Parent Directory - Deep-Learning-with-P..> 2020-08-26 14:58 45M · Apache Server at isip.piconepress.com Port 443",
        "snippets": [],
        "favicon_url": "https://you.com/favicon?domain=isip.piconepress.com&size=128"
      },
      {
        "url": "https://github.com/borninfreedom/DeepLearning/blob/master/Books/Deep-Learning-with-PyTorch.pdf",
        "title": "DeepLearning/Books/Deep-Learning-with-PyTorch.pdf at master · ...",
        "description": "深度学习、强化学习、模仿学习与机器人. Contribute to borninfreedom/DeepLearning development by creating an account on GitHub.",
        "snippets": [],
        "thumbnail_url": "https://opengraph.githubassets.com/491cdbc5e2c483ec0b7b14473b6a4e76899906bc05570ac6888a0772b401c62d/borninfreedom/DeepLearning",
        "favicon_url": "https://you.com/favicon?domain=github.com&size=128"
      },
      {
        "url": "https://machinelearningmastery.com/wp-content/uploads/2023/04/deep_learning_with_pytorch_mini_course.pdf",
        "title": "MACHINE LEARNING MASTERY Deep Learning with PyTorch 9-Day Mini-Course",
        "description": "MACHINE · LEARNING · MASTERY",
        "snippets": [],
        "favicon_url": "https://you.com/favicon?domain=machinelearningmastery.com&size=128"
      },
      {
        "url": "https://hprc.tamu.edu/files/training/2021/Spring/Introduction_to_DL_with_PyTorch.pdf",
        "title": "Introduction to Deep Learning with PyTorch Jian Tao jtao@tamu.edu",
        "description": "Introduction to Deep Learning · with PyTorch · Jian Tao · jtao@tamu.edu · HPRC Short Course · 4/16/2021 · Part I · Setting up a working · environment (15 mins) · Part III",
        "snippets": [
            "Introduction to Deep Learning with PyTorch · Q&A · (5 mins/part) Part I. Working Environment · HPRC Portal · * VPN is required for off-campus users. Login HPRC Portal (Terra) Terra Shell Access - I · Terra Shell Access - II · Python Virtual Environment (VENV) Create a VENV ·",
            "Part II. Deep Learning"
        ],
        "favicon_url": "https://you.com/favicon?domain=hprc.tamu.edu&size=128"
      }
    ]
  },
  "metadata": {
    "query": "machine learning best practices (Python OR PyTorch) -TensorFlow filetype:pdf",
    "search_uuid": "dacab1bf-042d-4cd2-b803-ebcb45904cb6",
    "latency": 0.7680318355560303
  }
}
```