import os
from datetime import datetime

import json
from collections import Counter
from typing import List, Dict, Any

# Path Configurations
from pathlib import Path
current_file_path = Path(__file__)
SRC_DIR = current_file_path.parent
PROJECT_ROOT = SRC_DIR.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# Helper Methods 
def _get_active_period(timestamps: List[Any]) -> str: 
    """Helper function to determine the most active time period from timestamps."""
    if not timestamps:
        return "not enough data" 
    
    # Extract hour (0-23) from timestamps
    hours = [datetime.fromtimestamp(ts).hour for ts in timestamps]
    hour_counts = Counter(hours)

    if not hour_counts:
        return "not enough data"

    most_common_hour = hour_counts.most_common(1)[0][0]
    
    # Categorize to Human-readable period
    if 5 <= most_common_hour < 12:
        return "Morning (5am-12pm UTC)"
    elif 12 <= most_common_hour < 17:
        return "Afternoon (12pm-5pm UTC)"
    elif 17 <= most_common_hour < 21:
        return "Evening (5pm-9pm UTC)"
    else:
        return "Late Night (9pm-4am UTC)"

    
def save_raw_data(raw_data: Dict[Any, Any], username: str, verbose: bool = False) -> Path:
    """
    Save raw data to a JSON file.

    :param raw_data: The raw data to save.
    :param username: The Reddit username associated with the data.
    :param verbose: If True, print status messages.
    :return: The path to the saved JSON file.
    """
    if not raw_data:
        raise ValueError("Raw data is empty or None.")

    # Ensure the directory exists
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # Create a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = RAW_DATA_DIR / f"{username}_{timestamp}_raw_data.json"

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=4)
        if verbose:
            print(f"INFO: Raw data for '{username}' saved to {file_path}")
        return file_path
    except Exception as e:
        raise IOError(f"Failed to save raw data. Reason: {e}")


# Core 
def process_data(raw_data: Dict[Any, Any], verbose: bool = False) -> Dict[Any, Any] or None: 
    """
    Process raw data from Reddit API into a more user-friendly format.

    :param raw_data: A dictionary containing 'summary_analysis' and 'content_for_llm',
        or None if the input is invalid.

    This function: 
    1. Saves the raw data to a JSON file.
    2. Analyzes metadata (timestamps, scores, post-types) to create a quantitative summary.
    3. Consolidates textual content for qualitative analysis by LLMs. 
    """
    if not raw_data or 'username' not in raw_data:
        print("ERROR: Invalid or empty raw_data received in processor.")
        return None

    username = raw_data.get('username')
    posts = raw_data.get('posts', [])
    comments = raw_data.get('comments', [])

    # -- Save Raw Data --
    raw_data_file = save_raw_data(raw_data, username, verbose)

    # -- Analyze Metadata --
    all_timestamps = [p.get('timestamp') for p in posts] + [c.get('timestamp') for c in comments]
    post_scores = [p.get('score', 0) for p in posts]
    comment_scores = [c.get('score', 0) for c in comments]
    num_posts, num_comments = len(posts), len(comments)

    summary = {
        "username": username,
        "total_posts": num_posts,
        "total_comments": num_comments,
        "most_active_period": _get_active_period(all_timestamps),
        "average_post_score": round(sum(post_scores) / num_posts, 2) if num_posts > 0 else 0,
        "average_comment_score": round(sum(comment_scores) / num_comments, 2) if num_comments > 0 else 0,
        "nsfw_post_percentage": round((sum(1 for p in posts if p.get('over_18')) / num_posts) * 100, 2) if num_posts > 0 else 0,
        "spoiler_post_percentage": round((sum(1 for p in posts if p.get('spoiler')) / num_posts) * 100, 2) if num_posts > 0 else 0,
        "original_content_percentage": round((sum(1 for p in posts if p.get('is_original_content')) / num_posts) * 100, 2) if num_posts > 0 else 0,
        "edited_comment_percentage": round((sum(1 for c in comments if c.get('edited')) / num_comments) * 100, 2) if num_comments > 0 else 0,
    }

    # -- Consolidate Content for LLMs --
    content_for_llm = []
    for post in posts:
        full_text = f"Post Title: {post.get('title', '')}\n\nPost Body: {post.get('text', '')}".strip()
        if full_text:
            content_for_llm.append(
                {
                    "type": "Post",
                    "source_url": post.get('url'),
                    "content": full_text
                }
            )
    for comment in comments:
        comment_text = comment.get('text', '').strip()
        if comment_text:
            content_for_llm.append(
                {
                    "type": "Comment", 
                    "source_url": comment.get('url'),
                    "content": comment_text
                }
            )

    if verbose: 
        print(f"INFO: Analysis complete for '{username}'. Found {len(content_for_llm)} pieces of text content.")

    # Save the processed data to a JSON file
    processed_data_file = PROJECT_ROOT / "data" / "processed" / f"{username}_processed_data.json"
    os.makedirs(processed_data_file.parent, exist_ok=True)
    with open(processed_data_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary_analysis": summary,
            "content_for_llm": content_for_llm
        }, f, indent=4)
    if verbose:
        print(f"INFO: Processed data for '{username}' saved to {processed_data_file}")
        
    return {
        "summary_analysis": summary,
        "content_for_llm": content_for_llm
    }   


