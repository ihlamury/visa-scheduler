# US Visa Appointment Scheduler 🎯

An automated Python script to monitor and check for available US visa appointment slots at the Istanbul consulate. The script runs at random intervals to avoid detection and can notify you when appointments become available.

## 🌟 Features

- ✅ Automated login with captcha handling
- ✅ Security question answering
- ✅ Calendar navigation and appointment checking
- ✅ Random interval checking (50-70 minutes by default)
- ✅ Screenshot capture for debugging
- ✅ Comprehensive logging
- ✅ Notification support (Telegram, Email - optional)
- ✅ Headless browser option
- ✅ GitHub Actions support for cloud execution

## 📋 Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/ihlamury/visa-scheduler.git
cd visa-scheduler
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your details:

```env
VISA_USERNAME=your_username
VISA_PASSWORD=your_password

# Fill in all three security answers
SECURITY_ANSWER_1=your_first_car
SECURITY_ANSWER_2=where_you_met_spouse
SECURITY_ANSWER_3=your_third_answer

TARGET_MONTH=12
TARGET_YEAR=2025
```

### 5. Run the Script

```bash
python main.py
```

## 📁 Project Structure

```
visa-scheduler/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── auth.py                # Login and authentication
│   ├── appointment_checker.py # Main checking logic
│   ├── notifier.py           # Notification system
│   └── utils.py              # Helper functions
├── tests/
│   └── __init__.py
├── logs/                      # Application logs
├── screenshots/               # Debug screenshots
├── .env                       # Your credentials (not in git)
├── .env.example              # Example environment file
├── requirements.txt          # Python dependencies
├── main.py                   # Entry point
└── README.md                 # This file
```

## ⚙️ Configuration Options

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `VISA_USERNAME` | Your login username | Yes | - |
| `VISA_PASSWORD` | Your login password | Yes | - |
| `SECURITY_ANSWER_1` | Answer to first security question | Yes | - |
| `SECURITY_ANSWER_2` | Answer to second security question | Yes | - |
| `SECURITY_ANSWER_3` | Answer to third security question | Yes | - |
| `TARGET_MONTH` | Target month for appointment (1-12) | No | 12 |
| `TARGET_YEAR` | Target year for appointment | No | 2025 |
| `CHECK_INTERVAL_MIN` | Minimum minutes between checks | No | 50 |
| `CHECK_INTERVAL_MAX` | Maximum minutes between checks | No | 70 |
| `HEADLESS` | Run browser in headless mode | No | True |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING) | No | INFO |

### Notification Setup (Optional)

#### Telegram Notifications

1. Create a bot with [@BotFather](https://t.me/botfather)
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
3. Add to `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 🔍 How It Works

1. **Login**: Authenticates with username, password, and captcha
2. **Security Questions**: Answers the two randomly selected security questions
3. **Navigation**: Navigates to the appointment scheduling page
4. **Selection**: Selects Istanbul from the consular posts dropdown
5. **Checking**: Navigates through calendar months to find available slots in December 2025
6. **Notification**: Alerts you when appointments are found
7. **Wait**: Waits a random interval before checking again

## 📝 Logging

Logs are stored in the `logs/` directory with daily rotation:
- Format: `visa_scheduler_YYYYMMDD.log`
- Includes timestamps, log levels, and detailed messages
- Both file and console logging enabled

## 📸 Screenshots

Debug screenshots are automatically saved to `screenshots/` directory when:
- Login is successful
- Security questions are answered
- Appointment page is loaded
- Errors occur

## 🤖 GitHub Actions (Optional)

To run the script on GitHub's servers:

1. Go to your repository settings
2. Add repository secrets:
   - `VISA_USERNAME`
   - `VISA_PASSWORD`
   - `SECURITY_ANSWER_1`
   - `SECURITY_ANSWER_2`
   - `SECURITY_ANSWER_3`
3. Enable GitHub Actions
4. The workflow will run automatically based on the schedule

## 🛠️ Development

### Running Tests

```bash
python -m pytest tests/
```

### Debugging

Set `HEADLESS=False` in `.env` to watch the browser in action:

```env
HEADLESS=False
LOG_LEVEL=DEBUG
```

## ⚠️ Important Notes

- **Captcha**: The script will pause for manual captcha entry if needed
- **Rate Limiting**: Random intervals help avoid detection
- **Session Timeout**: The script handles session timeouts automatically
- **Legal**: Use responsibly and in accordance with the website's terms of service

## 🐛 Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   - The script auto-downloads ChromeDriver
   - Ensure Chrome browser is installed

2. **Login fails**
   - Verify credentials in `.env`
   - Check if website layout has changed

3. **Security questions not answered**
   - Ensure all three answers are in `.env`
   - Check the exact question text matches

4. **No appointments found**
   - Script is working correctly
   - Keep running, it will notify when slots appear

## 📜 License

MIT License - feel free to modify and use as needed.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⭐ Support

If this project helps you secure an appointment, please consider giving it a star!

---

**Disclaimer**: This tool is for personal use only. Use responsibly and in accordance with the visa scheduling website's terms of service.
