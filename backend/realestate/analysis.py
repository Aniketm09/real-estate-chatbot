from typing import List, Dict
import pandas as pd
from .utils import get_dataset
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables (works locally, harmless on Render)
load_dotenv()

# Column constants
LOCATION_COL = "final_location"
YEAR_COL = "year"


# ------------------------------
# OpenAI Client (SAFE INITIALIZATION)
# ------------------------------

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")

    print("OPENAI_API_KEY exists:", bool(api_key))

    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment variables")

    return OpenAI(api_key=api_key)


# ------------------------------
# Helper column finders
# ------------------------------

def _flat_rate_col(df: pd.DataFrame) -> str | None:
    for c in df.columns:
        if "flat" in c.lower() and "weighted" in c.lower():
            return c
    return None


def _demand_col(df: pd.DataFrame) -> str | None:
    for c in df.columns:
        if "demand" in c.lower() or "total_sales" in c.lower():
            return c
    return None


# ------------------------------
# Query type detector
# ------------------------------

def detect_query_type(message: str) -> str:
    text = message.lower()

    if "compare" in text or "vs" in text:
        return "compare"

    if "price" in text and "growth" in text:
        return "price_growth"

    if "demand" in text or "trend" in text:
        return "demand_trend"

    return "single_area"


# ------------------------------
# Extract locations from message
# ------------------------------

def extract_locations(message: str, df: pd.DataFrame) -> List[str]:
    text = message.lower()

    locations = df[LOCATION_COL].dropna().unique()

    found = []

    for loc in locations:
        loc_str = str(loc)

        if loc_str.lower() in text:
            found.append(loc_str)

    # remove duplicates, preserve order
    return list(dict.fromkeys(found))


# ------------------------------
# LLM Summaries (SAFE)
# ------------------------------

def llm_summary(system_prompt: str, user_prompt: str) -> str | None:
    try:
        client = get_openai_client()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=200
        )

        return response.choices[0].message.content

    except Exception as e:
        print("LLM error → fallback summary:", str(e))
        return None


# ------------------------------
# Summary Functions
# ------------------------------

def summary_single(area: str, df: pd.DataFrame) -> str:

    area_df = df[df[LOCATION_COL] == area].sort_values(YEAR_COL)

    if area_df.empty:
        return f"I don't have data for {area}."

    user_prompt = f"""
    Give a short real-estate analysis for locality '{area}' based on:
    {area_df.to_dict(orient='records')}
    """

    llm = llm_summary(
        "You are a real estate analyst.",
        user_prompt
    )

    if llm:
        return llm

    # fallback
    flat_col = _flat_rate_col(df)
    demand_col = _demand_col(df)

    years = area_df[YEAR_COL].tolist()

    parts = [
        f"Analysis for {area} from {years[0]} to {years[-1]}:"
    ]

    if flat_col and flat_col in area_df.columns:

        start_rate = round(area_df[flat_col].iloc[0])
        end_rate = round(area_df[flat_col].iloc[-1])

        trend = (
            "increased"
            if end_rate > start_rate
            else "decreased"
            if end_rate < start_rate
            else "remained stable"
        )

        parts.append(
            f"Prices have {trend} from {start_rate} to {end_rate}."
        )

    if demand_col and demand_col in area_df.columns:

        start_d = round(area_df[demand_col].iloc[0])
        end_d = round(area_df[demand_col].iloc[-1])

        parts.append(
            f"Demand changed from {start_d} to {end_d}."
        )

    return " ".join(parts)


def summary_compare(areas: List[str], df: pd.DataFrame) -> str:

    if len(areas) < 2:
        return "I need at least two locations to compare."

    area_data = {}

    for area in areas:
        area_data[area] = df[
            df[LOCATION_COL] == area
        ].to_dict(orient="records")

    user_prompt = f"""
    Compare real-estate data for these areas:
    {area_data}
    """

    llm = llm_summary(
        "You are a real estate comparison expert.",
        user_prompt
    )

    if llm:
        return llm

    # fallback
    flat_col = _flat_rate_col(df)

    last_year = df[YEAR_COL].max()

    snippets = []

    for area in areas:

        row = df[
            (df[LOCATION_COL] == area)
            & (df[YEAR_COL] == last_year)
        ]

        if not row.empty and flat_col in row.columns:

            snippets.append(
                f"{area}: ~{round(row[flat_col].iloc[0])}"
            )

    return " | ".join(snippets) if snippets else "No comparable data found."


def summary_price_growth(area: str, df: pd.DataFrame) -> str:

    area_df = df[
        df[LOCATION_COL] == area
    ].sort_values(YEAR_COL).tail(4)

    if area_df.empty:
        return f"No price data for {area}."

    user_prompt = f"""
    Analyze the price growth trend for {area} using:
    {area_df.to_dict(orient='records')}
    """

    llm = llm_summary(
        "You are a real estate analyst.",
        user_prompt
    )

    if llm:
        return llm

    flat_col = _flat_rate_col(df)

    if not flat_col:
        return "Price column not found."

    years = area_df[YEAR_COL].tolist()

    prices = area_df[flat_col].tolist()

    return (
        f"Price growth for {area}: "
        + ", ".join(
            [f"{y}: {p}" for y, p in zip(years, prices)]
        )
    )


def summary_demand_trend(area: str, df: pd.DataFrame) -> str:

    area_df = df[
        df[LOCATION_COL] == area
    ].sort_values(YEAR_COL)

    if area_df.empty:
        return f"No demand data for {area}."

    demand_col = _demand_col(df)

    if not demand_col:
        return "Demand column not found."

    user_prompt = f"""
    Analyze demand trend for {area} using:
    {area_df.to_dict(orient='records')}
    """

    llm = llm_summary(
        "You are a demand trend analyst.",
        user_prompt
    )

    if llm:
        return llm

    start = round(area_df[demand_col].iloc[0])
    end = round(area_df[demand_col].iloc[-1])

    trend = (
        "increased"
        if end > start
        else "decreased"
        if end < start
        else "remained stable"
    )

    return f"Demand for {area} has {trend}."


# ------------------------------
# Chart data
# ------------------------------

def chart_data_for_area(area: str, df: pd.DataFrame) -> Dict:

    area_df = df[
        df[LOCATION_COL] == area
    ].sort_values(YEAR_COL)

    labels = area_df[YEAR_COL].tolist()

    flat_col = _flat_rate_col(df)
    demand_col = _demand_col(df)

    datasets = []

    if flat_col and flat_col in area_df.columns:

        datasets.append(
            {
                "label": "Average Price",
                "data": area_df[flat_col].tolist(),
            }
        )

    if demand_col and demand_col in area_df.columns:

        datasets.append(
            {
                "label": "Demand",
                "data": area_df[demand_col].tolist(),
            }
        )

    return {
        "labels": labels,
        "datasets": datasets,
    }


# ------------------------------
# Table data
# ------------------------------

def table_data_for_area(area: str, df: pd.DataFrame) -> List[Dict]:

    area_df = df[
        df[LOCATION_COL] == area
    ].sort_values(YEAR_COL)

    selected_cols = [
        YEAR_COL,
        "city",
        LOCATION_COL,
    ]

    flat = _flat_rate_col(df)
    demand = _demand_col(df)

    if flat:
        selected_cols.append(flat)

    if demand:
        selected_cols.append(demand)

    selected_cols = [
        c for c in selected_cols
        if c in area_df.columns
    ]

    return area_df[selected_cols].to_dict(orient="records")