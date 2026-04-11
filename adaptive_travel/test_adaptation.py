r"""
Test Suite for Scoring-Based Adaptation Engine

Run from terminal:
    c:\Users\SK\OneDrive\Desktop\smart_tourism\venv\bin\python test_adaptation.py
"""

import json
from services.adaptation_engine import AdaptationEngine


def load_attractions():
    """Load attractions from JSON"""
    with open('attractions.json', 'r') as f:
        return json.load(f)['attractions']


def test_case_1_basic_scoring():
    """Test Case 1: Basic scoring with clear weather and low crowds"""
    print("\n" + "="*70)
    print("TEST CASE 1: Basic Scoring (Clear Weather, Low Crowds, Good AQI)")
    print("="*70)
    
    engine = AdaptationEngine()
    engine.set_conditions(
        weather_raining=False,
        crowd_level='low',
        aqi_level=80
    )
    
    attractions = load_attractions()
    selected = [a for a in attractions if a['id'] in [1, 4, 5]]  # City Palace, Museum, Temple
    
    result = engine.adapt_itinerary(selected)
    
    print("\nSelected Attractions:")
    for attr in result['original_plan']:
        print(f"  - {attr['name']}")
    
    print("\nAdapted Plan (Reordered by Score):")
    for idx, attr in enumerate(result['adapted_plan'], 1):
        score = result['scoring_details'][attr['name']]
        final_score = score['base'] + score['adjustments']
        print(f"  {idx}. {attr['name']} (Score: {final_score})")
    
    print(f"\nEnergy: {result['total_energy_used']}/100 used, {result['energy_remaining']} remaining")
    print("\nExplanations:")
    for expl in result['explanations']:
        print(f"  • {expl}")
    
    return result


def test_case_2_rain_impact():
    """Test Case 2: Rain impact on outdoor activities"""
    print("\n" + "="*70)
    print("TEST CASE 2: Rain Impact (Raining, Low Crowds, Good AQI)")
    print("="*70)
    
    engine = AdaptationEngine()
    engine.set_conditions(
        weather_raining=True,
        crowd_level='low',
        aqi_level=80
    )
    
    attractions = load_attractions()
    selected = [a for a in attractions if a['id'] in [1, 3, 4, 6]]  # Mix of outdoor/indoor
    
    result = engine.adapt_itinerary(selected)
    
    print("\nSelected Attractions:")
    for attr in result['original_plan']:
        print(f"  - {attr['name']} (type: {attr['type']})")
    
    print("\nAdapted Plan (Reordered - Indoor FIRST due to rain):")
    for idx, attr in enumerate(result['adapted_plan'], 1):
        score = result['scoring_details'][attr['name']]
        final_score = score['base'] + score['adjustments']
        print(f"  {idx}. {attr['name']} ({attr['type']}) - Score: {final_score}")
    
    print(f"\nEnergy: {result['total_energy_used']}/100 used, {result['energy_remaining']} remaining")
    print("\nKey Insight: Indoor attraction (Museum) should rank higher than outdoor ones")
    
    return result


def test_case_3_high_aqi():
    """Test Case 3: High AQI impact on pollution-sensitive activities"""
    print("\n" + "="*70)
    print("TEST CASE 3: High AQI Impact (Clear, Low Crowds, AQI 250)")
    print("="*70)
    
    engine = AdaptationEngine()
    engine.set_conditions(
        weather_raining=False,
        crowd_level='low',
        aqi_level=250  # Poor air quality
    )
    
    attractions = load_attractions()
    selected = [a for a in attractions if a['id'] in [1, 3, 9, 4, 8]]  # High sensitivity + museum
    
    result = engine.adapt_itinerary(selected)
    
    print("\nSelected Attractions:")
    for attr in result['original_plan']:
        sensitivity = attr.get('pollution_sensitivity', 'unknown')
        print(f"  - {attr['name']} (type: {attr['type']}, sensitivity: {sensitivity})")
    
    print("\nAdapted Plan (Indoor/Low-Sensitivity FIRST):")
    for idx, attr in enumerate(result['adapted_plan'], 1):
        score = result['scoring_details'][attr['name']]
        final_score = score['base'] + score['adjustments']
        sensitivity = attr.get('pollution_sensitivity', 'unknown')
        print(f"  {idx}. {attr['name']} - Score: {final_score} (sensitivity: {sensitivity})")
    
    print(f"\nEnergy: {result['total_energy_used']}/100 used, {result['energy_remaining']} remaining")
    print("\nKey Insight: Pollution-sensitive outlooks should be penalized heavily")
    print("Museums and galleries (indoor) score much higher")
    
    return result


def test_case_4_high_crowds():
    """Test Case 4: High crowd impact on popular attractions"""
    print("\n" + "="*70)
    print("TEST CASE 4: High Crowds Impact (Clear, High Crowds, Good AQI)")
    print("="*70)
    
    engine = AdaptationEngine()
    engine.set_conditions(
        weather_raining=False,
        crowd_level='high',
        aqi_level=80
    )
    
    attractions = load_attractions()
    selected = [a for a in attractions if a['id'] in [1, 2, 3, 9, 6, 7]]  # Mix of high/low popularity
    
    result = engine.adapt_itinerary(selected)
    
    print("\nSelected Attractions:")
    for attr in result['original_plan']:
        print(f"  - {attr['name']} (popularity: {attr['popularity']})")
    
    print("\nAdapted Plan (Low-Popularity FIRST to avoid crowds):")
    for idx, attr in enumerate(result['adapted_plan'], 1):
        score = result['scoring_details'][attr['name']]
        final_score = score['base'] + score['adjustments']
        print(f"  {idx}. {attr['name']} - Score: {final_score} (popularity: {attr['popularity']})")
    
    print(f"\nEnergy: {result['total_energy_used']}/100 used, {result['energy_remaining']} remaining")
    print("\nKey Insight: Low-popularity attractions like Sisodia Rani Garden")
    print("get boost in rankings when crowds are high")
    
    return result


