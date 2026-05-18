# Knowledge Management Skill

Provides access to the knowledge base through the db-knowledge MCP server.

## Tools Used
- `search_all` — Full-text + vector + memory combined search
- `vector_search` — Semantic search via FAISS embeddings
- `search_memory` — Memory layer search
- `analyze_content` — Extract tags, entities, summary from content
- `get_graph` — Knowledge graph overview
- `get_status` — System status

## Workflows
### Search Knowledge Base
1. Call `search_all` with the user's query
2. Return formatted results

### Analyze New Content
1. Call `analyze_content` with the file path
2. Call `process_file` to run full pipeline
