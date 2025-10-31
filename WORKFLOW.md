# Visa Scheduler - Workflow Diagram

## 🔄 Complete Automation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     START APPLICATION                            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  INITIALIZATION                                                  │
│  • Load configuration from .env                                  │
│  • Validate credentials and settings                            │
│  • Setup logging system                                         │
│  • Initialize Chrome WebDriver                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: AUTHENTICATION                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 1: Navigate to Login Page                          │   │
│  │  • Open https://www.usvisascheduling.com/               │   │
│  │  • Wait for page load                                    │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 2: Fill Login Form                                │   │
│  │  • Enter username: yihlamur1                            │   │
│  │  • Enter password: ********                             │   │
│  │  • Handle captcha (manual or OCR)                       │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 3: Submit Login                                   │   │
│  │  • Click "Sign In" button                               │   │
│  │  • Wait for redirect                                    │   │
│  │  • Take screenshot: "login_success"                     │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 4: Security Questions                             │   │
│  │  • Detect Question 1 text                               │   │
│  │  • Match with configured answers                        │   │
│  │  • Fill Answer 1                                        │   │
│  │  • Detect Question 2 text                               │   │
│  │  • Match with configured answers                        │   │
│  │  • Fill Answer 2                                        │   │
│  │  • Click "Continue" button                              │   │
│  │  • Take screenshot: "security_questions_answered"       │   │
│  └─────────────────────────┬───────────────────────────────┘   │
└─────────────────────────────┼───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: APPOINTMENT CHECKING                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 1: Navigate to Scheduling                         │   │
│  │  • Find "Schedule Appointment" button/link              │   │
│  │  • Click and wait for page load                         │   │
│  │  • Take screenshot: "scheduling_page"                   │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 2: Select Consular Post                           │   │
│  │  • Locate "Consular Posts" dropdown                     │   │
│  │  • Click dropdown to expand                             │   │
│  │  • Select "ISTANBUL" from options                       │   │
│  │  • Wait for calendar to appear                          │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 3: Navigate Calendar                              │   │
│  │  • Check current month displayed                        │   │
│  │  • If not December 2025:                                │   │
│  │    - Click "Next Month" button                          │   │
│  │    - Wait for calendar update                           │   │
│  │    - Repeat until December 2025                         │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                             ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Step 4: Check Availability                             │   │
│  │  • Scan all dates in December 2025                      │   │
│  │  • Identify clickable/available dates                   │   │
│  │  • Extract date and time information                    │   │
│  │  • If appointments found:                               │   │
│  │    - Take screenshot: "appointments_found"              │   │
│  │    - Log appointment details                            │   │
│  │    - Trigger notifications                              │   │
│  │  • If no appointments:                                  │   │
│  │    - Log: "No appointments available"                   │   │
│  └─────────────────────────┬───────────────────────────────┘   │
└─────────────────────────────┼───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 3: NOTIFICATION (If Appointments Found)                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • Format appointment information                       │   │
│  │  • Send Telegram message (if configured)                │   │
│  │  • Send Email alert (if configured)                     │   │
│  │  • Log to file                                          │   │
│  │  • Save screenshot                                      │   │
│  └─────────────────────────┬───────────────────────────────┘   │
└─────────────────────────────┼───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  CLEANUP & WAIT                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • Close browser/cleanup resources                      │   │
│  │  • Calculate random wait time (50-70 minutes)           │   │
│  │  • Log: "Waiting X minutes until next check"            │   │
│  │  • Sleep for calculated duration                        │   │
│  └─────────────────────────┬───────────────────────────────┘   │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  LOOP BACK TO   │
                    │  INITIALIZATION │
                    └─────────────────┘

```

## 🎯 Key Decision Points

### 1. Captcha Handling
```
Captcha Detected
    │
    ├─→ Simple Text Captcha
    │   └─→ Use Pillow + pytesseract (OCR)
    │
    ├─→ reCAPTCHA
    │   ├─→ Manual Entry (pause for user)
    │   └─→ 2Captcha Service (paid)
    │
    └─→ No Captcha
        └─→ Continue automatically
