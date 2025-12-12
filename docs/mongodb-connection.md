# MongoDB Connection Guide

## Connection String (Working)
```
mongodb://himlam_mongo:himlam_mongo@127.0.0.1:27017/ami?authSource=admin
```

## MongoDB Compass - Method 1: Connection String
Paste vào Compass:
```
mongodb://himlam_mongo:himlam_mongo@127.0.0.1:27017/ami?authSource=admin
```

**Lưu ý**: Dùng `127.0.0.1` thay vì `localhost`

## MongoDB Compass - Method 2: Fill Individual Fields
1. **Connection Type**: Standalone
2. **Host**: `127.0.0.1`
3. **Port**: `27017`
4. **Authentication**: Username/Password
5. **Username**: `himlam_mongo`
6. **Password**: `himlam_mongo`
7. **Authentication Database**: `admin`
8. **Default Database**: `ami` (optional)

## Troubleshooting

### Issue: "Authentication failed"
- Đảm bảo **Authentication Database** = `admin`
- Username/password đúng: `himlam_mongo` / `himlam_mongo`

### Issue: "Connection timeout"
- Dùng `127.0.0.1` thay vì `localhost`
- Kiểm tra Docker container đang chạy: `docker ps | grep mongo`
- Kiểm tra port: `netstat -tuln | grep 27017`

### Issue: Compass version cũ
- Update MongoDB Compass lên version mới nhất
- Hoặc dùng mongosh CLI:
  ```bash
  mongosh "mongodb://himlam_mongo:himlam_mongo@127.0.0.1:27017/ami?authSource=admin"
  ```

## Test Connection từ Terminal
```bash
# Test ping
mongosh "mongodb://himlam_mongo:himlam_mongo@127.0.0.1:27017/ami?authSource=admin" --eval "db.adminCommand({ping: 1})"

# List databases
mongosh "mongodb://himlam_mongo:himlam_mongo@127.0.0.1:27017/ami?authSource=admin" --eval "db.adminCommand({listDatabases: 1})"

# Show collections
mongosh "mongodb://himlam_mongo:himlam_mongo@127.0.0.1:27017/ami?authSource=admin" --eval "db.getCollectionNames()"
```

## Credentials (from .env)
- **User**: `himlam_mongo`
- **Password**: `himlam_mongo`
- **Database**: `ami`
- **Auth Database**: `admin`
- **Port**: `27017`
