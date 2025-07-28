import os

def create_env_file():
    """
    Creates a .env file and writes API keys to it.
    """
    env_content = """
GEMINI_API_KEY=AIzaSyAqko3NqGS-GtXhzm8LeiZ3xUEyo_XIqLo
LLAMA_API_KEY=LLM|1469017110898899|mJOyVVo1xc4vbUj6y1Wj-svovnE
COMPOSIO_API_KEY=ak_dJr0TZ3pX1e1-p2i9X4Z
"""
    try:
        with open(".env", "w") as f:
            f.write(env_content.strip())
        print("Successfully created .env file with API keys.")
        print("\nTo use these secrets in your Python scripts, follow these steps:")
        print("1. Install the python-dotenv library:")
        print("   pip install python-dotenv")
        print("\n2. Add the following code to your script to load the variables:")
        print("   from dotenv import load_dotenv")
        print("   import os")
        print("\n   load_dotenv()")
        print("\n   gemini_api_key = os.getenv('GEMINI_API_KEY')")
        print("   llama_api_key = os.getenv('LLAMA_API_KEY')")
        print("   composio_api_key = os.getenv('COMPOSIO_API_KEY')")

    except IOError as e:
        print(f"Error writing to .env file: {e}")

if __name__ == "__main__":
    create_env_file()