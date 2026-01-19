INPUTS=("FlakyRootCause/data/jsons/rust_jsons" "FlakyRootCause/data/jsons/mpft_jsons")
MODELS=("gpt-4-turbo" "gpt-5")

echo START $(date +%Y-%m-%d)
GIT_SHA=$(git rev-parse HEAD)
echo "Current commit SHA: $GIT_SHA"


DIR_WITH="results/results_with_patch"
DIR_NO="results/results_no_patch"

mkdir -p "$DIR_WITH" "$DIR_NO"

for INPUT in "${INPUTS[@]}"; do
  for MODEL in "${MODELS[@]}"; do
    BASE_NAME=$(basename "$INPUT" .json)
    SAVE_PATH_WITH="${DIR_WITH}/root_cause_eval_${BASE_NAME}_${MODEL}.jsonl"
    SAVE_PATH_NO="${DIR_NO}/root_cause_eval_${BASE_NAME}_${MODEL}.jsonl"

    echo "---------------------------------------------"
    echo "INPUT: $INPUT"
    echo "MODEL: $MODEL"
    echo "WITH PATCH: $SAVE_PATH_WITH"
    echo "NO PATCH: $SAVE_PATH_NO"
    echo "---------------------------------------------"

    python3 src/prompt_model.py \
      --input_json "$INPUT" \
      --model "$MODEL" \
      --save_path "$SAVE_PATH_WITH"

    # Run without patch
    python3 src/prompt_model.py \
      --input_json "$INPUT" \
      --model "$MODEL" \
      --save_path "$SAVE_PATH_NO" \
      --no_patch
  done
done

echo END $(date +%Y-%m-%d)