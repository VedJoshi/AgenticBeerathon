#!/usr/bin/env python3
"""
Deployment utility for Clanker That Recommends Alcohol
"""

import argparse
import os
import subprocess
import sys

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import boto3
        import fastapi
        import uvicorn
        import pydantic
        import dotenv
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run 'pip install -r requirements.txt' to install dependencies")
        return False

def check_env():
    """Check if environment variables are set"""
    required_vars = ['AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("Create a .env file with the required variables")
        return False
    
    print("✅ All environment variables are set")
    return True

def deploy_local():
    """Deploy locally with uvicorn"""
    if not (check_dependencies() and check_env()):
        return
    
    print("\n🚀 Deploying locally...")
    print("Starting API server on http://localhost:8000")
    
    subprocess.run([sys.executable, "-m", "src.beer_clanker_bot.api"])

def deploy_docker():
    """Deploy with Docker"""
    if not check_dependencies():
        return
    
    print("\n🐳 Building Docker image...")
    subprocess.run(["docker", "build", "-t", "clanker-api", "."])
    
    print("\n🚀 Running Docker container...")
    subprocess.run([
        "docker", "run", "-p", "8000:8000", 
        "-e", f"AWS_REGION={os.getenv('AWS_REGION', 'us-east-1')}", 
        "-e", f"AWS_ACCESS_KEY_ID={os.getenv('AWS_ACCESS_KEY_ID', '')}", 
        "-e", f"AWS_SECRET_ACCESS_KEY={os.getenv('AWS_SECRET_ACCESS_KEY', '')}", 
        "clanker-api"
    ])

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Deploy Clanker That Recommends Alcohol")
    parser.add_argument("--mode", choices=["local", "docker"], default="local", help="Deployment mode")
    
    args = parser.parse_args()
    
    print("🍸🎬 Clanker That Recommends Alcohol - Deployment")
    print("=" * 60)
    
    if args.mode == "local":
        deploy_local()
    elif args.mode == "docker":
        deploy_docker()

if __name__ == "__main__":
    main()
