import argparse
from .core import read_cells, analyze, save_csv, save_geojson


def main():
    parser = argparse.ArgumentParser(description="Educational grid flood-risk screening (not a flood model)")
    parser.add_argument("--input", default="data/sample_cells.csv")
    parser.add_argument("--output", default="outputs/risk_results.csv")
    parser.add_argument("--geojson", default="outputs/risk_points.geojson")
    args = parser.parse_args()
    result = analyze(read_cells(args.input))
    save_csv(result, args.output)
    save_geojson(result, args.geojson)
    print(f"Analyzed {len(result)} cells; CSV: {args.output}; GeoJSON: {args.geojson}")
    for level in ("low", "medium", "high"):
        print(f"{level}: {sum(r['risk_class'] == level for r in result)}")


if __name__ == "__main__":
    main()
