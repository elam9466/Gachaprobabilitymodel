import math
import random
from collections import Counter


def average(values):
    """Calculate the arithmetic mean of a list of numbers."""
    if not values:
        return 0
    return sum(values) / len(values)


def median(values):
    """Calculate the median of a list of numbers."""
    if not values:
        return 0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
    return sorted_vals[mid]


def gachaModel(
    currency: int,
    cost: int,
    rate: float,
    seed: int,
    featuredRate: float = None,
    checkExternal=None,
    custom_rate_calculator=None
):
    if currency < cost:
        print("Not enough currency to pull.")
        return None

    random.seed(seed)

    rolls = currency // cost
    pulls = []
    successes = 0
    firstHit = None
    featuredSuccesses = 0
    firstFeaturedHit = None
    rollResults = []

    for roll in range(1, rolls + 1):
        # Use custom rate if provided, otherwise fall back to flat base rate
        currentRate = custom_rate_calculator(roll) if custom_rate_calculator else rate

        if random.random() < currentRate:
            successes += 1
            pulls.append(roll)

            if firstHit is None:
                firstHit = roll

            isFeatured = False
            featuredName = None

            if featuredRate is not None:
                if random.random() < featuredRate:
                    isFeatured = True
                    featuredName = "Featured Unit"
                    featuredSuccesses += 1
                    if firstFeaturedHit is None:
                        firstFeaturedHit = roll
                else:
                    featuredName = "Off rate Unit"

            elif checkExternal is not None:
                isFeatured, featuredName = checkExternal(roll)
                if isFeatured:
                    featuredSuccesses += 1
                    if firstFeaturedHit is None:
                        firstFeaturedHit = roll

            rollResults.append({
                "roll": roll,
                "success": True,
                "featured": isFeatured,
                "featured_name": featuredName
            })
        else:
            rollResults.append({
                "roll": roll,
                "success": False,
                "featured": False,
                "featured_name": None
            })

    # Gaps between consecutive SSR hits (used for histogram binning)
    gaps = []
    prev = 0
    for p in pulls:
        gaps.append(p - prev)
        prev = p

    # Bin the gaps — FIX: was `rollResults / 40` (list ÷ int → TypeError),
    # now correctly uses `rolls` (the integer pull count)
    bin_size = max(1, math.floor(rolls / 40))
    bins = {i: 0 for i in range(1, rolls + 1, bin_size)}
    for g in gaps:
        bin_key = ((g - 1) // bin_size) * bin_size + 1
        bins[bin_key] = bins.get(bin_key, 0) + 1

    # Statistics — FIX: this block was unreachable dead code because of
    # an early return above it; now everything feeds into a single return
    empMean = average(pulls) if successes > 0 else 0
    empMedian = median(pulls) if successes > 0 else 0
    theoMean = 1 / rate if rate > 0 else 0
    theoVariance = (1 - rate) / (rate ** 2) if rate > 0 else 0
    empSuccessRate = successes / rolls if rolls > 0 else 0
    featuredRateEmp = featuredSuccesses / successes if successes > 0 else 0

    pmf = {k: ((1 - rate) ** (k - 1)) * rate for k in range(1, rolls + 1)}
    cdf = {k: 1 - (1 - rate) ** k for k in range(1, rolls + 1)}

    return {
        "total_rolls": rolls,
        "successes": successes,
        "featured_successes": featuredSuccesses,
        "first_success_at": firstHit,
        "first_featured_at": firstFeaturedHit,
        "success_positions": pulls,
        "featured_positions": [r["roll"] for r in rollResults if r.get("featured")],
        "empirical_mean": empMean,
        "empirical_median": empMedian,
        "theoretical_mean": theoMean,
        "theoretical_variance": theoVariance,
        "empirical_success_rate": empSuccessRate,
        "featured_rate_empirical": featuredRateEmp,
        "pmf": pmf,
        "cdf": cdf,
        "roll_details": rollResults,
        "bins": bins,
        "bin_size": bin_size,
        "gaps": gaps,
    }