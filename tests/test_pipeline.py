import pytest
import pandas as pd
from src.pipeline import (
    generate_synthetic_data,
    calculate_attribution_scores,
    analyze_user_journeys,
)


def test_generate_synthetic_data(tmp_path):
    output_file = tmp_path / "test_data.csv"
    df = generate_synthetic_data(num_users=10, num_articles=5, output_path=output_file)

    assert not df.empty
    assert output_file.exists()
    assert {"page_name", "page_url", "user_id", "timestamp"}.issubset(df.columns)
    assert df["page_url"].str.contains("/articles/|/register").all()


@pytest.mark.parametrize(
    "journey,method,expected",
    [
        (["/a1", "/a2", "/a3"], "first_touch", {"/a1": 1.0}),
        (["/a1", "/a2", "/a3"], "last_touch", {"/a3": 1.0}),
        (["/a1", "/a2", "/a3"], "linear", {"/a1": 1 / 3, "/a2": 1 / 3, "/a3": 1 / 3}),
        (["/a1", "/a2", "/a3"], "position_based", {"/a1": 0.4, "/a2": 0.2, "/a3": 0.4}),
        (["/a1"], "position_based", {"/a1": 1.0}),
        (["/a1"], "time_decay", {"/a1": 1.0}),
        (
            ["/a1", "/a2", "/a3"],
            "time_decay",
            {"/a1": 1 / 7, "/a2": 2 / 7, "/a3": 4 / 7},
        ),
        ([], "linear", {}),
    ],
)
def test_calculate_attribution_scores(journey, method, expected):
    result = calculate_attribution_scores(journey, method)
    assert result == expected


def test_analyze_user_journeys(tmp_path):
    df = pd.DataFrame(
        [
            {
                "page_name": "article1",
                "page_url": "/articles/article1",
                "user_id": "u1",
                "timestamp": "2024-01-01 10:00:00",
            },
            {
                "page_name": "article2",
                "page_url": "/articles/article2",
                "user_id": "u1",
                "timestamp": "2024-01-01 10:05:00",
            },
            {
                "page_name": "Register",
                "page_url": "/register",
                "user_id": "u1",
                "timestamp": "2024-01-01 10:10:00",
            },
        ]
    )
    path = tmp_path / "hitlog.csv"
    df.to_csv(path, index=False)

    result = analyze_user_journeys(path, attribution_method="linear")

    assert not result.empty
    assert {"page_name", "page_url", "total"}.issubset(result.columns)
    assert all(url.startswith("/articles/") for url in result["page_url"])

    # Assert the total attribution adds up to 1.0 for this journey
    total_score = result["total"].sum()
    assert abs(total_score - 1.0) < 0.0001
