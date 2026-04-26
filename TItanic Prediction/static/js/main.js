// Prediction Form Handling
document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        pclass: document.getElementById('pclass').value,
        sex: document.getElementById('sex').value,
        age: document.getElementById('age').value,
        sibsp: document.getElementById('sibsp').value,
        parch: document.getElementById('parch').value,
        fare: document.getElementById('fare').value,
        embarked: document.getElementById('embarked').value
    };
    
    const submitBtn = e.target.querySelector('.predict-btn');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Predicting...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        displayResult(result);
    } catch (error) {
        console.error('Prediction failed:', error);
        alert('Failed to get prediction. Please try again.');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
});

function displayResult(result) {
    const resultCard = document.getElementById('resultCard');
    const circle = document.getElementById('circleProgress');
    const percentageText = document.getElementById('percentageText');
    const predictionText = document.getElementById('predictionText');
    const riskLevel = document.getElementById('riskLevel');
    const survivalProb = document.getElementById('survivalProb');
    
    resultCard.style.display = 'block';
    
    // Animate circle
    const prob = result.survival_probability;
    circle.style.stroke = result.risk_color === 'green' ? '#3fb950' : 
                          result.risk_color === 'orange' ? '#d29922' : '#f85149';
    circle.setAttribute('stroke-dasharray', `${prob}, 100`);
    
    // Animate percentage number
    animateValue(percentageText, 0, prob, 1000, '%');
    
    // Update text
    predictionText.textContent = result.survived ? 'Survived' : 'Did Not Survive';
    predictionText.style.color = result.survived ? '#3fb950' : '#f85149';
    
    riskLevel.textContent = result.risk_level;
    riskLevel.style.color = result.risk_color === 'green' ? '#3fb950' : 
                            result.risk_color === 'orange' ? '#d29922' : '#f85149';
    
    survivalProb.textContent = result.survival_probability + '%';
    
    // Scroll to result
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function animateValue(element, start, end, duration, suffix = '') {
    const range = end - start;
    const minTimer = 50;
    let stepTime = Math.abs(Math.floor(duration / range));
    stepTime = Math.max(stepTime, minTimer);
    
    let startTime = new Date().getTime();
    let endTime = startTime + duration;
    let timer;
    
    function run() {
        let now = new Date().getTime();
        let remaining = Math.max((endTime - now) / duration, 0);
        let value = Math.round(end - (remaining * range));
        element.textContent = value + suffix;
        if (value == end) {
            clearInterval(timer);
        }
    }
    
    timer = setInterval(run, stepTime);
    run();
}

// Tab Switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        const tab = btn.dataset.tab;
        document.getElementById('singleTab').style.display = tab === 'single' ? 'grid' : 'none';
        document.getElementById('csvTab').style.display = tab === 'csv' ? 'block' : 'none';
    });
});

// CSV Upload Handling
const uploadArea = document.getElementById('uploadArea');
const csvFileInput = document.getElementById('csvFileInput');
const fileNameDisplay = document.getElementById('fileName');
const uploadPredictBtn = document.getElementById('uploadPredictBtn');
let selectedFile = null;

uploadArea.addEventListener('click', () => csvFileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].name.endsWith('.csv')) {
        handleFileSelect(files[0]);
    } else {
        alert('Please upload a CSV file');
    }
});

csvFileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    selectedFile = file;
    fileNameDisplay.textContent = file.name;
    uploadPredictBtn.disabled = false;
}

uploadPredictBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    uploadPredictBtn.textContent = 'Processing...';
    uploadPredictBtn.disabled = true;
    
    try {
        const response = await fetch('/predict_csv', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        if (data.error) {
            alert(data.error);
            return;
        }
        displayCsvResults(data.results);
    } catch (error) {
        console.error('CSV prediction failed:', error);
        alert('Failed to process CSV file. Please check the format and try again.');
    } finally {
        uploadPredictBtn.textContent = 'Predict from CSV';
        uploadPredictBtn.disabled = false;
    }
});

function displayCsvResults(results) {
    const resultsSection = document.getElementById('csvResultsSection');
    const tbody = document.querySelector('#csvResultsTable tbody');
    const summary = document.getElementById('csvSummary');
    
    resultsSection.style.display = 'block';
    tbody.innerHTML = '';
    
    let survivedCount = 0;
    
    results.forEach((row, index) => {
        if (row.survived) survivedCount++;
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>${row.pclass}</td>
            <td>${row.sex}</td>
            <td>${row.age}</td>
            <td>$${row.fare}</td>
            <td>${row.survival_probability}%</td>
            <td class="${row.survived ? 'survived-yes' : 'survived-no'}">${row.survived ? 'Survived' : 'Did Not Survive'}</td>
            <td class="risk-${row.risk_color === 'green' ? 'low' : row.risk_color === 'orange' ? 'medium' : 'high'}">${row.risk_level}</td>
        `;
        tbody.appendChild(tr);
    });
    
    const total = results.length;
    const survivalRate = ((survivedCount / total) * 100).toFixed(1);
    
    summary.innerHTML = `
        <div class="summary-item"><span class="label">Total Passengers:</span><span class="value">${total}</span></div>
        <div class="summary-item"><span class="label">Predicted Survivors:</span><span class="value">${survivedCount}</span></div>
        <div class="summary-item"><span class="label">Survival Rate:</span><span class="value">${survivalRate}%</span></div>
    `;
    
    // Store for download
    window.csvResults = results;
    
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Download Results
document.getElementById('downloadResultsBtn').addEventListener('click', () => {
    if (!window.csvResults || window.csvResults.length === 0) return;
    
    const headers = ['Pclass', 'Sex', 'Age', 'SibSp', 'Parch', 'Fare', 'Embarked', 'SurvivalProbability', 'PredictedSurvival', 'RiskLevel'];
    const rows = window.csvResults.map(r => [
        r.pclass, r.sex, r.age, r.sibsp, r.parch, r.fare, r.embarked,
        r.survival_probability + '%', r.survived ? 'Yes' : 'No', r.risk_level
    ]);
    
    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'titanic_predictions.csv';
    a.click();
    URL.revokeObjectURL(url);
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // App ready
});
