from zenml import step
from typing import List
import feedparser
import pandas as pd

@step
def fetch_medium_posts(username: str) -> List[str]:
    url = f"https://medium.com/feed/@{username}"
    feed = feedparser.parse(url)
    return [entry.title for entry in feed.entries]

@step
def fetch_linkedin_posts_simulated() -> List[str]:
    return [
        "Announcing our new AI feature",
        "We just raised a $10M Series A round",
        "Tips for managing engineering teams remotely"
    ]

@step
def combine_and_process_posts(
    medium_posts: List[str], linkedin_posts: List[str]
) -> List[str]:
    all_posts = medium_posts + linkedin_posts
    return [post.upper() for post in all_posts]

@step
def output_posts(posts: List[str]) -> None:
    print("Combined Posts from Medium and LinkedIn:\n")
    for i, post in enumerate(posts, 1):
        print(f"{i}. {post}")

@step
def export_posts_to_csv(posts: List[str]) -> None:
    df = pd.DataFrame(posts, columns=["Post"])
    df.to_csv("exported_posts.csv", index=False)
    print("Posts exported to 'exported_posts.csv'")

