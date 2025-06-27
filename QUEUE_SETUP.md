# Queue Worker System Setup

## Overview
The blood test analyzer now supports concurrent request processing using a Redis-based queue system. This allows the API to handle multiple analysis requests simultaneously without blocking.

## Features
- **Asynchronous Processing**: Submit analysis requests and get results later
- **Concurrent Execution**: Multiple workers can process jobs simultaneously  
- **Fallback Support**: Works with in-memory queue if Redis is not available
- **Job Tracking**: Monitor job status and retrieve results
- **Queue Statistics**: Monitor system performance

## Quick Setup

### 1. Install Redis (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 2. Install Python Dependencies
```bash
# Install queue requirements
pip install -r requirements_queue.txt

# Or install manually
pip install redis==5.0.1
```

### 3. Start the System

#### Option A: Integrated Worker (Single Process)
```bash
# Start FastAPI with embedded worker
python main.py
```

#### Option B: Separate Worker Processes (Recommended for Production)
```bash
# Terminal 1: Start FastAPI server
python main.py

# Terminal 2: Start dedicated workers
python worker.py

# Or with custom worker count
WORKER_COUNT=4 python worker.py
```

## API Endpoints

### Synchronous Processing (Original)
```http
POST /analyze
Content-Type: multipart/form-data

file: [PDF file]
query: "Please analyze my blood test results"
```

### Asynchronous Processing (New)
```http
POST /analyze-async
Content-Type: multipart/form-data

file: [PDF file]
query: "Please analyze my blood test results"
```

**Response:**
```json
{
  "status": "queued",
  "job_id": "uuid-here",
  "message": "Analysis has been queued for processing",
  "status_url": "/status/uuid-here",
  "estimated_processing_time": "1-3 minutes"
}
```

### Check Job Status
```http
GET /status/{job_id}
```

**Response (Processing):**
```json
{
  "job_id": "uuid-here",
  "status": "processing",
  "created_at": "2024-01-27T12:00:00",
  "updated_at": "2024-01-27T12:01:00"
}
```

**Response (Completed):**
```json
{
  "job_id": "uuid-here", 
  "status": "completed",
  "result": {
    "status": "success",
    "analysis": "...",
    "specialists_consulted": ["..."]
  }
}
```

### Queue Statistics
```http
GET /queue/stats
```

**Response:**
```json
{
  "queue_enabled": true,
  "queue_length": 3,
  "backend": "redis",
  "status": "healthy"
}
```

## Configuration

### Environment Variables
```bash
# Redis connection
REDIS_URL=redis://localhost:6379/0

# Worker settings
WORKER_COUNT=2

# Google API key (existing)
GOOGLE_API_KEY=your_key_here
```

### Fallback Mode
If Redis is not available, the system automatically falls back to an in-memory queue:
- ⚠️ Jobs are lost on server restart
- ⚠️ No persistence across worker processes
- ✅ Still allows concurrent processing within single process

## Production Deployment

### Using Docker Compose
```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
  
  worker:
    build: .
    command: python worker.py
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
      - WORKER_COUNT=4
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    scale: 2
```

### Using systemd (Linux)
```ini
# /etc/systemd/system/blood-test-worker.service
[Unit]
Description=Blood Test Analysis Worker
After=network.target redis.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/blood-test-analyser-debug
Environment=WORKER_COUNT=4
Environment=GOOGLE_API_KEY=your_key
ExecStart=/path/to/venv/bin/python worker.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Monitoring

### Log Files
- `blood_test_analyzer.log` - Main API logs
- `worker.log` - Worker process logs

### Health Checks
```bash
# Check API health
curl http://localhost:8000/health

# Check queue stats
curl http://localhost:8000/queue/stats

# Check Redis status
redis-cli ping
```

### Performance Monitoring
```bash
# Monitor queue length
redis-cli llen blood_analysis_queue

# Monitor job keys
redis-cli keys "job:*"

# Check worker processes
ps aux | grep worker.py
```

## Testing Your Queue System

### Test Asynchronous Processing
```bash
# Submit a job (returns immediately with job_id)
curl -X POST "http://localhost:8000/analyze-async" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/blood_test_report.pdf" \
  -F "query=Please analyze my blood test results"

# Expected response:
{
  "status": "queued",
  "job_id": "62cc85e0-e000-4bd1-81b0-be3dc4f1f976",
  "request_id": "0365e356-a60d-4702-bb55-e05483fd0343",
  "message": "Analysis has been queued for processing",
  "status_url": "/status/62cc85e0-e000-4bd1-81b0-be3dc4f1f976",
  "estimated_processing_time": "1-3 minutes",
  "file_processed": "sample.pdf",
  "processing_info": {
    "file_size_bytes": 704703,
    "timestamp": 1751057413.2923782,
    "mode": "asynchronous"
  }
}
```

### Check Job Results
```bash
# Use the job_id from above response
curl -X GET "http://localhost:8000/status/YOUR_JOB_ID" | python3 -m json.tool

# Example with actual job ID:
curl -X GET "http://localhost:8000/status/62cc85e0-e000-4bd1-81b0-be3dc4f1f976" | python3 -m json.tool
```

### Test Multiple Concurrent Jobs
```bash
# Submit multiple jobs simultaneously to test concurrency
for i in {1..3}; do
  curl -X POST "http://localhost:8000/analyze-async" \
    -H "Content-Type: multipart/form-data" \
    -F "file=@data/blood_test_report.pdf" \
    -F "query=Test job $i" &
