import os
import sys
from pathlib import Path
from .pipeline import NewsProcessingPipeline

def main():
    print("🎯 News Processing Pipeline v1.0")
    pipeline = NewsProcessingPipeline()
    
    print("\n📋 Example 1: Processing sample articles")
    result1 = pipeline.run_pipeline("sample")
    
    print("\n📋 Example 2: Processing Discord messages")
    try:
        import json
        with open("../messages_example.json", "r") as f:
            messages_list = json.load(f)
        
        sample_messages = messages_list[:3]  # Just first 3 for demo
        result2 = pipeline.run_pipeline_with_messages(sample_messages)
    except Exception as e:
        print(f"⚠️  Could not process messages: {e}")
    
    print("\n📋 Example 3: Retrieving recent results")
    recent_results = pipeline.get_recent_results(limit=10)
    print(f"Found {recent_results['total_articles']} articles and {recent_results['total_clusters']} clusters")

def run_single_pipeline(source: str = "sample"):
    pipeline = NewsProcessingPipeline()
    result = pipeline.run_pipeline(source)
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        source = sys.argv[1]
        run_single_pipeline(source)
    else:
        main()
