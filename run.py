import sys
import argparse
from pathlib import Path

from src.scraper import scrape_user_data
from src.data_processor import process_data
from src.persona_builder import generate_standard_persona, generate_structured_persona

# Path Configuration
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))



def main():
    """
    The main function that orchestrates the entire persona generation pipeline.
    """
    # Set up the command-line argument parser with separate limits
    parser = argparse.ArgumentParser(
        description="Generate a user persona from a Reddit profile by running the full pipeline.",
        epilog="Example: python run.py --username kojied --post-limit 5 --comment-limit 5"
    )
    parser.add_argument("-u", "--username", type=str, required=True, help="The Reddit username to analyze.")
    parser.add_argument("-pl", "--post-limit", type=int, default=15, help="Number of recent posts to fetch. Default: 15.")
    parser.add_argument("-cl", "--comment-limit", type=int, default=15, help="Number of recent comments to fetch. Default: 15.")
    parser.add_argument("-m", "--mode", type=str, default="text", choices=['text', 'json'], help="Output mode: 'text' (Markdown) or 'json' (Structured). Default: text.")
    
    args = parser.parse_args()

    print("==============================================")
    print(f"▶️. Starting Persona Generation for: u/{args.username}")
    print(f"   - Post Limit: {args.post_limit}")
    print(f"   - Comment Limit: {args.comment_limit}")
    print(f"   - Output Mode: {args.mode}")
    print("==============================================")

    try:
        # Scrape Reddit Data
        print("\n[Step 1/3] Scraping user data from Reddit...")
        raw_data = scrape_user_data(
            username=args.username,
            post_limit=args.post_limit,
            comment_limit=args.comment_limit
        )
        
        if not raw_data:
            print("❌ Pipeline stopped: Scraping failed or returned no data.")
            sys.exit(1)
        print("✅ Scraping complete.")

        # Process and Analyze Data 
        print("\n[Step 2/3] Processing and analyzing scraped data...")
        processed_data = process_data(raw_data)
        
        if not processed_data:
            print("❌ Pipeline stopped: Data processing failed.")
            sys.exit(1)
        print("✅ Data processing and analysis complete.")

        # Build the Persona
        print("\n[Step 3/3] Generating persona with LLM...")
        if args.mode == 'json':
            _ = generate_structured_persona(processed_data)
        else:
            generate_standard_persona(processed_data)
        
        print("\n🎉🎉🎉")
        print("Persona generation pipeline finished successfully!")
        print("🎉🎉🎉")

    except Exception as e:
        print("\n🔥🔥🔥 An unexpected error occurred during the pipeline! 🔥🔥🔥")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()