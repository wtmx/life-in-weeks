# Life in Weeks Visualization

This project creates a visualization of my life in weeks (updated weekly), inspired by the article ["How to Visualize the Rest of Your Life"](https://medium.com/towards-data-science/how-to-visualize-the-rest-of-your-life-28f943b1f70b) by Dr. Gregor Scheithauer. The visualization represents each week of your life as a cross, with:
- Blue crosses representing weeks I've lived
- Grey crosses representing weeks remaining
- A red cross indicating the current week

## Project Overview

This project extends the original concept by:
1. Creating an interactive visualization using Python and Altair
2. Generating a CSV file for Tableau integration
3. Automatically uploading the CSV to Google Drive
4. Enabling a live connection to Tableau Public

## Technical Setup

### Prerequisites
- Python 3.x
- Virtual environment (recommended)
- Google Cloud Console account
- Gmail account (for notifications)
- Tableau Desktop (for development)
- Tableau Public account (for publishing)

### Initial Setup

1. Clone the repository and create a virtual environment:
```bash
git clone https://github.com/wtmx/life-in-weeks.git
cd life-in-weeks
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install pandas numpy altair google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Google Drive Setup
1. Create a project in Google Cloud Console
2. Enable the Google Drive API
3. Create OAuth 2.0 credentials (Desktop application)
4. Download credentials and save as `credentials.json` in project directory
5. Add your Google account as a test user in OAuth consent screen

### Email Notification Setup
1. Create a Gmail App Password:
   - Go to your [Google Account Security settings](https://myaccount.google.com/security)
   - Enable 2-Step Verification if not already enabled
   - Go to [App Passwords](https://myaccount.google.com/apppasswords)
   - Select "Other (Custom name)" and enter "Life in Weeks"
   - Copy the generated 16-character password

2. Set up environment variables:
   ```bash
   cp .env.template .env
   ```
   Edit `.env` and add your:
   - Gmail address as `NOTIFICATION_EMAIL`
   - App Password as `NOTIFICATION_PASSWORD`

### Automation Setup

1. Create the update script:
```bash
cp update_life_weeks.sh.template update_life_weeks.sh
chmod +x update_life_weeks.sh
```

2. Set up the cron job (runs every Sunday at midnight):
```bash
crontab -e
```
Add the line:
```
0 0 * * 0 cd /path/to/life-in-weeks && ./update_life_weeks.sh
```

## Project Structure
```
life-in-weeks/
├── life.py                    # Main script for visualization and data generation
├── gdrive_upload.py          # Google Drive upload functionality
├── email_notifier.py         # Email notification functionality
├── update_life_weeks.sh      # Shell script for automated updates
├── .env                      # Environment variables (not in repo)
├── credentials.json          # Google Cloud credentials (not in repo)
├── graphs/                   # Output directory
│   ├── output.html          # Altair visualization
│   └── life_in_weeks.csv    # Data file for Tableau
└── README.md                # This file
```

## Security Notes

- Keep `credentials.json` secure and never commit to version control
- The `.env` file containing email credentials is excluded from Git
- The Google Drive file is publicly readable but not writable
- OAuth credentials are stored locally in `token.pickle`

## Monitoring and Logs

The automation process creates several log files:
- `cron.log` - Overall script execution logs
- `gdrive_upload.log` - Google Drive upload logs
- `email_notifier.log` - Email notification logs

You'll receive email notifications for:
- Successful uploads (with file ID and public URL)
- Any errors during the process (with detailed logs)

## Contributing

Feel free to fork this project and submit pull requests for improvements or bug fixes.

## Dashboard Live in Tableau Public

My life in weeks visualization is available on Tableau Public:
- [View the live dashboard](https://public.tableau.com/app/profile/wilson.teng7303/viz/MyLifeinWeeks_17384989280950/Dashboard1)

![Life in Weeks Visualization](images/tableau_viz.png)

## Acknowledgments

- Inspired by Dr. Gregor Scheithauer's Medium article
- Inspired also by Karolina Grodzinska's Tableau Public viz (https://public.tableau.com/app/profile/karolina.grodzinska/viz/Mylifeinweeks/Dashboard1)
- Built with Python, Altair, and Google Cloud Platform
- Visualization powered by Tableau Public 