done
wait

# Check queue stats to see concurrent processing
curl -X GET "http://localhost:8000/queue/stats" | python3 -m json.tool
```

### Performance Comparison Testing
```bash
# Test synchronous endpoint (blocking, slower)
time curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/blood_test_report.pdf" \
  -F "query=Sync test"

# Test asynchronous endpoint (immediate response, faster)
time curl -X POST "http://localhost:8000/analyze-async" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/blood_test_report.pdf" \
  -F "query=Async test"
```

### Real-time Queue Monitoring
```bash
# Watch queue stats in real-time
watch -n 2 'curl -s "http://localhost:8000/queue/stats" | python3 -m json.tool'

# Monitor Redis queue length (if using Redis)
watch -n 1 'redis-cli llen blood_analysis_queue'
```

## Troubleshooting

### Redis Connection Issues
```bash
# Check if Redis is running
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping

# Check Redis logs
sudo journalctl -u redis-server

# If Redis fails to start, check configuration
sudo nano /etc/redis/redis.conf
```

### Worker Issues
```bash
# Check worker logs
tail -f worker.log

# Restart workers
pkill -f worker.py
python worker.py

# Check if workers are processing jobs
ps aux | grep worker.py

# Monitor worker activity in real-time
tail -f blood_test_analyzer.log | grep -E "(Processing job|Job.*completed)"
```

### Queue Stuck
```bash
# Check queue status first
redis-cli llen blood_analysis_queue
redis-cli keys "job:*"

# Clear all jobs (WARNING: destructive)
redis-cli flushdb

# Or clear specific queue
redis-cli del blood_analysis_queue

# Clear specific job
redis-cli del "job:YOUR_JOB_ID"
```

### Common Issues and Solutions

#### Issue: "Queue not working, jobs stay pending"
**Solution:**
1. Check if workers are running: `ps aux | grep worker.py`
2. Start workers: `python worker.py`
3. Check worker logs: `tail -f worker.log`

#### Issue: "Redis connection refused"
**Solution:**
1. Install Redis: `sudo apt install redis-server`
2. Start Redis: `sudo systemctl start redis-server`
3. Check status: `redis-cli ping`

#### Issue: "Jobs complete but results missing"
**Solution:**
1. Check Redis for job data: `redis-cli keys "job:*"`
2. Verify job ID format in status requests
3. Check API logs: `tail -f blood_test_analyzer.log`

#### Issue: "In-memory fallback not working"
**Solution:**
1. Check API logs for fallback activation
2. Ensure main.py is running with embedded queue worker
3. Restart API server: `python main.py`

## Performance Benefits

### Before (Synchronous Only)
- 🐌 One request at a time
- 😴 Users wait 5-15 seconds per request
- ❌ Server blocks during processing
- 📉 Poor scalability

### After (With Queue System)
- ⚡ Multiple concurrent requests
- 🚀 Immediate response (job queued)
- 📊 Non-blocking API
- 📈 Horizontal scalability
- 🎯 Better user experience

## Implementation Details

### Key Components
1. **`queue_worker.py`**: Redis-based queue system with in-memory fallback
2. **`main.py`**: Enhanced FastAPI server with async endpoints
3. **`worker.py`**: Standalone worker processes for production
4. **`requirements_queue.txt`**: Additional dependencies for queue functionality

### Job Status Flow
```
queued → processing → completed
   ↓         ↓           ↓
pending → running → success/failed
```

### Data Structures
```python
# Job data stored in Redis
{
  "job_id": "uuid",
  "status": "pending|processing|completed|failed", 
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "file_path": "temp/file/path",
  "query": "user query",
  "result": {...}  # Only present when completed
}
```

### Error Handling
- **File Upload Validation**: Size limits, PDF format checking
- **Queue Failures**: Automatic fallback to in-memory processing
- **Worker Crashes**: Jobs automatically retry with other workers
- **Redis Outages**: Graceful degradation to embedded processing

## Advanced Configuration

### Tuning for Production
```bash
# Redis memory optimization
redis-cli config set maxmemory 512mb
redis-cli config set maxmemory-policy allkeys-lru

# Worker optimization
export WORKER_COUNT=8  # CPU cores * 2
export REDIS_POOL_SIZE=10
export MAX_QUEUE_SIZE=1000
```

### SSL/TLS Setup
```bash
# For production Redis with authentication
export REDIS_URL="rediss://username:password@redis-host:6380/0"
```

### Horizontal Scaling
```yaml
# Scale workers independently
docker-compose up --scale worker=5

# Load balance API servers
version: '3.8'
services:
  nginx:
    image: nginx
    ports: ["80:80"]
  api:
    build: .
    scale: 3
```

## Cost Analysis
- **Redis Memory**: ~1MB per 1000 queued jobs
- **Worker Overhead**: ~50MB per Python worker process
- **Network**: Minimal Redis communication overhead
- **Processing Time**: ~1-2 minutes per blood test analysis
- **Concurrency**: Up to 10x more requests handled simultaneously
- **Total**: Very lightweight for significant performance gain

## Version History
- **v2.0.0**: Basic queue system implementation
- **v2.1.0**: Enhanced error handling and validation
- **v2.2.0**: Queue system with async endpoints (current)

## Migration Guide

### From v2.1.0 to v2.2.0
1. Install queue dependencies: `pip install -r requirements_queue.txt`
2. No breaking changes - all existing endpoints work unchanged
3. New async endpoints available immediately
4. Optional: Set up Redis for persistence (system works without it) 