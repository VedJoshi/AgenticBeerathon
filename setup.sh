#!/bin/bash

# Setup script for AgenticBeerathon Vector Database

echo "🍸 Setting up AgenticBeerathon Vector Database..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL first."
    echo "On macOS: brew install postgresql"
    echo "On Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# Check if pgvector extension is available
echo "🔍 Checking for pgvector extension..."

# Start PostgreSQL service if not running
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! pgrep -x "postgres" > /dev/null; then
        echo "🚀 Starting PostgreSQL service..."
        brew services start postgresql
        sleep 3
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    sudo service postgresql start
fi

# Create database if it doesn't exist
echo "📊 Creating database 'agenticbeerathon'..."
createdb agenticbeerathon 2>/dev/null || echo "Database already exists or user lacks privileges"

# Install pgvector extension
echo "🔧 Installing pgvector extension..."
psql -d agenticbeerathon -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>/dev/null || {
    echo "❌ Failed to install pgvector extension."
    echo "Please install pgvector:"
    echo "  brew install pgvector  # macOS"
    echo "  sudo apt install postgresql-<version>-pgvector  # Ubuntu"
    exit 1
}

# Set up Python virtual environment
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment variables
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << EOF
# Database Configuration
DB_HOST=localhost
DB_NAME=agenticbeerathon
DB_USER=postgres
DB_PASSWORD=
DB_PORT=5432

# OpenAI Configuration (optional - for better embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# AWS Configuration (if using AWS services)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Logging
LOG_LEVEL=INFO
EOF
    echo "📝 Created .env file. Please update with your configuration."
fi

# Run database schema setup
echo "🏗️ Setting up database schema..."
python -c "
import sys
sys.path.append('.')
from src.utils.database_config import setup_database, run_schema_setup
try:
    setup_database()
    run_schema_setup()
    print('✅ Database schema setup completed')
except Exception as e:
    print(f'❌ Schema setup failed: {e}')
    print('Please check your database connection and try again.')
"

echo ""
echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your database credentials and API keys"
echo "2. Load cocktail data: python src/utils/cocktail_data_embedder.py"
echo "3. Test the search: python tools/cocktail_search_cli.py similar Margarita"
echo ""
echo "For help: python tools/cocktail_search_cli.py --help"
