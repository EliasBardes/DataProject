import pandas as pd
import numpy as np
from pathlib import Path


def create_mock_activity(nb_users: int = 8, days: int = 30, seed: int | None = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    base_users = [
        "user_elias",
        "user_sophie",
        "user_marie",
        "user_thomas",
        "user_luc",
        "user_lea",
        "user_amina",
        "user_nathan",
    ]
    users = base_users[:nb_users]

    start_date = pd.Timestamp("2025-09-01")
    date_range = pd.date_range(start_date, periods=days, freq="D")

    actions = [
        ("post_create", "content"),
        ("comment_reply", "engagement"),
        ("comment_like", "engagement"),
        ("read_article", "content"),
        ("share_post", "collaboration"),
        ("search_query", "navigation"),
        ("join_group", "collaboration"),
        ("upload_file", "content"),
        ("send_message", "communication"),
    ]

    rows = []
    for current_date in date_range:
        active_users = rng.choice(users, size=rng.integers(3, len(users) + 1), replace=False)
        for user in active_users:
            daily_actions = rng.integers(1, 5)
            for _ in range(daily_actions):
                action, category = actions[rng.integers(0, len(actions))]
                time_spent = int(rng.normal(8, 4))
                time_spent = max(time_spent, 1)
                rows.append(
                    {
                        "user_id": user,
                        "date": current_date.date(),
                        "action_type": action,
                        "time_spent_min": time_spent,
                        "category": category,
                    }
                )

    df = pd.DataFrame(rows)
    df.sort_values(["date", "user_id"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def main():
    df = create_mock_activity()
    output_path = Path(__file__).parent / "data_activity.csv"
    df.to_csv(output_path, index=False)
    print(f"Jeu de données généré avec {len(df)} lignes dans {output_path}")


if __name__ == "__main__":
    main()

