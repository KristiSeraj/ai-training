# GitHub Repo Tracker - Week 02

A simple pipeline that searches GitHub for Python repositories, extracts their data, and stores them in databases.

## What it does

1. **Searches** GitHub for trending Python repositories
2. **Extracts** metadata and README content
3. **Creates** semantic embeddings
4. **Stores** data in MongoDB and Qdrant

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start databases
```bash
# Start MongoDB
mongod

# Start Qdrant (in another terminal)
docker run -p 6333:6333 qdrant/qdrant
```

### 3. Run the pipeline
```bash
python main.py
```

## Files

- `main.py` - Runs the pipeline
- `pipeline.py` - Defines the pipeline steps
- `steps.py` - Contains the actual functions
- `requirements.txt` - Python packages needed

## Pipeline Steps

1. **Search** - Uses GitHub API to find Python repos
2. **Extract** - Downloads metadata and README files
3. **Embed** - Creates semantic embeddings
4. **Store** - Saves to MongoDB and Qdrant

## Example Output

```
GitHub Repo Tracker - Python Repositories
==================================================

Searching for Python repositories...
Found 10 Python repositories for query: language:python machine-learning sort:stars
Successfully extracted data for 10 repositories
Generated embeddings for 10 repositories
Successfully stored 10 repositories

==================================================
PIPELINE COMPLETE
==================================================
```

## Optional: Qdrant Cloud

If you want to use Qdrant Cloud instead of local:

1. Create account at https://cloud.qdrant.io/
2. Create a `.env` file:
```
QDRANT_API_KEY=your_api_key_here
QDRANT_URL=https://your-cluster.qdrant.io
```