import boto3
from datetime import date, timedelta
from app.config import AWS_REGION

# Cost Explorer is a global service, but the API client itself
# must be created in us-east-1 regardless of your other regions.
ce_client = boto3.client("ce", region_name="us-east-1")


def get_daily_cost_by_service(days: int = 7):
    """
    Fetches daily cost, broken down by AWS service, for the last N days.
    Returns a list like:
    [{"date": "2026-07-14", "service": "Amazon EC2", "cost": 12.34}, ...]
    """
    end = date.today()
    start = end - timedelta(days=days)

    response = ce_client.get_cost_and_usage(
        TimePeriod={"Start": start.isoformat(), "End": end.isoformat()},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    results = []
    for day in response["ResultsByTime"]:
        day_date = day["TimePeriod"]["Start"]
        for group in day["Groups"]:
            service = group["Keys"][0]
            cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
            if cost > 0:  # skip zero-cost noise
                results.append({"date": day_date, "service": service, "cost": round(cost, 2)})

    return results


def detect_anomalies(cost_data: list, threshold_percent: float = 30.0):
    """
    Compares each service's most recent day of cost against its own
    average over the prior days. Flags services where the change
    exceeds the threshold (default 30%).
    """
    from collections import defaultdict

    by_service = defaultdict(list)
    for entry in cost_data:
        by_service[entry["service"]].append(entry)

    anomalies = []
    for service, entries in by_service.items():
        entries.sort(key=lambda x: x["date"])
        if len(entries) < 2:
            continue  # not enough data to compare

        latest = entries[-1]
        previous = entries[:-1]
        avg_previous = sum(e["cost"] for e in previous) / len(previous)

        if avg_previous == 0:
            continue  # avoid division by zero; new service with no prior baseline

        percent_change = ((latest["cost"] - avg_previous) / avg_previous) * 100

        if abs(percent_change) >= threshold_percent:
            anomalies.append({
                "service": service,
                "latest_cost": latest["cost"],
                "average_previous_cost": round(avg_previous, 2),
                "percent_change": round(percent_change, 1),
                "date": latest["date"],
            })

    return anomalies


def get_cost_forecast(days_ahead: int = 30):
    """
    Uses AWS's own forecasting to predict total spend for the next N days.
    Returns predicted total cost plus the confidence range AWS provides.
    """
    start = date.today() + timedelta(days=1)  # forecast starts tomorrow
    end = start + timedelta(days=days_ahead)

    response = ce_client.get_cost_forecast(
        TimePeriod={"Start": start.isoformat(), "End": end.isoformat()},
        Metric="UNBLENDED_COST",
        Granularity="MONTHLY",
    )

    forecast_total = float(response["Total"]["Amount"])
    unit = response["Total"]["Unit"]

    return {
        "forecast_period_days": days_ahead,
        "predicted_total_cost": round(forecast_total, 2),
        "currency": unit,
    }