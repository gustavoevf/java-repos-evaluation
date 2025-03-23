import requests
import pandas as pd
import time

# Defina seu token do GitHub
TOKEN = "TOKEN"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# URL da API GraphQL
graphql_url = "https://api.github.com/graphql"

# Consulta GraphQL
query = """
query ($cursor: String) {
  search(query: "stars:>0 sort:stars-desc language:Java", type: REPOSITORY, first: 25, after: $cursor) {
    pageInfo {
      endCursor
      hasNextPage
    }
    edges {
      node {
        ... on Repository {
          id
          full_name: nameWithOwner
          html_url: url
          stargazers_count: stargazerCount
          created_at: createdAt
          updated_at: updatedAt
          primaryLanguage {
            name
          }
          releases {
            totalCount
          }
        }
      }
    }
  }
}
"""

repositorios = []
cursor = None
i = 0

# Coletar 1.000 repositórios
for _ in range(40):
    i+=1
    print("Coletando dados..." + str(i))
    
    response = requests.post(graphql_url, headers=HEADERS, json={"query": query, "variables": {"cursor": cursor}})
    
    if response.status_code != 200:
        print(f"Erro: {response.status_code}, {response.text}")
        break
    
    data = response.json()
    search_data = data["data"]["search"]
    
    # Extrair repositórios
    for edge in search_data["edges"]:
        repo = edge["node"]
        primary_language = repo["primaryLanguage"]["name"] if repo["primaryLanguage"] else ""
        repositorios.append({
            "id": repo["id"],
            "full_name": repo["full_name"],
            "html_url": repo["html_url"],
            "stargazers_count": repo["stargazers_count"],
            "created_at": repo["created_at"],
            "updated_at": repo["updated_at"],
            "primary_language": primary_language,
            "releases": repo["releases"]["totalCount"],
        })

    
    # Atualizar cursor para próxima página
    cursor = search_data["pageInfo"]["endCursor"]
    if not search_data["pageInfo"]["hasNextPage"]:
        break
    
    time.sleep(2)  # Evitar atingir limites da API

# Criar DataFrame
df = pd.DataFrame(repositorios)

# Salvar em CSV
df.to_csv("github_top_1000.csv", index=False)

print("Coleta finalizada e salva em 'github_top_1000.csv'.")