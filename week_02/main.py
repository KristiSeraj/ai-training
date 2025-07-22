from pipeline import github_repo_tracker_pipeline

if __name__ == "__main__":
    print("GitHub Repo Tracker - Python Repositories")
    print("="*50)
    print()
    print("Searching for Python repositories...")
    
    github_repo_tracker_pipeline(
        language="python",
        topic="machine-learning",
        limit=0
    )
    
    print("\n" + "="*50)
    print("PIPELINE COMPLETE")
    print("="*50)
