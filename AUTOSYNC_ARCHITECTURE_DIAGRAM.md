```mermaid
flowchart TB
    subgraph GitHub
        A[User Installs App]
        B[Developer Pushes Code]
        C[User Creates Issue]
        D[Repository Created]
    end

    subgraph WebhookSystem["Webhook System (/api/github/webhook/)"]
        E[Receive Webhook]
        F{Verify Signature}
        G[Route Event]
    end

    subgraph EventProcessors["Event Processors"]
        H[Installation Handler]
        I[Push Handler]
        J[Issue Handler]
        K[Repository Handler]
    end

    subgraph SyncManager["Sync Manager"]
        L[Token Cache]
        M[Import Repository]
        N[Sync Commits]
        O[Sync Issues]
        P[Update Contributors]
    end

    subgraph Database["Database"]
        Q[(Repositories)]
        R[(Commits)]
        S[(Issues)]
        T[(Contributors)]
        U[(SyncJobs)]
    end

    subgraph BackgroundJobs["Background Jobs"]
        V[Periodic Sync<br/>Every 15 min]
        W[Process All Installations]
        X[Catch Missed Webhooks]
    end

    subgraph Frontend["Frontend Dashboard"]
        Y[Repository List]
        Z[Analytics]
        AA[Team Health]
        AB[Sync Status]
    end

    subgraph Monitoring["Monitoring"]
        AC[/api/sync/health/]
        AD[/api/sync/jobs/]
        AE[Success Rate]
        AF[Error Tracking]
    end

    A -->|installation.created| E
    B -->|push| E
    C -->|issues.opened| E
    D -->|repository.created| E

    E --> F
    F -->|Valid| G
    F -->|Invalid| G1[Return 401]
    
    G --> H
    G --> I
    G --> J
    G --> K

    H -->|Auto-import all repos| M
    I -->|Import commits| N
    J -->|Import issues| O
    K -->|Create repo| M

    M --> L
    N --> L
    O --> L
    P --> L

    L -->|Cached 50 min| M
    L -->|Cached 50 min| N
    L -->|Cached 50 min| O

    M --> Q
    N --> R
    O --> S
    P --> T
    
    H --> U
    I --> U
    J --> U
    K --> U

    V --> W
    W --> M
    W --> N
    W --> O
    W --> U
    X --> M

    Q --> Y
    R --> Z
    S --> Z
    T --> AA
    U --> AB

    U --> AC
    U --> AD
    U --> AE
    U --> AF

    style E fill:#4CAF50
    style F fill:#FF9800
    style L fill:#2196F3
    style U fill:#9C27B0
    style V fill:#FF5722

    classDef webhook fill:#4CAF50,stroke:#388E3C,stroke-width:2px
    classDef security fill:#FF9800,stroke:#F57C00,stroke-width:2px
    classDef cache fill:#2196F3,stroke:#1976D2,stroke-width:2px
    classDef database fill:#9C27B0,stroke:#7B1FA2,stroke-width:2px
    classDef cron fill:#FF5722,stroke:#D84315,stroke-width:2px
```

## System Flow Explanation

### 1. Webhook Reception (Green)
- GitHub sends event → Webhook handler receives
- Signature verified with HMAC-SHA256
- Event routed to appropriate processor

### 2. Event Processing (Orange)
- Installation events → Auto-import ALL repositories
- Push events → Import new commits
- Issue events → Create/update issues
- Repository events → Add/remove repos

### 3. Token Management (Blue)
- JWT token generated for GitHub App
- Installation tokens cached for 50 minutes
- Automatic refresh on expiration
- Reduces API calls by 95%

### 4. Database Operations (Purple)
- Idempotent inserts (no duplicates)
- Transaction-based for consistency
- SyncJob tracks every operation
- Detailed error logging

### 5. Background Sync (Red)
- Runs every 15-30 minutes via cron
- Syncs ALL installations
- Catches missed webhooks
- Ensures data consistency

### 6. Frontend Updates
- Real-time data from database
- Repository list always current
- Analytics automatically updated
- Team health recalculated

### 7. Monitoring
- Health check endpoint
- Sync job history
- Success rate tracking
- Error monitoring

## Key Flows

### Flow A: New Installation
```
User installs app → installation.created webhook 
→ Auto-import handler → Fetch all repos via API
→ For each repo: Create DB record + Setup webhook
→ Import commits, issues, contributors
→ Create SyncJob record
→ Frontend shows all repos
```

### Flow B: New Commit
```
Developer pushes → push webhook 
→ Push handler extracts commits
→ For each commit: Check SHA (idempotent)
→ Get/create contributor
→ Create commit record
→ Update repository metrics
→ Frontend shows new commit instantly
```

### Flow C: Periodic Sync
```
Cron triggers → sync_github command
→ For each installation:
    → For each repository:
        → Check last_synced_at
        → Fetch new commits/issues
        → Update DB
        → Update last_synced_at
→ Create SyncJob with results
→ Log metrics
```

### Flow D: Token Refresh
```
API call needed → Check cache
→ If cached: Use token
→ If expired: Generate JWT
→ Exchange for installation token
→ Cache for 50 minutes
→ Make API call
```
