"""
Clanker Interactive Demo
Run this to test movie-to-cocktail recommendations interactively
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.agents.clanker_agent import ClankerAgent

def main():
    """Interactive Clanker demo"""
    print("🎬🍸 Welcome to Clanker!")
    print("Get personalized cocktail recommendations for your favorite movies")
    print("=" * 60)
    
    agent = ClankerAgent()
    
    print("\n✨ Examples to try:")
    print("- 'The Grand Budapest Hotel'")
    print("- 'Casablanca'") 
    print("- 'Inception'")
    print("- 'The Godfather'")
    print("- 'Pulp Fiction'")
    print("- 'Her'")
    
    while True:
        print("\n" + "-" * 60)
        movie_title = input("\n🎬 Enter a movie title (or 'quit' to exit): ").strip()
        
        if movie_title.lower() in ['quit', 'exit', 'q']:
            print("\n🎉 Thanks for using Clanker! Cheers! 🥂")
            break
        
        if not movie_title:
            print("❌ Please enter a movie title!")
            continue
        
        print(f"\n🔍 Searching for '{movie_title}'...")
        
        try:
            result = agent.sync_recommend(movie_title)
            
            if result['success']:
                print(f"\n{'='*60}")
                print(f"🎬 MOVIE: {result['movie']['title']} ({result['movie']['year']})")
                print(f"🎭 Genre: {result['movie']['genre']}")
                print(f"🎬 Director: {result['movie']['director']}")
                print(f"⭐ IMDb Rating: {result['movie']['imdb_rating']}")
                print(f"\n📖 Plot: {result['movie']['plot']}")
                
                print(f"\n{'='*60}")
                print(f"🍸 RECOMMENDED COCKTAIL: {result['cocktail']['name']}")
                print(f"🥃 Serve in: {result['cocktail']['glass']}")
                print(f"🏷️ Tags: {', '.join(result['cocktail']['tags'][:3])}")
                
                print(f"\n🧪 INGREDIENTS:")
                for i, ingredient in enumerate(result['cocktail']['ingredients'][:5], 1):
                    print(f"   {i}. {ingredient}")
                if len(result['cocktail']['ingredients']) > 5:
                    print(f"   ... and {len(result['cocktail']['ingredients']) - 5} more")
                
                print(f"\n📝 INSTRUCTIONS:")
                instructions = result['cocktail']['instructions']
                if len(instructions) > 200:
                    instructions = instructions[:200] + "..."
                print(f"   {instructions}")
                
                print(f"\n{'='*60}")
                print(f"💭 WHY THIS PAIRING:")
                print(f"   {result['explanation']}")
                
                print(f"\n🎯 Pairing Mood: {result['mood'].title()}")
                print(f"🎲 Confidence: {result['confidence']}")
                
            else:
                print(f"\n❌ {result['error']}")
                print("💡 Try checking the spelling or try a different movie!")
                
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("💡 Please try again with a different movie.")

if __name__ == "__main__":
    main()
