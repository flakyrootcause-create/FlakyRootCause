# Flaky Test Root Cause Category through LLM

This is the artifact of paper *"Preliminary Results on Evaluating Large Language Models for
Labeling Root Cause Categories of Fixed Flaky Tests"* accepted at FTW 2026.

## File Structure


- `data`: Rust flaky tests dataset (published at FTW 2025); MPFT dataset (introduced in this paper), covering 244 flaky tests in 17 programming languages (Python (67), Java (54), Go (32), TypeScript (25), C++ (16), JavaScript (15), Scala (13), Rust (5), C# (5), Ruby (4), Erlang (2), Svelte (1), SQL (1),
Objective-C (1), Kotlin (1), Dart (1), C (1))
- `src`: Source code
- `results`: Model prediction outputs and evaluation results


## Setup

- Set up github and openai keys
```
export OPENAI_API_KEY=[YOUR KEY]
```
- Install requiremtnes  
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Prompt model 

- Run the following command, output is saved to the `results/` directory:
```
bash -x src/eval.sh
```