import geometric
import app

if __name__ == "__main__":
    # Quick demo of the gacha model
    print("Running geometric.py demo...\n")
    result = geometric.gachaModel(currency=300, cost=3, rate=0.01, seed=42)
    if result:
        print(f"  Total rolls: {result['total_rolls']}")
        print(f"  Successes:   {result['successes']}")
        print(f"  Mean pull:   {result['empirical_mean']}")
        print(f"  Median pull: {result['empirical_median']}")
    print()

    # Start the Flask web server (blocks until stopped)
    print("Starting Flask server on http://localhost:5001 ...\n")
    app.app.run(host="0.0.0.0", port=5001)