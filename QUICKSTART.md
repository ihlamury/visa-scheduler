# Quick Start Guide 🚀

## Immediate Next Steps

### 1. Download and Setup (5 minutes)

```bash
# On your local machine
cd ~/projects  # or wherever you keep projects
git clone https://github.com/ihlamury/visa-scheduler.git
cd visa-scheduler

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Your Credentials (2 minutes)

```bash
# Copy the example file
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

Fill in:
```env
VISA_USERNAME=yihlamur1
VISA_PASSWORD=your_actual_password
SECURITY_ANSWER_1=your_first_car_answer
SECURITY_ANSWER_2=where_you_met_spouse_answer
SECURITY_ANSWER_3=third_answer
```

### 3. Test Basic Setup (1 minute)

```bash
python main.py
```

You should see:
```
============================================================
US Visa Appointment Scheduler Starting
============================================================
Configuration validated successfully
Target: ISTANBUL - 12/2025
Check interval: 50-70 minutes
Setup complete. Ready to implement checking logic.
```

## What We Have So Far ✅

1. **Project Structure**: All folders and base files
2. **Configuration Management**: Loads your credentials securely
3. **Logging System**: Tracks everything that happens
4. **Utility Functions**: Helper functions for driver setup, screenshots, etc.
5. **Documentation**: Comprehensive README and guides

## What We Need to Build Next 🔨

### Phase 2: Authentication (Most Important)

We need to inspect the actual HTML elements of the login page. Here's how to help:

#### Option A: Use Browser DevTools

1. Open https://www.usvisascheduling.com/ in Chrome
2. Right-click on username field → Inspect
3. Copy the HTML or take screenshots of:
   - Username input element
   - Password input element
   - Captcha input element
   - Sign In button
   - Security question labels
   - Security answer inputs
   - Continue button

#### Option B: Share More Screenshots

Take screenshots of:
1. The HTML inspector showing element IDs/names for username field
2. The HTML inspector showing element IDs/names for password field
3. The security questions page with inspector open

### Why This Matters

Selenium needs exact selectors like:
- `id="username"`
- `name="password"`
- `class="captcha-input"`

Without these, we can't automate the login.

## Development Approach 🎯

We're taking a **step-by-step** approach:

```
Phase 1: Setup ✅ (DONE)
    ↓
Phase 2: Authentication 🔨 (NEXT)
    ↓
Phase 3: Appointment Checking
    ↓
Phase 4: Notification System
    ↓
Phase 5: Main Loop
    ↓
Phase 6: Testing
    ↓
Phase 7: Deployment
```

## How to Provide Element Information

### Method 1: Screenshot with Inspector
1. Open the login page
2. Press F12 to open DevTools
3. Click the inspector tool (top-left icon)
4. Click on the username field
5. Take a screenshot showing the HTML in DevTools
6. Repeat for all important elements

### Method 2: Copy HTML
1. Right-click on element → Inspect
2. In DevTools, right-click the highlighted HTML
3. Copy → Copy outerHTML
4. Paste into a text file and share

### Method 3: Use Console
Open browser console (F12) and run:
```javascript
// Find all input fields
document.querySelectorAll('input').forEach((el, i) => {
    console.log(`Input ${i}:`, {
        id: el.id,
        name: el.name,
        type: el.type,
        class: el.className
    });
});

// Find all buttons
document.querySelectorAll('button').forEach((el, i) => {
    console.log(`Button ${i}:`, el.textContent, {
        id: el.id,
        class: el.className
    });
});
```

Copy the console output and share it.

## Next Steps for You 👨‍💻

1. **Clone the repo** to your GitHub
2. **Set up locally** following steps above
3. **Gather element information** using one of the methods above
4. **Share the information** so we can implement auth.py
5. **Test the authentication** once implemented
6. **Move to next phase**

## Questions to Consider 🤔

1. **Captcha**: Is it a simple text captcha or reCAPTCHA?
   - Simple text: We can use OCR
   - reCAPTCHA: May need manual entry or 2Captcha service

2. **Security Questions**: What is the 3rd possible question?
   - We have: "What was your first car?" and "Where did you meet your spouse?"
   - Need to know the third one

3. **Browser Preference**: Should we run headless or visible?
   - Visible: Good for debugging
   - Headless: Better for production/server

## Ready to Continue? 🎯

Reply with:
- A) Element information (IDs, names, classes) from the login page
- B) Questions about the approach
- C) Request to implement a specific component
- D) Any issues you're encountering

Let's build this together, one step at a time! 💪
