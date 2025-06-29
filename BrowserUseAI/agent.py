from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import traceback # For better error reporting
import asyncio # Import asyncio

# Attempt to import your custom Agent
try:
    from browser_use import Agent # This is your custom agent
except ImportError:
    print("ERROR: Could not import 'Agent' from 'browser_use'.")
    print("Make sure 'browser_use.py' (or the module containing Agent) is in the same directory or accessible in your PYTHONPATH.")
    print("And ensure the 'Agent' class is correctly defined within it.")
    exit()


# Read GOOGLE_API_KEY into env
load_dotenv()

# --- Define an async main function ---
async def main():
    # --- 1. Initialize the LLM ---
    try:
        print("Initializing LLM...")
        llm = ChatGoogleGenerativeAI(
            model='gemini-2.0-flash-exp', # Using a standard, generally available model
            # google_api_key=os.getenv("GOOGLE_API_KEY") # Implicitly used if GOOGLE_API_KEY is set
        )
        print("LLM Initialized Successfully!")
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        traceback.print_exc()
        return # Exit the async function on error

    # --- 2. Define a Task and Create the Agent ---
    # Replace this with a task relevant to your browser agent's capabilities
    specific_task = "I need you to go to the following websites: https://www.uscis.gov/tools/reports-and-studies/h-1b-employer-data-hub, https://h1bdata.info/index.php?em=&job=structural+engineer&city=&year=2024, https://www.goinglobal.com/, and https://h1bgrader.com/job-titles/structural-engineer-d0g91ry7ko#job-h1b-sponsors. you can pon them in multiple tabs For each, search for companies in civil engineering and construction industry. Then, for each company, find the number of H-1B visas issued in 2024. Finally, return a list of companies and the number of H-1B visas issued in 2024."
    # specific_task = "What is the current weather in San Francisco?"
    # specific_task = "Find the price of the book 'Atomic Habits' on Amazon.com"

    print(f"\nCreating agent for task: '{specific_task}'")
    try:
        agent = Agent(
            task=specific_task,
            llm=llm
            # IMPORTANT: Your 'Agent' class from 'browser_use' might require
            # other parameters. For example:
            # - A browser instance (e.g., from Selenium or Playwright)
            # - Configuration for web interaction
            # You NEED to check the definition of `browser_use.Agent`
            # to know what it expects.
            # Note: The traceback suggests memory is enabled by default.
            # If you don't need memory, you might be able to disable it:
            # enable_memory=False
        )
        print("Agent created successfully.")
    except Exception as e:
        print(f"Error creating Agent instance: {e}")
        print("This could be due to missing arguments required by your Agent's __init__ method or missing dependencies (like google-generativeai).")
        traceback.print_exc()
        return # Exit the async function on error

    # --- 3. Run the Agent ---
    print("\nRunning agent...")
    try:
        # This is an ASSUMPTION. Your Agent class might have a different method name
        # (e.g., execute(), process(), __call__(), etc.)
        # --- Use await for the coroutine ---
        result = await agent.run()

        print("\n--- Agent Result ---")
        if result is not None:
            # Ensure result is printable (it might be complex)
            print(str(result))
        else:
            print("Agent did not return a result (or returned None).")
        print("--------------------")

    except AttributeError as e:
        print(f"AttributeError: {e}")
        print("This likely means your 'Agent' class does not have a method named 'run()'.")
        print("Please check the 'browser_use.Agent' class definition for the correct method to start the task execution.")
        traceback.print_exc()
    except Exception as e:
        print(f"An error occurred while running the agent: {e}")
        traceback.print_exc()

# --- Run the async main function ---
if __name__ == "__main__":
    asyncio.run(main())