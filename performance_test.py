import subprocess
import time
import statistics
import os
import platform
import shlex

def check_llamafile():
    filename = "./mistral-7b-instruct-v0.2.Q5_K_M.llamafile"
    if not os.path.exists(filename):
        print(f"Error: {filename} does not exist in the current directory.")
        return False
    
    if not os.access(filename, os.X_OK):
        print(f"Error: {filename} is not executable. Trying to set execute permission...")
        try:
            os.chmod(filename, os.stat(filename).st_mode | 0o111)
            print("Execute permission set. Please run the script again.")
        except Exception as e:
            print(f"Failed to set execute permission: {e}")
        return False
    
    file_info = subprocess.run(["file", filename], capture_output=True, text=True)
    print(f"File information: {file_info.stdout.strip()}")
    
    return True

def run_llamafile(prompt):
    escaped_prompt = shlex.quote(prompt)
    command = f"./mistral-7b-instruct-v0.2.Q5_K_M.llamafile -p {escaped_prompt}"
    start_time = time.time()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        end_time = time.time()
        return result.stdout, end_time - start_time
    except subprocess.TimeoutExpired:
        print(f"Error: Command timed out after 60 seconds.")
        return None, None
    except subprocess.CalledProcessError as e:
        print(f"Error running LLamafile: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None

def count_tokens(text):
    return len(text.split()) if text else 0

def main():
    print(f"Python version: {platform.python_version()}")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Machine: {platform.machine()}")
    
    if not check_llamafile():
        return

    prompts = [
        "How do I improve my running speed?",
        "What are the best exercises for building muscle?",
        "How can I lose weight quickly?",
        "What is the best diet for weight loss?"
    ]

    latencies = []
    speeds = []

    for prompt in prompts:
        print(f"Running prompt: {prompt[:30]}...")
        output, latency = run_llamafile(prompt)
        if output is None or latency is None:
            continue
        
        tokens = count_tokens(output)
        speed = tokens / latency if latency > 0 else 0

        latencies.append(latency)
        speeds.append(speed)

        print(f"Latency: {latency:.2f} seconds")
        print(f"Speed: {speed:.2f} tokens/second")
        print(f"Output: {output[:100]}...")  # Print first 100 characters of output
        print("-" * 50)

    if latencies and speeds:
        avg_latency = statistics.mean(latencies)
        avg_speed = statistics.mean(speeds)

        print(f"Average Latency: {avg_latency:.2f} seconds")
        print(f"Average Speed: {avg_speed:.2f} tokens/second")
    else:
        print("No successful runs to calculate averages.")

if __name__ == "__main__":
    main()