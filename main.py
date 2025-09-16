import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import sys
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file
from call_function import call_function


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    system_prompt = """
        You are a helpful AI coding agent.

        When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

        - List files and directories
        - Read file contents
        - Execute Python files with optional arguments
        - Write or overwrite files

        All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
        """

    if len(sys.argv) < 2:
        print("I need a promp!")
        sys.exit(1)

    verbose_flag = False
    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose_flag = True
    prompt = sys.argv[1]

    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )

    config = types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt
    )

    if verbose_flag:
        print(f"User prompt: {prompt}")

    MAX_ITERS = 20
    for i in range(MAX_ITERS):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-001", contents=messages, config=config
            )
        except Exception as e:
            print(f"Error generating content: {e}")
            break

        if response is None or response.usage_metadata is None:
            print("response is malformed")
            break

        if verbose_flag and response.usage_metadata is not None:
            prompt_tokens = response.usage_metadata.prompt_token_count
            response_tokens = response.usage_metadata.candidates_token_count
            print(f"Prompt tokens: {prompt_tokens}")
            print(f"Response tokens: {response_tokens}")

        # Add model messages (the "I want to call ..." parts) to the convo
        if response.candidates:
            for candidate in response.candidates:
                if candidate and candidate.content:
                    messages.append(candidate.content)

        if response.function_calls and len(response.function_calls) > 0:
            for function_call_part in response.function_calls:
                function_call_result = call_function(function_call_part, verbose_flag)
                messages.append(function_call_result)

                try:
                    payload = function_call_result.parts[0].function_response.response
                except Exception:
                    raise RuntimeError(
                        "Function call did not return a function_response.response"
                    )

                if verbose_flag:
                    print(f"-> {payload}")
            continue

        if getattr(response, "text", None):
            if verbose_flag:
                print("Final response:")
            print(response.text)
            break

        # Otherwise, nothing more to do
        if verbose_flag:
            print("No further response; stopping.")
        break


main()
