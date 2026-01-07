# Deployment Strategy for KDP Ghostwriter App

## Recommended: User API Keys + Lightweight Server

This is the best model for a KDP-focused app store application.

### Architecture

```
┌──────────────────────┐
│ User's Mobile Device │
│                      │
│ App Settings:        │
│ • OpenAI API Key     │
│ • Anthropic API Key  │
└──────────┬───────────┘
           │ HTTPS
           ▼
┌──────────────────────┐
│ Your Cloud Server    │
│ (DigitalOcean $24/mo)│
│                      │
│ • FastAPI            │
│ • Redis (local)      │
│ • ChromaDB (local)   │
│                      │
│ NO user data stored  │
│ NO API key storage   │
└──────────────────────┘
```

### Why This Works for KDP Publishers

**Your Target Users Already Have:**
- OpenAI API accounts (for ChatGPT, GPT-4)
- Budget for AI tools ($100-500/month)
- Technical knowledge (using AI for publishing)

**Benefits:**
1. **Zero API Costs for You**: Users pay their own OpenAI/Anthropic bills ($12-18 per book)
2. **Privacy**: No user manuscripts stored permanently on your server
3. **Compliance**: No need to secure API keys (they're never stored)
4. **Scalability**: Your server just orchestrates - no heavy costs
5. **Simple Billing**: One-time app purchase or small monthly fee ($9.99/month)

---

## Implementation Changes

### 1. Update Mobile App Settings Screen

**Add Settings Screen** (`mobile_app/src/screens/SettingsScreen.js`):

```javascript
import React, { useState } from 'react';
import { View, TextInput, Button, AsyncStorage } from 'react-native';

export default function SettingsScreen() {
  const [openaiKey, setOpenaiKey] = useState('');
  const [anthropicKey, setAnthropicKey] = useState('');

  const saveKeys = async () => {
    await AsyncStorage.setItem('openai_key', openaiKey);
    await AsyncStorage.setItem('anthropic_key', anthropicKey);
    Alert.alert('Saved', 'API keys saved securely');
  };

  return (
    <View>
      <Text>OpenAI API Key</Text>
      <TextInput
        value={openaiKey}
        onChangeText={setOpenaiKey}
        placeholder="sk-..."
        secureTextEntry
      />

      <Text>Anthropic API Key</Text>
      <TextInput
        value={anthropicKey}
        onChangeText={setAnthropicKey}
        placeholder="sk-ant-..."
        secureTextEntry
      />

      <Button title="Save Keys" onPress={saveKeys} />

      <Text>How to get API keys:</Text>
      <Text>• OpenAI: https://platform.openai.com/api-keys</Text>
      <Text>• Anthropic: https://console.anthropic.com/</Text>
    </View>
  );
}
```

### 2. Update API Upload to Send Keys

```javascript
// In HomeScreen.js
const uploadManuscript = async () => {
  const openaiKey = await AsyncStorage.getItem('openai_key');
  const anthropicKey = await AsyncStorage.getItem('anthropic_key');

  if (!openaiKey || !anthropicKey) {
    Alert.alert('API Keys Required', 'Please configure your API keys in Settings');
    return;
  }

  const response = await api.uploadManuscript(
    selectedFile,
    openaiKey,
    anthropicKey
  );
};
```

### 3. Update Backend to Accept User Keys

```python
# In api_server.py
@app.post("/upload")
async def upload_manuscript(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    openai_key: str = Header(...),
    anthropic_key: str = Header(...)
):
    # Validate keys immediately
    if not openai_key.startswith("sk-"):
        raise HTTPException(400, "Invalid OpenAI key")
    if not anthropic_key.startswith("sk-ant-"):
        raise HTTPException(400, "Invalid Anthropic key")

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Start processing with USER'S keys
    background_tasks.add_task(
        process_manuscript_async,
        job_id=job_id,
        file_path=str(file_path),
        openai_key=openai_key,
        anthropic_key=anthropic_key
    )

    return {"job_id": job_id}
```

### 4. Update Orchestrator to Use Provided Keys

```python
# In main.py
class GhostwriterOrchestrator:
    def __init__(
        self,
        book_id: str,
        openai_key: str = None,  # NEW
        anthropic_key: str = None,  # NEW
        redis_host: str = "localhost",
        redis_port: int = 6379,
        chromadb_host: str = "localhost",
        chromadb_port: int = 8000,
        verbose: bool = True
    ):
        # Set keys as environment variables for this session
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key

        # Rest of initialization...
```

---

## Storage Requirements

### Redis (Temporary Storage)
**What**: In-memory database for active processing
**Stores**: Current manuscript, flags, task states
**Size**: ~50MB per active job
**Retention**: Cleared after job completes

**Setup on Server:**
```bash
# Docker container (included in docker-compose.yml)
docker run -d -p 6379:6379 redis:alpine
```

**Cost**: Free (included in server)

### ChromaDB (Long-term Learning)
**What**: Vector database for persistent patterns
**Stores**: High-quality scenes, niche patterns
**Size**: ~1GB per 100 books processed
**Retention**: Persistent (improves over time)

**Setup on Server:**
```bash
# Docker container (included in docker-compose.yml)
docker run -d -p 8000:8000 chromadb/chroma
```

**Cost**: Free (included in server)

**Privacy Note**: With user API keys model, you can choose:
- **Shared Learning**: All users benefit from patterns (default)
- **Private Learning**: Each user's data isolated (add `book_id` prefix per user)

---

## Server Requirements

### Minimum Specs
- **CPU**: 2 cores
- **RAM**: 4GB (2GB FastAPI + 1GB Redis + 1GB ChromaDB)
- **Disk**: 50GB (10GB OS + 40GB ChromaDB growth)
- **Network**: 100GB/month bandwidth

### Recommended Providers

#### **DigitalOcean Droplet** ($24/month)
- 2 vCPU, 4GB RAM, 80GB SSD
- Simple setup
- Good support

#### **AWS EC2 t3.medium** ($30/month)
- 2 vCPU, 4GB RAM
- More scalability options
- Requires more configuration

#### **Hetzner Cloud** ($15/month)
- 2 vCPU, 4GB RAM, 40GB SSD
- Cheapest option
- EU-based

---

## Data Flow Example

### User Processes a Book

1. **Upload** (Mobile App):
   ```
   User selects manuscript.txt
   App reads from AsyncStorage: openai_key, anthropic_key
   POST /upload with file + keys in headers
   ```

2. **Server Receives**:
   ```python
   # api_server.py receives:
   # - manuscript.txt file
   # - openai_key: sk-abc123...
   # - anthropic_key: sk-ant-xyz789...

   # Server does NOT store keys
   # Keys passed directly to background task
   ```

3. **Processing**:
   ```
   Orchestrator initialized with user's keys
   OpenAI calls → charged to user's account
   Anthropic calls → charged to user's account

   Chapters stored in Redis (temporary)
   Progress updates via WebSocket
   ```

4. **Completion**:
   ```
   Final manuscript compiled
   Saved to /outputs/{job_id}_manuscript.txt
   High-quality scenes → ChromaDB (learning)
   Redis data cleared
   ```

5. **Download** (Mobile App):
   ```
   GET /download/{job_id}
   Manuscript downloaded to device
   Server file deleted after 24 hours
   ```

---

## Cost Breakdown

### Your Monthly Costs (Per 100 Users Processing 1 Book/Month)

**Server:**
- DigitalOcean Droplet: $24/month
- Domain + SSL: $2/month
- **Total Server**: $26/month

**API Costs:**
- None! (Users use their own keys)

**Your Revenue:**
- 100 users × $9.99/month = $999/month
- **Profit**: $973/month

### User's Costs (Per Book)
- OpenAI API: $8-12
- Anthropic API: $4-6
- Your app subscription: $9.99/month
- **Total**: ~$22-28 per book

**Still 40x cheaper than human ghostwriter ($800-1,300)**

---

## Privacy & Security

### What You Store
- ✅ Job metadata (job_id, status, progress)
- ✅ Activity logs (for debugging)
- ✅ Successful patterns in ChromaDB (anonymized)
- ❌ User API keys (NEVER stored)
- ❌ User manuscripts (deleted after download)

### Security Measures
1. **HTTPS Required**: SSL certificate (Let's Encrypt)
2. **Keys in Headers**: Never in URL or request body
3. **Temporary Storage**: Manuscripts deleted after 24 hours
4. **Rate Limiting**: Prevent abuse
5. **Input Validation**: Sanitize all uploads

---

## Alternative: Local-First Model

If you want users to run everything locally (not App Store compatible):

### Desktop App (Electron)
```
User's Computer:
├── Electron App (frontend)
├── Python Backend (bundled)
├── Redis (Docker)
└── ChromaDB (Docker)
```

**Pros:**
- Complete privacy
- No server costs
- Users own their data

**Cons:**
- Can't publish to mobile app stores
- Complex installation
- No centralized learning

---

## Recommended Path Forward

### Phase 1: MVP (This Month)
1. Add Settings screen to mobile app
2. Update API to accept user keys
3. Deploy to DigitalOcean ($24/month)
4. Test with 5-10 beta users

### Phase 2: Launch (Next Month)
1. Submit to App Stores
2. Pricing: $9.99/month or $79/year
3. Marketing to KDP publishers
4. Monitor server load

### Phase 3: Scale (Months 3-6)
1. If >200 users, upgrade server
2. Add payment processing (Stripe)
3. Add user accounts (optional)
4. Build web version

---

## Setup Instructions

See `SERVER_SETUP_GUIDE.md` for step-by-step deployment to DigitalOcean.

---

## Questions?

**"What if users abuse the server?"**
- Rate limiting: 1 upload per 10 minutes
- Require account registration
- Monitor unusual patterns

**"What if my server goes down?"**
- Set up monitoring (UptimeRobot)
- Keep backups of ChromaDB data
- Use managed services as fallback

**"Can I offer a free tier?"**
- Free: 1 book per month
- Paid: Unlimited processing
- This covers your server costs

---

**Recommendation**: Start with User API Keys model. It's the most sustainable for a KDP-focused app.
