"""
AI Clanker Demo - Compare Simple vs AI-Powered Recommendations
Run this to see the difference between rule-based and AI-powered pairing
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.agents.clanker_agent import ClankerAgent
from src.agents.ai_clanker_agent import AIClankerAgent

def compare_recommendations(movie_title: str):
    """Compare simple rule-based vs AI-powered recommendations"""
    
    print(f"\n{'='*80}")
    print(f"🎬 COMPARING RECOMMENDATIONS FOR: {movie_title}")
    print('='*80)
    
    # Simple Agent
    print(f"\n🔧 SIMPLE RULE-BASED AGENT:")
    print("-" * 40)
    
    simple_agent = ClankerAgent()
    simple_result = simple_agent.sync_recommend(movie_title)
    
    if simple_result['success']:
        print(f"🍸 Recommended: {simple_result['cocktail']['name']}")
        print(f"🎯 Mood: {simple_result['mood']}")
        print(f"💭 Explanation: {simple_result['explanation'][:100]}...")
    else:
        print(f"❌ Error: {simple_result['error']}")
    
    # AI Agent
    print(f"\n🤖 AI-POWERED AGENT:")
    print("-" * 40)
    
    try:
        ai_agent = AIClankerAgent()
        ai_result = ai_agent.sync_ai_recommend(movie_title)
        
        if ai_result['success']:
            print(f"🍸 AI Recommended: {ai_result['cocktail']['name']}")
            print(f"🧠 AI Mood Analysis: {ai_result['mood_analysis']}")
            print(f"💭 AI Explanation: {ai_result['explanation']}")
            print(f"🎯 Confidence: {ai_result['pairing_strength']}")
            
            if ai_result['alternatives']:
                print(f"🔄 Alternatives: {', '.join([alt['name'] for alt in ai_result['alternatives']])}")
        else:
            print(f"❌ AI Error: {ai_result['error']}")
            
    except Exception as e:
        print(f"❌ AI Agent Error: {str(e)}")
        print("💡 This might be due to AWS credentials or Bedrock access")

def main():
    """Interactive demo comparing both agents"""
    print("🎬🍸 Welcome to AI Clanker Comparison!")
    print("Compare simple rule-based vs AI-powered cocktail recommendations")
    print("=" * 80)
    
    print("\n✨ Great movies to try:")
    print("- 'Blade Runner 2049' (Sci-fi)")
    print("- 'The Grand Budapest Hotel' (Comedy/Drama)")
    print("- 'Casablanca' (Classic Romance)")
    print("- 'Mad Max: Fury Road' (Action)")
    print("- 'Her' (Drama/Romance/Sci-fi)")
    print("- 'Pulp Fiction' (Crime/Drama)")
    
    while True:
        print("\n" + "-" * 80)
        movie_title = input("\n🎬 Enter a movie title to compare (or 'quit' to exit): ").strip()
        
        if movie_title.lower() in ['quit', 'exit', 'q']:
            print("\n🎉 Thanks for comparing! The AI makes a big difference! 🤖🥂")
            break
        
        if not movie_title:
            print("❌ Please enter a movie title!")
            continue
        
        compare_recommendations(movie_title)

if __name__ == "__main__":
    main()
