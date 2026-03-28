from typing import List, Dict
import pandas as pd
from .utils import get_dataset
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ==============================
# COLUMN CONSTANTS
# ==============================

LOCATION_COL = "final location"
YEAR_COL = "year"


# ==============================
# SAFE ROUND HELPER
# ==============================

def safe_round(value):
    try:
        return round(float(value))
    except:
        return value


# ==============================
# OpenAI Client
# ==============================

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")

    print("OPENAI_API_KEY exists:", bool(api_key))

    if not api_key:
        raise Exception("OPENAI_API_KEY not set")

    return OpenAI(api_key=api_key)


# ==============================
# Helper column finders
# ==============================

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


# ==============================
# Query type detection
# ==============================

def detect_query_type(message: str) -> str:

    text = message.lower()

    if "compare" in text or "vs" in text:
        return "compare"

    if "price" in text and "growth" in text:
        return "price_growth"

    if "demand" in text or "trend" in text:
        return "demand_trend"

    return "single_area"


# ==============================
# Extract locations
# ==============================

def extract_locations(message: str, df: pd.DataFrame) -> List[str]:

    text = message.lower()

    locations = df[LOCATION_COL].dropna().unique()

    found = []

    for loc in locations:
        loc_str = str(loc)
        if loc_str.lower() in text:
            found.append(loc_str)

    return list(dict.fromkeys(found))


# ==============================
# LLM summary
# ==============================

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
        print("LLM fallback:", str(e))
        return None


# ==============================
# SINGLE AREA SUMMARY
# ==============================

def summary_single(area: str, df: pd.DataFrame) -> str:

    area_df = df[df[LOCATION_COL] == area].sort_values(YEAR_COL)

    if area_df.empty:
        return f"No data found for {area}"

    user_prompt = f"""
    Analyze real estate trend for {area}
    Data:
    {area_df.to_dict(orient='records')}
    """

    llm = llm_summary(
        "You are a real estate analyst",
        user_prompt
    )

    if llm:
        return llm

    flat_col = _flat_rate_col(df)
    demand_col = _demand_col(df)

    years = area_df[YEAR_COL].tolist()

    parts = [
        f"Analysis for {area} ({years[0]} to {years[-1]})"
    ]

    if flat_col and flat_col in area_df.columns:

        start = safe_round(area_df[flat_col].iloc[0])
        end = safe_round(area_df[flat_col].iloc[-1])

        trend = (
            "increased"
            if end > start
            else "decreased"
            if end < start
            else "remained stable"
        )

        parts.append(f"Price {trend} from {start} to {end}")

    if demand_col and demand_col in area_df.columns:

        start = safe_round(area_df[demand_col].iloc[0])
        end = safe_round(area_df[demand_col].iloc[-1])

        parts.append(f"Demand changed from {start} to {end}")

    return ". ".join(parts)


# ==============================
# COMPARE SUMMARY
# ==============================

def summary_compare(areas: List[str], df: pd.DataFrame) -> str:

    if len(areas) < 2:
        return "Need at least 2 areas to compare"

    data = {}

    for area in areas:
        data[area] = df[df[LOCATION_COL] == area].to_dict(orient="records")

    llm = llm_summary(
        "You are real estate comparison expert",
        str(data)
    )

    if llm:
        return llm

    flat_col = _flat_rate_col(df)

    last_year = df[YEAR_COL].max()

    parts = []

    for area in areas:

        row = df[
            (df[LOCATION_COL] == area)
            & (df[YEAR_COL] == last_year)
        ]

        if not row.empty and flat_col in row.columns:

            parts.append(
                f"{area}: {safe_round(row[flat_col].iloc[0])}"
            )

    return " | ".join(parts)


# ==============================
# PRICE GROWTH
# ==============================

def summary_price_growth(area: str, df: pd.DataFrame) -> str:

    area_df = df[df[LOCATION_COL] == area].sort_values(YEAR_COL)

    if area_df.empty:
        return "No data found"

    llm = llm_summary(
        "Real estate analyst",
        str(area_df.to_dict(orient="records"))
    )

    if llm:
        return llm

    flat_col = _flat_rate_col(df)

    years = area_df[YEAR_COL].tolist()

    prices = [
        safe_round(p)
        for p in area_df[flat_col].tolist()
    ]

    return ", ".join(
        [f"{y}: {p}" for y, p in zip(years, prices)]
    )


# ==============================
# DEMAND TREND
# ==============================

def summary_demand_trend(area: str, df: pd.DataFrame) -> str:

    area_df = df[df[LOCATION_COL] == area].sort_values(YEAR_COL)

    demand_col = _demand_col(df)

    if area_df.empty or not demand_col:
        return "No demand data"

    llm = llm_summary(
        "Demand analyst",
        str(area_df.to_dict(orient="records"))
    )

    if llm:
        return llm

    start = safe_round(area_df[demand_col].iloc[0])
    end = safe_round(area_df[demand_col].iloc[-1])

    trend = (
        "increased"
        if end > start
        else "decreased"
        if end < start
        else "stable"
    )

    return f"Demand {trend}"


# ==============================
# CHART DATA
# ==============================

def chart_data_for_area(area: str, df: pd.DataFrame) -> Dict:

    area_df = df[df[LOCATION_COL] == area].sort_values(YEAR_COL)

    flat_col = _flat_rate_col(df)
    demand_col = _demand_col(df)

    datasets = []

    if flat_col:
        datasets.append({
            "label": "Price",
            "data": area_df[flat_col].tolist()
        })

    if demand_col:
        datasets.append({
            "label": "Demand",
            "data": area_df[demand_col].tolist()
        })

    return {
        "labels": area_df[YEAR_COL].tolist(),
        "datasets": datasets
    }


# ==============================
# TABLE DATA
# ==============================

def table_data_for_area(area: str, df: pd.DataFrame) -> List[Dict]:

    area_df = df[df[LOCATION_COL] == area].sort_values(YEAR_COL)

    return area_df.to_dict(orient="records")