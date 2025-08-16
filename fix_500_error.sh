#!/bin/bash
# Script to debug and fix 500 Internal Server Error

echo "🔧 AmiAgent API 500 Error Debug & Fix Script"
echo "============================================="

# 1. Check container status
echo "1. Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n2. Check .env file:"
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    echo "OPENAI_API_KEY status:"
    if grep -q "OPENAI_API_KEY=" .env; then
        if grep -q "OPENAI_API_KEY=sk-" .env; then
            echo "✅ OPENAI_API_KEY is set"
        else
            echo "❌ OPENAI_API_KEY is empty or invalid"
            echo "🔧 Fix: Add your OpenAI API key to .env file"
        fi
    else
        echo "❌ OPENAI_API_KEY not found in .env"
        echo "🔧 Fix: Add OPENAI_API_KEY=sk-your-key-here to .env file"
    fi
else
    echo "❌ .env file not found"
    echo "🔧 Creating .env file from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env created from .env.example"
        echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
    else
        echo "❌ .env.example also not found"
    fi
fi

echo -e "\n3. API Logs (last 20 lines):"
docker logs amiagent-api --tail 20

echo -e "\n4. Quick API Test:"
echo "Testing health endpoint..."
health_response=$(curl -s -w "%{http_code}" http://localhost:1912/health -o /tmp/health_response)
if [ "$health_response" = "200" ]; then
    echo "✅ Health endpoint working: $(cat /tmp/health_response)"
else
    echo "❌ Health endpoint failed with code: $health_response"
fi

echo -e "\n5. Environment Variables in Container:"
docker exec amiagent-api env | grep -E "(OPENAI|APP_ENV|DEBUG)" || echo "Could not access container env"

echo -e "\n============================================="
echo "🎯 COMMON FIXES:"
echo "1. Add OpenAI API Key:"
echo "   echo 'OPENAI_API_KEY=sk-your-key-here' >> .env"
echo ""
echo "2. Restart container:"
echo "   docker compose restart amiagent"
echo ""
echo "3. For testing without OpenAI (mock mode):"
echo "   Edit .env and set APP_ENV=dev"
echo "   Or remove OPENAI_API_KEY requirement temporarily"
echo ""
echo "4. View real-time logs:"
echo "   docker logs amiagent-api -f"
echo ""
echo "5. Complete restart:"
echo "   docker compose down && docker compose up -d"

rm -f /tmp/health_response
