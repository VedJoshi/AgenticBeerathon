import streamlit as st
import sys
import os
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from beer_clanker_bot.main_app import VinoFlix

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="VinoFlix",
    page_icon="🍸🎬",
    layout="wide"
)

# Title
st.title("🍸🎬 VinoFlix")
st.markdown("**AI-powered movie and cocktail pairing recommendations**")
st.markdown("*Using your personal cocktail collection from S3*")

# Check environment variables
required_vars = ['OMDB_API_KEY', 'AWS_ACCESS_KEY_ID', 'S3_BUCKET_NAME', 'S3_CSV_KEY']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    st.error(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
    st.stop()

# Initialize app
@st.cache_resource
def load_app():
    return VinoFlix(
        s3_bucket=os.getenv('S3_BUCKET_NAME'),
        s3_csv_key=os.getenv('S3_CSV_KEY')
    )

try:
    app = load_app()
    cocktail_suggestions = app.get_cocktail_suggestions()
    if cocktail_suggestions:
        st.success(f"✅ Loaded {len(cocktail_suggestions)} cocktails from S3")
    else:
        st.warning("⚠️ No cocktails loaded from S3. Using fallback mode.")
except Exception as e:
    st.error(f"❌ Failed to load app: {e}")
    st.error("This might be due to S3 permissions or missing CSV file. The app will work in demo mode.")
    
    # Fallback mode - still allow movie recommendations
    try:
        from beer_clanker_bot.omdb_client import OMDBClient
        from beer_clanker_bot.bedrock_client import BedrockClient
        
        st.info("🔄 Running in demo mode - movie lookups available, cocktail data limited")
        omdb_client = OMDBClient(os.getenv('OMDB_API_KEY'))
        bedrock_client = BedrockClient()
        cocktail_suggestions = ["Martini", "Old Fashioned", "Manhattan", "Negroni", "Whiskey Sour"]
        app = None
    except Exception as e2:
        st.error(f"❌ Complete initialization failed: {e2}")
        st.stop()

# Main input
st.markdown("### Enter a movie title or cocktail name:")

# Add autocomplete suggestions for cocktails
if cocktail_suggestions:
    user_input = st.selectbox(
        "Choose from available cocktails or type a movie:",
        options=[""] + cocktail_suggestions + ["Type custom movie..."],
        index=0
    )
else:
    user_input = ""

# If user selects "Type custom movie", show text input
if user_input == "Type custom movie...":
    user_input = st.text_input("Enter movie title:", placeholder="e.g., Casablanca, The Godfather")
elif user_input == "":
    user_input = st.text_input("Or enter any movie/cocktail:", placeholder="e.g., Casablanca, Martini")

# Get recommendation button
if st.button("🎯 Get Perfect Pairing", type="primary"):
    if user_input and user_input not in ["", "Type custom movie..."]:
        with st.spinner("🤖 Claude is analyzing the perfect pairing..."):
            try:
                if app:
                    result = app.get_recommendation(user_input)
                else:
                    # Fallback mode - basic movie lookup
                    movie = omdb_client.get_movie(user_input)
                    if movie:
                        basic_prompt = f"""
                        Movie: {movie['title']} ({movie['year']})
                        Genre: {movie['genre']}
                        Plot: {movie['plot']}
                        
                        Recommend a classic cocktail that would pair perfectly with this movie.
                        Consider the movie's mood, time period, and atmosphere.
                        
                        Format: **🍸 Recommended Cocktail: [Name]**
                        Then explain why it pairs well in 2-3 sentences.
                        """
                        result = bedrock_client.ask_claude(basic_prompt)
                        result = f"## 🎬 {movie['title']} ({movie['year']})\n\n{result}\n\n*Demo mode - limited cocktail data*"
                    else:
                        result = f"❌ Sorry, couldn't find the movie '{user_input}'. Please try a different title."
                
                st.markdown(result)
            except Exception as e:
                st.error(f"❌ Error getting recommendation: {str(e)}")
    else:
        st.warning("Please select a cocktail or enter a movie name")

# Quick examples
st.markdown("---")
st.markdown("### 💡 Quick Examples:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**🎬 Try these movies:**")
    example_movies = ["Casablanca", "The Godfather", "Blade Runner 2049", "Pulp Fiction", "Her"]
    for movie in example_movies:
        if st.button(movie, key=f"movie_{movie}"):
            with st.spinner("🤖 Getting recommendation..."):
                try:
                    if app:
                        result = app.get_recommendation(movie)
                    else:
                        # Fallback mode
                        movie_data = omdb_client.get_movie(movie)
                        if movie_data:
                            basic_prompt = f"""
                            Movie: {movie_data['title']} ({movie_data['year']})
                            Genre: {movie_data['genre']}
                            
                            Recommend a classic cocktail that pairs perfectly with this movie.
                            """
                            result = bedrock_client.ask_claude(basic_prompt)
                            result = f"## 🎬 {movie_data['title']}\n\n{result}"
                        else:
                            result = f"❌ Could not find movie: {movie}"
                    
                    st.markdown(result)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

with col2:
    st.markdown("**🍸 Available cocktails:**")
    if cocktail_suggestions:
        for cocktail in cocktail_suggestions[:5]:  # Show first 5
            if st.button(cocktail, key=f"cocktail_{cocktail}"):
                with st.spinner("🤖 Getting recommendation..."):
                    try:
                        if app:
                            result = app.get_recommendation(cocktail)
                        else:
                            # Fallback mode
                            basic_prompt = f"""
                            Cocktail: {cocktail}
                            
                            Recommend a classic movie that would pair perfectly with this cocktail.
                            Consider the cocktail's sophistication and character.
                            """
                            result = bedrock_client.ask_claude(basic_prompt)
                            result = f"## 🍸 {cocktail}\n\n{result}"
                        
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    else:
        st.markdown("*No cocktails loaded - using demo mode*")

# Info section
st.markdown("---")
st.markdown("### 📊 How it works:")
if app and cocktail_suggestions:
    st.markdown(f"""
    - **Your Data**: {len(cocktail_suggestions)} cocktails loaded from S3
    - **Movie Data**: Real-time from OMDB API
    - **AI**: AWS Bedrock Claude analyzes and creates perfect pairings
    - **Logic**: Movie → Cocktail (from your collection) | Cocktail → Movie (from Claude's knowledge)
    """)
else:
    st.markdown("""
    - **Demo Mode**: Limited cocktail selection
    - **Movie Data**: Real-time from OMDB API
    - **AI**: AWS Bedrock Claude for recommendations
    - **Note**: For full experience, ensure S3 cocktail data is accessible
    """)
