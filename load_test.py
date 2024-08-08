import subprocess
import time
import statistics
import os
import platform
import shlex
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

def check_llamafile():
    filename = "./mistral-7b-instruct-v0.2.Q5_K_M.llamafile"
    if not os.path.exists(filename):
        print(f"Error: {filename} does not exist in the current directory.")
        return False
    
    if not os.access(filename, os.X_OK):
        print(f"Error: {filename} is not executable. Trying to set execute permission...")
        try:
            os.chmod(filename, os.stat(filename).st_mode | 0o111)
            print("Execute permission set.")
        except Exception as e:
            print(f"Failed to set execute permission: {e}")
            return False
    
    return True

def run_llamafile(prompt, timeout=300):
    escaped_prompt = shlex.quote(prompt)
    command = f"./mistral-7b-instruct-v0.2.Q5_K_M.llamafile -p {escaped_prompt}"
    start_time = time.time()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        end_time = time.time()
        return result.stdout, end_time - start_time
    except subprocess.TimeoutExpired:
        print(f"Error: Command timed out after {timeout} seconds.")
        return None, timeout
    except subprocess.CalledProcessError as e:
        print(f"Error running LLamafile: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None

def count_tokens(text):
    return len(text.split()) if text else 0

def worker(prompt, timeout):
    print(f"Starting request with prompt: {prompt[:30]}...")
    output, latency = run_llamafile(prompt, timeout)
    if output is None:
        print(f"Request failed for prompt: {prompt[:30]}...")
        return None
    tokens = count_tokens(output)
    speed = tokens / latency if latency > 0 else 0
    print(f"Completed request. Latency: {latency:.2f}s, Speed: {speed:.2f} tokens/s")
    return {
        "prompt": prompt,
        "latency": latency,
        "speed": speed,
        "tokens": tokens
    }

def load_test(num_requests, max_workers, timeout):
    prompts = [
        "How do I improve my running speed?",
        "What are the best exercises for building muscle?",
        "How can I lose weight quickly?",
        "What is the best diet for weight loss?",
        "How do I stay motivated to exercise?",
        "What are the benefits of yoga?",
        "How can I improve my flexibility?"
    ]

    results = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_prompt = {executor.submit(worker, random.choice(prompts), timeout): i for i in range(num_requests)}
        for future in as_completed(future_to_prompt):
            result = future.result()
            if result:
                results.append(result)

    end_time = time.time()
    total_time = end_time - start_time

    if results:
        latencies = [r["latency"] for r in results]
        speeds = [r["speed"] for r in results]
        tokens = [r["tokens"] for r in results]

        print(f"\nLoad Test Results:")
        print(f"Total requests: {num_requests}")
        print(f"Successful requests: {len(results)}")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Requests per second: {len(results)/total_time:.2f}")
        print(f"Average latency: {statistics.mean(latencies):.2f} seconds")
        print(f"Average speed: {statistics.mean(speeds):.2f} tokens/second")
        print(f"Average tokens per response: {statistics.mean(tokens):.2f}")
        print(f"Min latency: {min(latencies):.2f} seconds")
        print(f"Max latency: {max(latencies):.2f} seconds")
    else:
        print("No successful requests to calculate statistics.")

def main():
    print(f"Python version: {platform.python_version()}")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Machine: {platform.machine()}")
    
    if not check_llamafile():
        return

    num_requests = int(input("Enter the number of requests to make: "))
    max_workers = int(input("Enter the maximum number of concurrent workers: "))
    timeout = int(input("Enter the timeout in seconds for each request: "))

    load_test(num_requests, max_workers, timeout)

if __name__ == "__main__":
    main()