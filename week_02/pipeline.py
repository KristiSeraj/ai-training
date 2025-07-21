from zenml import pipeline
from steps import (
    fetch_medium_posts,
    fetch_linkedin_posts_simulated,
    combine_and_process_posts,
    output_posts,
    export_posts_to_csv
)

@pipeline
def content_fetch_pipeline(username: str):
    medium = fetch_medium_posts(username=username)
    linkedin = fetch_linkedin_posts_simulated()
    combined = combine_and_process_posts(
        medium_posts=medium, linkedin_posts=linkedin
    )
    output_posts(posts=combined)
    export_posts_to_csv(posts=combined)
