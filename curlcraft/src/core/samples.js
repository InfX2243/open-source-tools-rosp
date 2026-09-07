export const SAMPLES = [
  {
    id: 'post-json-auth',
    name: 'POST JSON with Bearer Auth',
    badge: 'POST',
    curl: `curl -X POST https://api.example.com/v1/users \\
  -H "Authorization: Bearer sec_tok_98234ab819" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Sarah Connor",
    "email": "sarah@cyberdyne.io",
    "role": "engineer",
    "tags": ["cloud", "devops"]
  }'`
  },
  {
    id: 'get-query-params',
    name: 'GET with Query Filters & Headers',
    badge: 'GET',
    curl: `curl "https://api.github.com/repos/facebook/react/issues?state=open&sort=created&direction=desc&per_page=10" \\
  -H "Accept: application/vnd.github.v3+json" \\
  -H "User-Agent: CurlCraft-App"`
  },
  {
    id: 'post-form-urlencoded',
    name: 'POST Form URL Encoded',
    badge: 'POST',
    curl: `curl -X POST https://auth.example.com/oauth/token \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  --data-urlencode "grant_type=client_credentials" \\
  --data-urlencode "client_id=app_client_123" \\
  --data-urlencode "client_secret=super_secret_key_456"`
  },
  {
    id: 'multipart-file-upload',
    name: 'Multipart Form & File Upload',
    badge: 'POST',
    curl: `curl -X POST https://api.storage.com/upload \\
  -H "Authorization: Bearer sk_live_99214" \\
  -F "file=@/documents/report.pdf" \\
  -F "description=Quarterly Financial Report" \\
  -F "is_public=false"`
  },
  {
    id: 'graphql-query',
    name: 'GraphQL Query',
    badge: 'POST',
    curl: `curl -X POST https://api.spacex.land/graphql/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "query GetLaunches { launchesPast(limit: 5) { mission_name launch_date_utc rocket { rocket_name } } }"
  }'`
  },
  {
    id: 'basic-auth',
    name: 'GET with Basic Auth & Timeout',
    badge: 'GET',
    curl: `curl -X GET https://api.stripe.com/v1/customers \\
  -u "sk_test_51Mz...:password123" \\
  -m 15 \\
  -H "Stripe-Version: 2023-10-16"`
  }
];
