# FlakyRootCause

# Flaky Test Root Cause Category through LLM

## File Structure

```
data: Rust flaky tests dataset and MPFT dataset 
src: Source code
results: Model prediction outputs and evaluation results
```

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