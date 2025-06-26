# app-service

## Versioning Information (relevant to A1)

We have implemented workflows that will update timestamps for a pre-release in the format `v{MAJOR}.{MINOR}.{PATCH}-pre-{TIMESTAMP}`.
 
Pre-release tags are updated on a simple git push.
```bash
git push
```

In order to create a release. Check the current pre-release information. This can be done using commands like 
```bash
git ls-remote --tags --sort="v:refname" origin
```
Choose the current pre-release version. Create a tag and push. This will create the a release with the versioning `v{MAJOR}.{MINOR}.{PATCH}`.

```bash
git tag v0.0.28
git push origin v0.0.28
```

## Monitoring information (relevant to A3)

Our implementation uses `Prometheus` to track the following metrics at the `/metrics` endpoint. We later use Grafana to scrape these values to create visualizations.

| Metric | Type | Labels | Information |
| :----: | :----: | :----: | :----: |
| REQUEST_COUNT | Gauge | `["method", "endpoint", "status_code"]` | Total number of requests to sentiment app |
| ACTIVE_USERS | Gauge | `["endpoint"]` | Number of currently active users |
| PREDICTION_REQUESTS | Counter | `["sentiment_result"]` | Total number of prediction requests |
| REQUEST_DURATION  | Uses Histogram | `["endpoint"]` | Time spent processing requests. |

The `REQUEST_DURATION` metric uses histogram to tell us the response time threshold at which 95% of all requests are handled.