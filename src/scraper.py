import os
from typing import List, Dict, Any

from dotenv import load_dotenv

import praw 
import prawcore


def scrape_user_posts(reddit_instance: praw.Reddit, username: str, post_limit: int = 5, verbose: bool = False) -> List[Dict[str, Any]]:
    """
    Scrape posts from a Reddit user.

    :param reddit_instance: An authenticated PRAW Reddit instance.
    :param username: The Reddit username to scrape.
    :param post_limit: The maximum number of posts to scrape.
    :return: A list of dictionaries containing post data.
    """
    posts_data = []
    if verbose:
        print(f"Scraping posts for user: {username}")

    try:
        # Get the User 
        user = reddit_instance.redditor(username)

        for submission in user.submissions.new(limit=post_limit):
            posts_data.append({
                "type": "Post",
                "id": submission.id,
                "title": submission.title,
                "author": submission.author.name if submission.author else "[deleted]",
                "timestamp": submission.created_utc,
                "text": submission.selftext,
                "url": f"https://www.reddit.com{submission.permalink}",
                "spoiler": submission.spoiler, 
                "over_18": submission.over_18,
                "is_original_content": submission.is_original_content,
                "num_comments": submission.num_comments,
                "score": submission.score, 

            })

        if verbose:
            print(f"Scraped {len(posts_data)} posts for user: {username}")
        
    except prawcore.exceptions.NotFound:
        if verbose:
            print(f"User {username} not found.")
        return []
    
    except Exception as e:
        if verbose:
            print(f"An error occurred while scraping posts for user {username}: {e}")
        return []
    
    return posts_data


def scrape_user_comments(reddit_instance: praw.Reddit, username: str, comment_limit: int = 20, verbose: bool = False) -> List:
    """
    Scrape comments from a Reddit user.

    :param reddit_instance: An authenticated PRAW Reddit instance.
    :param username: The Reddit username to scrape.
    :param comment_limit: The maximum number of comments to scrape.
    :return: A list of dictionaries containing comment data.
    """
    comments_data = []

    if verbose:
        print(f"Scraping comments for user: {username}")
    
    try:
        user = reddit_instance.redditor(username)
        for comment in user.comments.new(limit=comment_limit):
            comments_data.append({
                "type": "Comment",
                "id": comment.id,
                "author": comment.author.name if comment.author else "[deleted]",
                "timestamp": comment.created_utc,
                "text": comment.body,
                "url": f"https://www.reddit.com{comment.permalink}",
                "score": comment.score,
                "parent_id": comment.parent_id,
                "edited": comment.edited,
            })

        if verbose:
            print(f"Scraped {len(comments_data)} comments for user: {username}")
        
    except prawcore.exceptions.NotFound:
        pass

    except Exception as e:
        if verbose:
            print(f"An error occurred while scraping comments for user {username}: {e}")

    return comments_data


def scrape_user_data(
    username: str, 
    post_limit: int = 5,
    comment_limit: int = 20,
    verbose: bool = False
) -> Dict[Any, Any]:
    """
    Scrape both posts and comments from a Reddit user.

    :param username: The Reddit username to scrape.
    :param post_limit: The maximum number of posts to scrape.
    :param comment_limit: The maximum number of comments to scrape.
    :param verbose: If True, print additional information.
    :return: A dictionary containing posts and comments data.
    """ 
    load_dotenv() # To make sure client id and secret are loaded 

    CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    USER_AGENT = "User Persona Agent" 

    if not all([CLIENT_ID, CLIENT_SECRET]):
        print("FATAL: Reddit API credentials are not set in .env file!")
        return None
    
    # Initialize User
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )

    # Verify if the user exists
    try:
        reddit.redditor(username).id
    except prawcore.exceptions.NotFound:
        print(f"ERROR: User {username} does not exist.")
        return None
    
    # Scrape posts and comments
    posts = scrape_user_posts(reddit, username, post_limit, verbose)
    comments = scrape_user_comments(reddit, username, comment_limit, verbose)

    return {
        "username": username,
        "posts": posts,
        "comments": comments
    }
