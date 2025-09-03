# AWS Setup Checker & Fixer
# This will diagnose your AWS configuration and tell you exactly what to fix

import boto3
import os
from dotenv import load_dotenv
import json

def check_aws_setup():
    """Check if AWS is properly configured"""
    print("🔍 Checking AWS Setup...")
    
    # Load environment
    load_dotenv()
    
    # Check environment variables
    aws_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    
    print(f"📍 Region: {aws_region}")
    print(f"🔑 Access Key: {'✅ Set' if aws_key else '❌ Missing'}")
    print(f"🔒 Secret Key: {'✅ Set' if aws_secret else '❌ Missing'}")
    
    if not aws_key or not aws_secret:
        print("\n❌ AWS credentials are missing!")
        print("🛠️  Fix by adding to your .env file:")
        print("AWS_ACCESS_KEY_ID=your_key_here")
        print("AWS_SECRET_ACCESS_KEY=your_secret_here")
        print("\n📋 To get AWS keys:")
        print("1. Go to AWS Console → IAM → Users → Your User")
        print("2. Security Credentials tab")
        print("3. Create Access Key")
        print("4. Copy both keys to your .env file")
        return False
    
    # Test AWS connection
    try:
        # Test basic AWS connection
        sts = boto3.client('sts', region_name=aws_region)
        identity = sts.get_caller_identity()
        print(f"✅ AWS Connection: Success")
        print(f"👤 Account: {identity.get('Account', 'Unknown')}")
        
        # Test Bedrock access
        try:
            bedrock = boto3.client('bedrock', region_name=aws_region)
            models = bedrock.list_foundation_models()
            print(f"✅ Bedrock Access: Success")
            
            # Check for Claude models
            claude_models = [m for m in models['modelSummaries'] 
                           if 'anthropic.claude' in m['modelId']]
            print(f"🤖 Claude Models Available: {len(claude_models)}")
            
            if claude_models:
                print("Available Claude models:")
                for model in claude_models[:3]:  # Show first 3
                    print(f"   - {model['modelId']}")
            
        except Exception as e:
            print(f"❌ Bedrock Access: Failed - {str(e)}")
            print("🛠️  You may need to request Bedrock access in AWS Console")
            print("   Go to AWS Console → Bedrock → Model Access → Request Access")
            return False
            
        # Test Bedrock Runtime (for actual AI calls)
        try:
            bedrock_runtime = boto3.client('bedrock-runtime', region_name=aws_region)
            print(f"✅ Bedrock Runtime: Ready")
            return True
            
        except Exception as e:
            print(f"❌ Bedrock Runtime: Failed - {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ AWS Connection Failed: {str(e)}")
        print("🛠️  Check your AWS credentials and permissions")
        return False

def test_ai_recommendation():
    """Test a real AI recommendation with current setup"""
    print("\n🤖 Testing AI Recommendation...")
    
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', 
                                     region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        # Simple test prompt
        test_prompt = """You are a movie and cocktail expert. 
        
        Recommend one cocktail for the movie "Casablanca". 
        Respond with just the cocktail name and one sentence explanation.
        """
        
        # Prepare the request
        body = json.dumps({
            "messages": [{"role": "user", "content": test_prompt}],
            "max_tokens": 150,
            "temperature": 0.7
        })
        
        # Make the AI call
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=body,
            contentType='application/json'
        )
        
        # Parse response
        result = json.loads(response['body'].read())
        ai_response = result['content'][0]['text']
        
        print("✅ AI Test Successful!")
        print(f"🤖 Claude's Response: {ai_response}")
        return True
        
    except Exception as e:
        print(f"❌ AI Test Failed: {str(e)}")
        print("💡 Your system will use fallback logic instead")
        return False

def main():
    print("🎬🍸 AWS Strands Agent Setup Checker")
    print("="*50)
    
    # Check basic setup
    aws_ok = check_aws_setup()
    
    if aws_ok:
        # Test AI if AWS is working
        ai_ok = test_ai_recommendation()
        
        if ai_ok:
            print("\n🎉 SETUP COMPLETE!")
            print("Your system is ready for full AI-powered recommendations!")
        else:
            print("\n⚠️ PARTIAL SETUP")
            print("AWS works, but AI needs troubleshooting. Fallback mode will work.")
    else:
        print("\n🛠️ SETUP NEEDED")
        print("Fix AWS credentials first, then run this checker again.")
    
    print("\n📝 Next Steps:")
    print("1. Fix any issues shown above")
    print("2. Run your ai_demo.py to test recommendations")  
    print("3. Ready to add reverse flow (alcohol → movie)!")

if __name__ == "__main__":
    main()
