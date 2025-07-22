from zenml import step
from typing import List, Dict, Any
import pandas as pd
import requests
import time
import json
import os
from datetime import datetime
import base64
from sentence_transformers import SentenceTransformer
import numpy as np
from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

@dataclass
class GitHubRepo:
    name: str
    full_name: str
    description: str
    language: str
    stars: int
    forks: int
    url: str
    readme_content: str
    topics: List[str]
    created_at: str
    updated_at: str
    embedding: List[float] = None

@step
def search_github_trending_repos(language: str = "python", topic: str = "machine-learning", limit: int = 100) -> List[Dict[str, Any]]:
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'GitHub-Repo-Tracker'
    }
    
    base_url = "https://api.github.com/search/repositories"
    
    query = f"language:{language}"
    if topic:
        query += f" {topic}"
    query += " sort:stars"
    
    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc',
        'per_page': min(limit, 100)
    }
    
    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        repos = data.get('items', [])
        
        print(f"Found {len(repos)} Python repositories")
        
        return repos
        
    except requests.exceptions.RequestException as e:
        print(f"Error accessing GitHub API: {e}")
        return []
    except Exception as e:
        print(f"Error searching GitHub repos: {e}")
        return []

@step
def extract_repo_metadata_and_readme(repos: List[Dict[str, Any]]) -> List[GitHubRepo]:
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'GitHub-Repo-Tracker'
    }
    
    github_repos = []
    
    for repo in repos:
        try:
            name = repo.get('name', '')
            full_name = repo.get('full_name', '')
            description = repo.get('description', '')
            language = repo.get('language', 'Unknown')
            stars = repo.get('stargazers_count', 0)
            forks = repo.get('forks_count', 0)
            url = repo.get('html_url', '')
            topics = repo.get('topics', [])
            created_at = repo.get('created_at', '')
            updated_at = repo.get('updated_at', '')
            
            readme_url = f"https://api.github.com/repos/{full_name}/readme"
            readme_response = requests.get(readme_url, headers=headers, timeout=10)
            
            readme_content = ""
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                readme_content = base64.b64decode(readme_data.get('content', '')).decode('utf-8')
            else:
                readme_content = "README not found"
            
            github_repo = GitHubRepo(
                name=name,
                full_name=full_name,
                description=description,
                language=language,
                stars=stars,
                forks=forks,
                url=url,
                readme_content=readme_content,
                topics=topics,
                created_at=created_at,
                updated_at=updated_at
            )
            
            github_repos.append(github_repo)
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Error extracting data for {repo.get('full_name', 'unknown')}: {e}")
            continue
    
    print(f"Extracted data for {len(github_repos)} repositories")
    return github_repos

@step
def embed_readme_content(repos: List[GitHubRepo]) -> List[GitHubRepo]:
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        for repo in repos:
            embedding_text = f"{repo.name} {repo.description} {repo.readme_content}"
            embedding = model.encode(embedding_text)
            repo.embedding = embedding.tolist()
        
        print(f"Generated embeddings for {len(repos)} repositories")
        return repos
        
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return repos

@step
def store_in_vector_db(repos: List[GitHubRepo]) -> str:
    try:
        mongo_client = MongoClient('mongodb://localhost:27017/')
        db = mongo_client['github_repos']
        collection = db['repositories']
        
        qdrant_api_key = os.getenv('QDRANT_API_KEY')
        qdrant_url = os.getenv('QDRANT_URL', 'https://your-cluster.qdrant.io')
        
        if not qdrant_api_key:
            qdrant_client = QdrantClient("localhost", port=6333)
        else:
            qdrant_client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key
            )
        
        collection_name = "github_repos"
        
        try:
            qdrant_client.get_collection(collection_name)
        except:
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
        
        stored_ids = []
        
        for i, repo in enumerate(repos):
            try:
                mongo_doc = {
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'description': repo.description,
                    'language': repo.language,
                    'stars': repo.stars,
                    'forks': repo.forks,
                    'url': repo.url,
                    'readme_content': repo.readme_content,
                    'topics': repo.topics,
                    'created_at': repo.created_at,
                    'updated_at': repo.updated_at,
                    'created_timestamp': datetime.now()
                }
                
                mongo_result = collection.insert_one(mongo_doc)
                mongo_id = str(mongo_result.inserted_id)
                
                if repo.embedding:
                    qdrant_point = PointStruct(
                        id=i,
                        vector=repo.embedding,
                        payload={
                            'mongo_id': mongo_id,
                            'name': repo.name,
                            'full_name': repo.full_name,
                            'language': repo.language,
                            'stars': repo.stars,
                            'topics': repo.topics
                        }
                    )
                    qdrant_client.upsert(
                        collection_name=collection_name,
                        points=[qdrant_point]
                    )
                
                stored_ids.append(mongo_id)
                
            except Exception as e:
                print(f"Error storing repo {repo.name}: {e}")
                continue
        
        print(f"Stored {len(stored_ids)} repositories")
        
        if qdrant_api_key:
            return f"mongodb://localhost:27017/github_repos, qdrant://{qdrant_url}/{collection_name}"
        else:
            return f"mongodb://localhost:27017/github_repos, qdrant://localhost:6333/{collection_name}"
        
    except Exception as e:
        print(f"Error storing in databases: {e}")
        return ""

