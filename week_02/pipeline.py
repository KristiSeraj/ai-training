from zenml import pipeline
from steps import (
    search_github_trending_repos,
    extract_repo_metadata_and_readme,
    embed_readme_content,
    store_in_vector_db
)

@pipeline
def github_repo_tracker_pipeline(language: str = "python", topic: str = "machine-learning", limit: int = 100):
    repos = search_github_trending_repos(
        language=language,
        topic=topic,
        limit=limit
    )
    
    github_repos = extract_repo_metadata_and_readme(repos=repos)
    
    repos_with_embeddings = embed_readme_content(repos=github_repos)
    
    db_filename = store_in_vector_db(repos=repos_with_embeddings)
    
    print(f"\nGitHub Repo Tracker Pipeline Complete!")
    print(f"Data stored in: {db_filename}")
    print(f"Repositories scraped and stored successfully!")