```

### 2. Security Question Matching
```
Read Question Text
    │
    ├─→ Contains "first car"
    │   └─→ Use SECURITY_ANSWER_1
    │
    ├─→ Contains "meet" and "spouse"
    │   └─→ Use SECURITY_ANSWER_2
    │
    └─→ Contains [third question pattern]
        └─→ Use SECURITY_ANSWER_3
```

### 3. Appointment Found Action
```
Appointments Detected
    │
    ├─→ Send Notifications
    │   ├─→ Telegram
    │   ├─→ Email
    │   └─→ Log
    │
    ├─→ Save Screenshot
    │
    └─→ Options:
        ├─→ Continue checking (monitor for better dates)
        ├─→ Stop (alert only)
        └─→ Auto-book (future feature)
```

## 📊 Error Handling Flow

```
┌──────────────────┐
│  Action Attempt  │
└────────┬─────────┘
         │
         ▼
    ┌─────────┐
    │ Success?│
    └────┬────┘
         │
         ├─→ YES ──→ Continue to next step
         │
         └─→ NO
             │
             ▼
    ┌──────────────────┐
    │ Error Type?      │
    └────┬─────────────┘
         │
         ├─→ Timeout
         │   ├─→ Save screenshot
         │   ├─→ Log error
         │   └─→ Retry (max 3 times)
         │
         ├─→ Element Not Found
         │   ├─→ Save screenshot
         │   ├─→ Log error
         │   ├─→ Check if page changed
         │   └─→ Retry with alternate selector
         │
         ├─→ Session Expired
         │   ├─→ Log out
         │   └─→ Restart from login
         │
         └─→ Network Error
             ├─→ Wait 30 seconds
             └─→ Restart entire process
```

## 🔐 Security & Best Practices

1. **Credential Protection**
   - Never commit .env file
   - Use environment variables
   - Encrypt sensitive data if needed

2. **Rate Limiting**
   - Random intervals (50-70 minutes)
   - Mimic human behavior
   - Add random pauses between actions

3. **Error Resilience**
   - Try/except blocks around all operations
   - Screenshot on errors
   - Automatic retry logic
   - Graceful degradation

4. **Logging**
   - Log all actions
   - Timestamp everything
   - Include context in errors
   - Daily log rotation

## 🚀 Execution Modes

### Mode 1: Local Development
```
python main.py
```
- Visible browser for debugging
- Console output in real-time
- Easy to interrupt and modify

### Mode 2: Production Local
```
HEADLESS=True python main.py
```
- Headless browser
- Background execution
- Minimal resource usage

### Mode 3: Server/VPS
```
nohup python main.py > output.log 2>&1 &
```
- Runs in background
- Continues after logout
- Redirects output to file

### Mode 4: Screen/Tmux
```
screen -S visa-scheduler
python main.py
# Ctrl+A, D to detach
```
- Persistent session
- Can reattach anytime
- Multiple windows support

## 📈 Monitoring Dashboard (Future)

```
┌─────────────────────────────────────────────┐
│  Visa Scheduler - Status Dashboard          │
├─────────────────────────────────────────────┤
│  Status: 🟢 Running                          │
│  Uptime: 3 days, 5 hours                    │
│  Last Check: 2 minutes ago                  │
│  Next Check: in 58 minutes                  │
│                                             │
│  Statistics:                                │
│  • Total Checks: 87                         │
│  • Successful: 85 (97.7%)                   │
│  • Errors: 2 (2.3%)                         │
│  • Appointments Found: 0                    │
│                                             │
│  Recent Activity:                           │
│  10:45 AM - Checked December 2025           │
│  10:44 AM - Selected ISTANBUL               │
│  10:43 AM - Logged in successfully          │
│  09:32 AM - Checked December 2025           │
└─────────────────────────────────────────────┘
```

This completes the workflow documentation!
