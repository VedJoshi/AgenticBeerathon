import boto3
import json
import os

class BedrockClient:
    def __init__(self):
        self.bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
    
    def recommend_cocktail_for_movie(self, movie_data, cocktail_context=None):
        """Generate cocktail recommendation based on movie - either create new or select from available"""
        
        if cocktail_context:
            # Legacy mode: recommend from available cocktails
            prompt = f"""
            Movie: {movie_data['title']} ({movie_data['year']})
            Genre: {movie_data['genre']}
            Plot: {movie_data['plot']}
            Director: {movie_data['director']}
            Runtime: {movie_data['runtime']}
            
            {cocktail_context}

            First, check if the movie is widely associated with an iconic cocktail (e.g., Vesper Martini in Casino Royale, White Russian in The Big Lebowski, French 75 in Casablanca, Cosmopolitan in Sex and the City, Red Eye in Cocktail, Pink Lady in Grease, Blood and Sand in Blood and Sand). If so, OVERRIDE the standard S3 cocktail recommendation, and instead:

            **🍸 Iconic Movie Cocktail: [Name]**

            **Why this drink is iconic:**
            [2-3 sentences explaining the cocktail's place in the movie, cinematic significance, and how it embodies the film's atmosphere.]

            Otherwise, if there is no strong iconic cocktail association:

            Based on this movie's mood, themes, and atmosphere, recommend ONE specific cocktail from the available cocktails above that would pair perfectly.
            
            Consider:
            - The movie's genre and mood
            - The time period and setting
            - The sophistication level
            - The emotional tone
            
            Format your response as:
            **🍸 Recommended Cocktail: [Name]**
            
            **Why it pairs perfectly:**
            [2-3 sentences explaining why this specific cocktail matches the movie's character and mood]
            
            **The experience:**
            [Describe how sipping this cocktail would enhance watching this movie]
            """
        else:
            # New mode: AI creates/suggests any cocktail
            prompt = f"""
            Movie: {movie_data['title']} ({movie_data['year']})
            Genre: {movie_data['genre']}
            Plot: {movie_data['plot']}
            Director: {movie_data['director']}
            Runtime: {movie_data['runtime']}

            Based on this movie's mood, themes, atmosphere, and setting, recommend the PERFECT cocktail to pair with it. This can be:
            1. An iconic cocktail from the movie itself (if it has one)
            2. A classic cocktail that matches the movie's era, mood, or sophistication
            3. A creative cocktail you design specifically for this movie
            
            Consider:
            - The movie's genre, mood, and emotional tone
            - The time period and setting
            - The sophistication level and target audience
            - Colors, flavors, and presentation that match the movie's aesthetic
            - The drinking experience that would enhance movie watching
            
            Format your response as:
            **🍸 Perfect Pairing: [Cocktail Name]**
            
            **The Cocktail:**
            - Base spirit(s): [main ingredients]
            - Key flavors: [flavor profile]
            - Served in: [glass type]
            - Garnish: [garnish description]
            
            **Why it's perfect:**
            [2-3 sentences explaining why this cocktail perfectly captures the movie's essence]
            
            **The experience:**
            [Describe how this cocktail enhances the movie-watching experience]
            
            **Quick Recipe:** [If it's a known cocktail, provide basic proportions]
            """
        
        return self._call_claude(prompt)
    
    def recommend_movie_for_cocktail(self, cocktail_data):
        """Recommend movie based on specific cocktail"""
        
        prompt = f"""
        Cocktail: {cocktail_data['name']}
        Description: {cocktail_data['description']}
        Ingredients: {cocktail_data['ingredients']}
        Flavor Profile: {cocktail_data['flavor_profile']}
        Served in: {cocktail_data['glass']}
        Method: {cocktail_data['method']}
        
        Based on this cocktail's character, sophistication, flavor profile, and the mood it creates, recommend ONE specific well-known movie that would pair perfectly.
        
        Consider:
        - The cocktail's complexity and refinement
        - Its flavor notes (bitter, sweet, strong, etc.)
        - The occasion when someone would drink this
        - The atmosphere it creates
        - Its historical context or associations
        
        Format your response as:
        **🎬 Recommended Movie: [Title] ([Year])**
        
        **Why it pairs perfectly:**
        [2-3 sentences explaining why this movie matches the cocktail's character and mood]
        
        **The experience:**
        [Describe how this movie complements the cocktail-drinking experience]
        """
        
        return self._call_claude(prompt)
    
    def recommend_movie_for_cocktail_name(self, cocktail_name: str):
        """Recommend movie based on cocktail name only (when AI generates the cocktail)"""
        
        prompt = f"""
        Cocktail: {cocktail_name}
        
        Based on this cocktail's name and what you know about it (or if it's a creative cocktail, based on what the name suggests), recommend ONE specific well-known movie that would pair perfectly.
        
        Consider:
        - The cocktail's likely character and sophistication
        - The mood and atmosphere it suggests
        - Any cultural or historical associations
        - The type of occasion when someone would drink this
        
        Format your response as:
        **🎬 Recommended Movie: [Title] ([Year])**
        
        **About the cocktail:**
        [Brief description of what this cocktail is like]
        
        **Why it pairs perfectly:**
        [2-3 sentences explaining why this movie matches the cocktail's character and mood]
        
        **The experience:**
        [Describe how this movie complements the cocktail-drinking experience]
        """
        
        return self._call_claude(prompt)
    
    def ask_claude(self, prompt, temperature=0.7, max_tokens=1000):
        """
        Send a prompt to Claude via AWS Bedrock (legacy method)
        """
        return self._call_claude(prompt, temperature, max_tokens)
    
    def _call_claude(self, prompt, temperature=0.7, max_tokens=500):
        """Make API call to Claude"""
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            })
            
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
            
        except Exception as e:
            return f"Error calling Claude: {str(e)}"
