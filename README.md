# Titanic Survival Prediction

A full-stack web application that predicts Titanic passenger survival using Machine Learning. Built with Flask backend and HTML/CSS/JS frontend.

## Features

- **Single Prediction**: Enter passenger details to get survival probability
- **CSV Batch Upload**: Upload a CSV file with multiple passengers and get predictions for all
- **Drag & Drop**: Easy CSV file upload with drag and drop support
- **Download Results**: Export prediction results as CSV

## Project Structure

```
Titanic Prediction/
├── app.py                  # Flask backend with ML model
├── requirements.txt        # Python dependencies
├── run.bat                 # Windows startup script
├── run.sh                  # Linux/Mac startup script
├── README.md               # This file
├── templates/
│   └── index.html          # Main page
├── static/
│   ├── css/
│   │   └── style.css       # Styling
│   ├── js/
│   │   └── main.js         # Frontend logic
│   └── images/             # Image assets
├── model/                  # Saved ML model (auto-generated)
└── data/                   # Data files
```

## Requirements

- Python 3.9 or higher
- pip

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

Or directly:
```bash
python app.py
```

3. Open your browser and go to `http://localhost:5000`

## Manual Deployment

### Option 1: PythonAnywhere (Recommended for Beginners)

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Go to **Files** and upload all project files
3. Open a **Bash console** and run:
```bash
pip install --user -r requirements.txt
```
4. Go to **Web** tab, click **Add a new web app**
5. Select **Manual configuration** and **Python 3.10**
6. Set the working directory to your project folder
7. Set the WSGI file to point to `app.py`
8. Reload the web app

### Option 2: VPS / Dedicated Server

1. Upload all files to your server using FTP or SCP
2. Install Python and pip if not already installed
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run with Gunicorn for production:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Option 3: Shared Hosting (cPanel)

1. Zip all project files (except `venv/`, `.git/`, `__pycache__/`, `model/*.pkl`)
2. Upload via cPanel File Manager to your `public_html` or application folder
3. Set up a Python app in cPanel (if supported)
4. Point the app to `app.py`
5. Install requirements via SSH or cPanel terminal

## CSV Upload Format

Your CSV file should have these columns:

```csv
Pclass,Sex,Age,SibSp,Parch,Fare,Embarked
1,male,22,1,0,7.25,S
3,female,26,0,0,8.05,S
```

- **Pclass**: 1, 2, or 3
- **Sex**: male or female
- **Age**: Number
- **SibSp**: Siblings/Spouses aboard
- **Parch**: Parents/Children aboard
- **Fare**: Ticket fare
- **Embarked**: S (Southampton), C (Cherbourg), or Q (Queenstown)

## Model Details

The app uses a Random Forest classifier trained on synthetic data based on known Titanic survival patterns:
- Higher class passengers had better survival rates
- Women and children were prioritized
- Higher fares correlated with better outcomes

## License

Open source - free to use and modify.
