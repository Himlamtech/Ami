#!/bin/bash
echo "🔍 Checking Ami System Connection..."
echo ""
echo "1. Backend API (Port 6008):"
curl -s http://localhost:6008/ | python3 -c "import sys, json; print('✅ Backend is running')" 2>/dev/null || echo "❌ Backend not accessible"
echo ""
echo "2. Frontend (Port 6009):"
curl -s http://127.0.0.1:6009/ | head -1 | grep -q "html" && echo "✅ Frontend is running" || echo "❌ Frontend not accessible"
echo ""
echo "3. Test Login API:"
RESPONSE=$(curl -s -X POST http://localhost:6008/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "Origin: http://127.0.0.1:6009" \
  -d '{"username":"admin","password":"admin"}')
echo "$RESPONSE" | grep -q "access_token" && echo "✅ Login API works" || echo "❌ Login API failed"
echo ""
echo "4. Check Logo:"
curl -s -I http://127.0.0.1:6009/assets/logo_ptit.png | grep -q "200 OK" && echo "✅ Logo is accessible" || echo "❌ Logo not found"
echo ""
echo "5. Environment:"
[ -f .env.development ] && echo "✅ .env.development exists" || echo "❌ .env.development missing"
cat .env.development 2>/dev/null || echo ""
echo ""
echo "🌐 Access your app at: http://127.0.0.1:6009"