def test_case_5_energy_limit():
    """Test Case 5: Energy constraint - removing high-cost activities"""
    print("\n" + "="*70)
    print("TEST CASE 5: Energy Limit (All 10 Attractions Selected)")
    print("="*70)
    
    engine = AdaptationEngine()
    engine.set_conditions(
        weather_raining=False,
        crowd_level='low',
        aqi_level=100
    )
    
    attractions = load_attractions()
    
    print(f"\nTotal Attractions: {len(attractions)}")
    print("Energy Costs:")
    
    total_cost = 0
    for attr in attractions:
        cost = attr['base_energy_cost']
        total_cost += cost
        print(f"  - {attr['name']}: {cost} points")
    
    print(f"\nTotal Energy Needed: {total_cost} points")
    print(f"Available Energy: 100 points")
    print(f"Deficit: {total_cost - 100} points")
    
    result = engine.adapt_itinerary(attractions)
    
    print(f"\nRemoved Attractions ({len(result['removed_attractions'])}): ")
    for attr in result['removed_attractions']:
        print(f"  ❌ {attr['name']} (cost: {attr['base_energy_cost']})")
    
    print(f"\nFinal Plan ({len(result['adapted_plan'])} attractions):")
    for idx, attr in enumerate(result['adapted_plan'], 1):
        print(f"  {idx}. {attr['name']} (cost: {attr['base_energy_cost']})")
    
    print(f"\nEnergy: {result['total_energy_used']}/100 used, {result['energy_remaining']} remaining")
    print("\nExplanations:")
    for expl in result['explanations']:
        print(f"  • {expl}")
    
    return result


def test_case_6_perfect_storm():
    """Test Case 6: Combined stress test (Rain + High Crowds + High AQI + Energy Limit)"""
    print("\n" + "="*70)
    print("TEST CASE 6: Perfect Storm (Rain + High Crowds + AQI 280 + 6 Attractions)")
    print("="*70)
    
    engine = AdaptationEngine()
    engine.set_conditions(
        weather_raining=True,
        crowd_level='high',
        aqi_level=280  # Very Poor
    )
    
    attractions = load_attractions()
    selected = [a for a in attractions if a['id'] in [1, 2, 3, 9, 10, 4]]
    
    result = engine.adapt_itinerary(selected)
    
    print("\nSelected Attractions:")
    for attr in result['original_plan']:
        print(f"  - {attr['name']} (type: {attr['type']}, popularity: {attr['popularity']})")
    
    print("\nAdapted Plan (After ALL Adjustments):")
    for idx, attr in enumerate(result['adapted_plan'], 1):
        score = result['scoring_details'][attr['name']]
        final_score = score['base'] + score['adjustments']
        print(f"  {idx}. {attr['name']} - Score: {final_score}")
    
    if result['removed_attractions']:
        print(f"\nRemoved Attractions: {len(result['removed_attractions'])}")
        for attr in result['removed_attractions']:
            print(f"  ❌ {attr['name']} (reason: energy constraints)")
    
    print(f"\nEnergy: {result['total_energy_used']}/100 used, {result['energy_remaining']} remaining")
    print("\nExplanations:")
    for expl in result['explanations']:
        print(f"  • {expl}")
    
    print("\nExpected Result:")
    print("  ✓ Heavy penalties on all outdoor/high-popularity attractions")
    print("  ✓ Museums and galleries move to front")
    print("  ✓ Low-popularity attractions prioritized")
    print("  ✓ Possibly some removal due to energy limits")
    
    return result


def print_scoring_summary(result):
    """Print a summary of all scores"""
    print("\n" + "-"*70)
    print("SCORING SUMMARY")
    print("-"*70)
    
    scores = [
        (name, details['base'] + details['adjustments'])
        for name, details in result['scoring_details'].items()
    ]
    scores.sort(key=lambda x: x[1], reverse=True)
    
    print("\nAll Attractions Ranked by Final Score:")
    for name, final_score in scores:
        details = result['scoring_details'][name]
        print(f"\n  {name}")
        print(f"    Base: {details['base']}")
        print(f"    Adjustments: {details['adjustments']}")
        print(f"    Final: {final_score}")
        if details['reasons']:
            print(f"    Reasons: {', '.join(details['reasons'])}")


def run_all_tests():
    """Run all test cases"""
    print("\n" + "#"*70)
    print("# SCORING-BASED ADAPTATION ENGINE - TEST SUITE")
    print("#"*70)
    
    test_case_1_basic_scoring()
    test_case_2_rain_impact()
    test_case_3_high_aqi()
    test_case_4_high_crowds()
    test_case_5_energy_limit()
    test_case_6_perfect_storm()
    
    print("\n" + "#"*70)
    print("# ALL TESTS COMPLETED")
    print("#"*70 + "\n")


if __name__ == '__main__':
    run_all_tests()
