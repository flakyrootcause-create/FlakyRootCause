import argparse
import os
import json
import openai 
from tqdm import tqdm

openai.api_key = os.getenv("OPENAI_API_KEY")

# ROOT_CAUSE_OPTIONS = [
#     "Logic", "Randomness", "Network", "Async wait", "Concurrency",
#     "Time", "I/O", "Unordered collections", "Environment"
# ]
# ROOT_CAUSE_OPTIONS = ['Test order dependency', 'Time', 'Resource leak', 
#                       'Network', 'Unordered collections', 'Async wait', 
#                       'Concurrency', 'Floating point operations', 
#                       'Randomness', 'OS', 'I/O']

ROOT_CAUSE_OPTIONS = {
    "Test order dependency": "The test outcome depends on the order in which the tests are run.",
    "Async wait": "The test execution makes an asynchronous call and does not properly wait for the result of the call to become available before using it.",
    "Concurrency": "The test non-determinism is due to diﬀerent threads interacting in a non-desirable manner (but not due to asynchronous calls from the Async Wait category), e.g., due to data races, atomicity violations, or deadlocks.",
    "Resource leak": "A resource leak occurs whenever the application does not properly manage (acquire or release) one or more of its resources, e.g., memory allocations or database connections, leading to intermittent test failures.",
    "Network": "Tests whose execution depends on network can be flaky because the network is a resource that is hard to control, e.g., due to remote connection failures or local bad socket management.",
    "Time": "Tests that depend on system time or platform time can fail non-deterministically due to time zone changes, precision of time reported, or other time-related issues.",
    "I/O": "I/O operations can introduce flakiness when resources like files are not properly managed.",
    "Randomness": "The use of random objects can make some tests flaky.",
    "Floating point operations": "Dealing with floating point operations can lead to non-determinism.",
    "Unordered collections": "Tests that assume a specific order in unordered collections can be flaky.",
    "OS": "Tests can be flaky due to operating system-level issues, such as dependencies on specific system types or configurations.",
    "Environment": "Tests that depend on specific environment (such as third-party libraries).",
    "Logic": "Tests that have inherent logical issues leading to non-deterministic outcomes, such as off-by-one errors or deserialization issues."
}


def load_json_files(folder):
    for file in os.listdir(folder):
        if file.endswith(".json"):
            with open(os.path.join(folder, file), "r") as f:
                yield json.load(f)

def build_prompt(issue_description, patch, include_patch=True):
    if include_patch:
        return f"""You are an expert in flaky tests. Given the issue description and code patch below, classify the root cause of flaky tests into one of the following categories:

{ROOT_CAUSE_OPTIONS}

Respond only with the exact category name.

### Issue Description:
{issue_description}

### Code Patch:
{patch}
"""
    else:
        return f"""You are an expert in flaky tests. Given the issue description below, classify the root cause of flaky tests into one of the following categories:

{ROOT_CAUSE_OPTIONS}

Respond only with the exact category name.

### Issue Description:
{issue_description}
"""

def classify_root_cause(prompt, model):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature= 1 if model == "gpt-5" else 0,
        )
        prediction = response.choices[0].message["content"].strip()
        return prediction
    except Exception as e:
        print("OpenAI API error:", e)
        return None

def evaluate(folder, model, save_path, include_patch=True):
    correct = 0
    total = 0

    with open(save_path, "w") as f_out:
        for data in tqdm(load_json_files(folder)):
            gt = data.get("root_cause_category", "")
            if not gt:
                continue
            
            gt = str(gt).strip()
            if gt not in ROOT_CAUSE_OPTIONS:
                continue

            issue = data.get("issue_description", "")
            patch = "\n\n".join(file.get("patch", "") for file in data.get("files_changed", []) if "patch" in file)

            if not issue or (include_patch and not patch):
                continue

            prompt = build_prompt(issue, patch, include_patch)
            predicted = classify_root_cause(prompt, model)

            if not predicted:
                continue

            match = predicted.lower() == gt.lower()
            result = {
                "id": data["id"],
                "ground_truth": gt,
                "predicted": predicted,
                "match": match,
                "prompt": prompt
            }
            f_out.write(json.dumps(result, ensure_ascii=False) + "\n")

            total += 1
            correct += int(match)

    print(f"\nEvaluated {total} examples")
    print(f"Correct predictions: {correct}")
    print(f"Accuracy: {correct / total:.2%}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate root cause classification using LLM.")
    parser.add_argument("--input_json", type=str, required=True, help="Directory containing input JSON files")
    parser.add_argument("--model", type=str, default="gpt-4")
    parser.add_argument("--save_path", type=str, default="root_cause_eval_full.jsonl")
    parser.add_argument("--no_patch", action="store_true", help="Exclude code patch from the prompt")

    args = parser.parse_args()
    evaluate(args.input_json, args.model, save_path=args.save_path, include_patch=not args.no_patch)