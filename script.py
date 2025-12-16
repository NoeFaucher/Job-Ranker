from jobspy import scrape_jobs
import pandas as pd
import datetime

from src.intelligence import preprocess_text, compute_distances
from src.utils import load_config, parse_arguments
from src.db import init_db, insert_jobs_bulk, get_jobs_by_date, update_jobs_bulk

def process_existing_jobs(db_path, config):
    """Process jobs that are already in the database (text preprocessing and distance calculation)."""
    jobs_db = get_jobs_by_date(datetime.date.today(), db_path)
    print(f"{len(jobs_db)} jobs ready for filtering.")
    
    jobs_db = preprocess_text(jobs_db, config)
    
    jobs_dicts = jobs_db.to_dict(orient="records")
    update_jobs_bulk(jobs_dicts, db_path)

    jobs_db = compute_distances(jobs_db, config)
    
    jobs_dicts = jobs_db.to_dict(orient="records")
    update_jobs_bulk(jobs_dicts, db_path)

    # similarity_threshold = config["filtering"].get("similarity_threshold", 0.25)
    # # Filter jobs based on ai_score (not null and below threshold)
    # mask = (jobs_db["ai_score"].notnull()) & (jobs_db["ai_score"] <= similarity_threshold)
    # jobs_filtered = jobs_db[mask]

    # print(f"{len(jobs_filtered)} jobs after filtering.")

    # jobs_dicts = jobs_filtered.to_dict(orient="records")

    # with open("filterjobs.json", "w") as f:
    #     import json
    #     json.dump(jobs_dicts, f, indent=4)

def scrape(config, db_path):
    search_cfg = config["search"]
    print("Scraping job offers...")
    jobs_db = pd.DataFrame()
    for location in search_cfg["locations"]:
        # scrape jobs for this location
        
        # Use jobspy to scrape jobs
        temp_jobs_db = scrape_jobs(
            site_name=search_cfg["site_name"],
            search_term=search_cfg["search_term"],
            location=location,
            country_indeed=search_cfg["country_indeed"],
            hours_old=search_cfg["hours_old"],

            # Internal settings
            results_wanted=100000,
            linkedin_fetch_description=True,
            verbose=1,
        )
        jobs_db = pd.concat([jobs_db, temp_jobs_db], ignore_index=True)
        print(f" - Location: {location}: {len(temp_jobs_db)} jobs collected.")
    
    mask = jobs_db["description"].notnull() & (jobs_db["description"] != "")
    jobs_db = jobs_db[mask]

    jobs_dicts = jobs_db.to_dict(orient="records")

    print(f"Inserting {len(jobs_dicts)} jobs into SQLite...")
    insert_jobs_bulk(jobs_dicts, db_path)

def main():
    args = parse_arguments()
    
    config = load_config(args)
    db_path = config["database"]["path"]
    init_db(db_path)
    
    if not args.process_only:
        scrape(config, db_path)
        
    process_existing_jobs(db_path, config)
        
if __name__ == "__main__":
    main()
