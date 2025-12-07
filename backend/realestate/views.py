from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
import pandas as pd

from .utils import get_dataset
from .analysis import (
    detect_query_type,
    extract_locations,
    summary_single,
    summary_compare,
    summary_price_growth,
    summary_demand_trend,
    chart_data_for_area,
    table_data_for_area,
)


# ------------------------------
# MAIN CHATBOT ENDPOINT
# ------------------------------

@api_view(["POST"])
def analyze_query(request):
    try:
        message = request.data.get("message", "")
        if not message.strip():
            return Response({"error": "Message text is required"}, status=400)

        # Load dataset once per request
        df = get_dataset()

        # Extract location names from user query
        locations = extract_locations(message, df)
        query_type = detect_query_type(message)

        if not locations and query_type != "compare":
            return Response({
                "error": "No matching location found in dataset.",
                "locations_available": df["final_location"].unique().tolist()
            }, status=404)

        # Generate summary based on query type
        if query_type == "single_area":
            area = locations[0]
            summary = summary_single(area, df)
            chart = chart_data_for_area(area, df)
            table = table_data_for_area(area, df)

        elif query_type == "compare":
            summary = summary_compare(locations, df)
            chart = {"labels": [], "datasets": []}
            table = []

        elif query_type == "price_growth":
            area = locations[0]
            summary = summary_price_growth(area, df)
            chart = chart_data_for_area(area, df)
            table = table_data_for_area(area, df)

        elif query_type == "demand_trend":
            area = locations[0]
            summary = summary_demand_trend(area, df)
            chart = chart_data_for_area(area, df)
            table = table_data_for_area(area, df)

        else:
            summary = "I could not understand query type."
            chart = {}
            table = []

        return Response({
            "queryType": query_type,
            "locations": locations,
            "summary": summary,
            "chartData": chart,
            "tableData": table,
        })

    except Exception as e:
        return Response({"error": f"Internal Server Error: {e}"}, status=500)


# ------------------------------
# DOWNLOAD DATA ENDPOINT (Bonus)
# ------------------------------

@api_view(["GET"])
def download_data(request):
    """
    Download filtered data for a specific area as CSV.
    Example: /api/download/?area=Wakad
    """
    try:
        area = request.GET.get("area")
        if not area:
            return Response({"error": "area query parameter is required"}, status=400)

        df = get_dataset()
        filtered = df[df["final_location"].str.lower() == area.lower()]

        if filtered.empty:
            return Response({"error": f"No data found for {area}"}, status=404)

        # Convert to CSV
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{area}_data.csv"'
        filtered.to_csv(response, index=False)

        return response

    except Exception as e:
        return Response({"error": str(e)}, status=500)
