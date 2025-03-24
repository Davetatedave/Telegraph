"""Pipeline for analyzing user journeys and article influence."""

import pandas as pd
from typing import Dict, List, Optional, Union
from pathlib import Path
import random
from datetime import datetime, timedelta


def generate_synthetic_data(
    num_users: int = 1000,
    num_articles: int = 50,
    max_articles_per_journey: int = 5,
    registration_rate: float = 0.3,
    output_path: Optional[Union[str, Path]] = None,
) -> pd.DataFrame:
    """
    Generate synthetic hitlog data for testing and development.

    Args:
        num_users: Number of users to generate
        num_articles: Number of articles to generate
        max_articles_per_journey: Maximum articles per user journey
        registration_rate: Probability of user registration
        output_path: Optional path to save the generated data

    Returns:
        DataFrame containing the generated data
    """
    # Generate article URLs
    articles = [f"/articles/article{i}" for i in range(1, num_articles + 1)]

    # Generate data
    data = []
    base_timestamp = datetime(2024, 3, 21, 10, 0, 0)

    for user_id in range(1, num_users + 1):
        user_id = f"user{user_id}"
        timestamp = base_timestamp + timedelta(hours=random.randint(0, 24))

        # Generate journey
        num_articles = random.randint(1, max_articles_per_journey)
        journey = random.sample(articles, num_articles)

        # Add articles to journey
        for article in journey:
            data.append(
                {
                    "page_name": article.split("/")[-1],
                    "page_url": article,
                    "user_id": user_id,
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
            timestamp += timedelta(minutes=random.randint(1, 5))

        # Add registration if user converts
        if random.random() < registration_rate:
            data.append(
                {
                    "page_name": "Register",
                    "page_url": "/register",
                    "user_id": user_id,
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

    # Create DataFrame
    df = pd.DataFrame(data)

    # Save to file if path provided
    if output_path:
        df.to_csv(output_path, index=False)

    return df


def calculate_attribution_scores(journey: List[str], method: str) -> Dict[str, float]:
    """
    Calculate attribution scores for a journey using the specified method.

    Args:
        journey: List of article URLs in the journey
        method: Attribution method to use ("first_touch", "last_touch", "linear", "position_based", "time_decay")

    Returns:
        Dictionary mapping article URLs to their scores
    """
    if not journey:
        return {}

    scores = {}

    if method == "count":
        for article in journey:
            scores[article] = 1.0
    elif method == "first_touch":
        scores[journey[0]] = 1.0
    elif method == "last_touch":
        scores[journey[-1]] = 1.0
    elif method == "linear":
        score = 1.0 / len(journey)
        for article in journey:
            scores[article] = score
    elif method == "position_based":
        if len(journey) == 1:
            scores[journey[0]] = 1.0  # Single article gets full credit
        else:
            for i, article in enumerate(journey):
                if i == 0:  # First position
                    scores[article] = 0.4
                elif i == len(journey) - 1:  # Last position
                    scores[article] = 0.4
                else:  # Middle positions
                    scores[article] = 0.2
    elif method == "time_decay":
        if len(journey) == 1:
            scores[journey[0]] = 1.0  # Single article gets full credit
        else:
            # Calculate decay factor based on position
            # Later positions get exponentially more credit
            total_weight = sum(2**i for i in range(len(journey)))
            for i, article in enumerate(journey):
                # Earlier articles get less credit
                scores[article] = 2**i / total_weight

    return scores


def analyze_user_journeys(
    input_path: Union[str, Path], attribution_method: str = "count"
) -> pd.DataFrame:
    """
    Analyze user journeys and calculate article influence scores.

    Args:
        input_path: Path to the hitlog CSV file
        attribution_method: Method to use for attribution
        top_n: Number of top articles to return

    Returns:
        DataFrame with article influence scores
    """
    # Load and preprocess data
    df = pd.read_csv(input_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Extract user journeys
    journeys = {}

    # Process each user's data separately
    for user_id in df["user_id"].unique():
        # Get all data for this user, sorted by timestamp
        user_data = df[df["user_id"] == user_id].sort_values("timestamp")

        # Check if user has a registration event
        has_registration = "/register" in user_data["page_url"].values
        if not has_registration:
            continue

        # Find the first registration event
        registration_index = user_data[user_data["page_url"] == "/register"].index[0]

        # Get all articles that appear before registration
        articles_before_registration = user_data.loc[
            : registration_index - 1, "page_url"
        ].tolist()

        # Only include the journey if there are articles before registration
        if articles_before_registration:
            journeys[user_id] = articles_before_registration

    # Calculate scores based on attribution method
    article_scores = {}
    for journey in journeys.values():
        journey_scores = calculate_attribution_scores(journey, attribution_method)
        for article, score in journey_scores.items():
            article_scores[article] = article_scores.get(article, 0) + score

    # Create results DataFrame
    results = []
    for url, score in article_scores.items():
        if url.startswith("/articles/"):
            article_name = url.split("/")[-1]
            results.append({"page_name": article_name, "page_url": url, "total": score})

    # Return empty DataFrame if no results
    if not results:
        return pd.DataFrame(columns=["page_name", "page_url", "total"])

    # Sort and return top N results
    results_df = pd.DataFrame(results)
    return results_df.sort_values("total", ascending=False)


if __name__ == "__main__":
    # Generate synthetic data
    generate_synthetic_data(
        num_users=1000, num_articles=50, output_path="synthetic_hitlog.csv"
    )

    def analysis(attribution_method="count", dir="synthetic_hitlog.csv", top=3):
        # Analyze the data
        results = analyze_user_journeys(dir, attribution_method)
        topN = results.head(top)

        print(f"\nTop {top} influential articles using {attribution_method}:")
        print(topN)
        topN.to_csv("influential_articles.csv", index=False)

    analysis()
