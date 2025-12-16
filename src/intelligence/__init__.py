import threading
import pandas as pd
from tqdm import tqdm
from ollama import chat

def call_with_timeout(func, timeout, *args, **kwargs):
    """Execute a function in a daemon thread and return (result, error)."""
    result = {}
    error = {}

    def run():
        try:
            result["data"] = func(*args, **kwargs)
        except Exception as e:
            error["exception"] = e

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        return None, TimeoutError(f"Timeout after {timeout} seconds")

    if "exception" in error:
        return None, error["exception"]

    return result.get("data"), None

def call_with_retry_and_timeout(func, timeout, retries, *args, **kwargs):
    """
    Execute a function with timeout and retry.
    Returns (result, error).
    - timeout: timeout per attempt
    - retries: number of additional retries if it fails
    """
    attempt = 0
    last_error = None

    while attempt <= retries:
        result, err = call_with_timeout(func, timeout, *args, **kwargs)

        if err is None:
            return result, None  # success

        last_error = err
        attempt += 1
        print(f"Retrying {attempt}/{retries+1} failed: {err}")

    return None, last_error

def preprocess_text(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Preprocess job description text for filtering. Extract skills required in the column 'ai_skills_required' using an LLM."""
    mask = df["ai_skills_required"].isnull() & df["description"].notnull() & (df["description"] != "")

    for idx, desc in tqdm(df[mask]["description"].items(), total=mask.sum()):

        messages = [
            {
                'role': 'system',
                'content': (
                    'You are a helpful assistant that extracts skills from job descriptions. '
                    'Giving only list separate by comma on one line.\n'
                    'Like this:\n'
                    'Communication, team working, redaction, good attitude, fast learner'
                ),
            },
            {
                'role': 'user',
                'content': (
                    f'Give me a list of skills required for the following job description :\n\n'
                    f'{desc}\n\n'
                    'I want only the list, no other text. And the skills appear as they are in the description. '
                    '10 maximum. separate by commas.'
                ),
            }
        ]

        response, err = call_with_retry_and_timeout(
            chat,
            30,
            2,
            model=cfg["filtering"]["preprocess_model"],
            messages=messages
        )

        if err:
            id = df.loc[idx, "id"]
            print(f"Failure at row {idx} ({id}): {err}")
            df.loc[idx, "ai_skills_required"] = None
            continue

        try:
            skills = response.message.content
            df.loc[idx, "ai_skills_required"] = skills
        except Exception as e:
            print(f"Error processing response at row {idx}: {e}")
            df.loc[idx, "ai_skills_required"] = None

    return df

def compute_distances(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Compute the cosine distances between job skills and reference skills using sentence embeddings. (set as 'ai_score' column)"""
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics import pairwise_distances

    # ai_skills_required must be not null and ai_score must be null
    if  cfg["filtering"].get("force_distance_compute", True):
        mask = df["ai_skills_required"].notnull()
    else:
        mask = df["ai_skills_required"].notnull() & df["ai_score"].isnull()
        
    if mask.sum() == 0:
        print("No new jobs to compute distances for.")
        return df

    print(f"Computing distances for {mask.sum()} jobs...")

    embedding_model = SentenceTransformer(cfg["filtering"]["embedding_model"])
    emb_skills = embedding_model.encode(df.loc[mask,"ai_skills_required"].to_list(), show_progress_bar=True)

    if "skills_description" in cfg["filtering"]:
        reference = cfg["filtering"]["skills_description"]
        emb_reference = embedding_model.encode([reference])
    elif "skills_embedding_path" in cfg["filtering"]:
        import numpy as np
        emb_reference = np.load(cfg["filtering"]["skills_embedding_path"])
    else:
        raise ValueError("Missing 'skills_description' in filtering config.")

    similarities_distance = pairwise_distances(
        emb_reference.reshape(1, -1),
        emb_skills,
        metric="cosine"
    )[0,:]

    df.loc[mask, "ai_score"] = similarities_distance
    return df
