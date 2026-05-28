// app.js

// 1. Import the modern Firebase modules directly from the web
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-app.js";
import { getDatabase, ref, onValue } from "https://www.gstatic.com/firebasejs/10.8.1/firebase-database.js";

// 2. Firebase Configuration
const firebaseConfig = {
    apiKey: "AIzaSyA3iSD2P6rrysE93uOD1i_o3QcGfGS_sjU",
    authDomain: "stick-ai-system.firebaseapp.com",
    databaseURL: "https://stick-ai-system-default-rtdb.europe-west1.firebasedatabase.app",
    projectId: "stick-ai-system",
    storageBucket: "stick-ai-system.firebasestorage.app",
    messagingSenderId: "174536136776",
    appId: "1:174536136776:web:517dd123c2e3d443cae07d"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

// Point to the exact path your Python script is updating
const sensorRef = ref(db, 'sensors');

// Global Chart Defaults to match your dark UI
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = '#334155';

const maxDataPoints = 15; // Keeps the chart from getting too crowded
let lastKnownBPM = null; 

// --- 3. Setup Empty Heart Rate Chart ---
const hrChart = new Chart(document.getElementById('heartRateChart').getContext('2d'), {
    type: 'line',
    data: { 
        labels: [], 
        datasets: [{ 
            label: 'Heart Rate (BPM)', 
            borderColor: '#ef4444', 
            backgroundColor: 'rgba(239, 68, 68, 0.1)', 
            data: [], 
            tension: 0.4, 
            fill: true, 
            pointRadius: 4, 
            pointBackgroundColor: '#ef4444' 
        }] 
    },
    options: { responsive: true, scales: { y: { min: 40, max: 150 } }, animation: { duration: 500 } }
});

// --- 4. Setup Empty Motion Chart ---
const motionChart = new Chart(document.getElementById('motionChart').getContext('2d'), {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            { label: 'X-Axis', borderColor: '#38bdf8', data: [], tension: 0.3, pointRadius: 0 },
            { label: 'Y-Axis', borderColor: '#4ade80', data: [], tension: 0.3, pointRadius: 0 },
            { label: 'Z-Axis', borderColor: '#a78bfa', data: [], tension: 0.3, pointRadius: 0 }
        ]
    },
    options: { responsive: true, scales: { y: { suggestedMin: -20, suggestedMax: 20 } }, animation: { duration: 500 } }
});

// --- 5. Listen for Live Data & Update Dashboard ---
onValue(sensorRef, (snapshot) => {
    const data = snapshot.val();
    
    if (data) {
        // Get the current time for the chart labels
        const now = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});

        // ==========================================
        // AI STATUS LOGIC
        // ==========================================
        if (data.status) {
            const statusElement = document.getElementById("ai-status");
            if (statusElement) {
                statusElement.innerText = data.status;

                // Change colors dynamically based on the alert level
                if (data.status.includes("Walking")) {
                    statusElement.className = "status-safe";
                } else if (data.status.includes("Drop")) {
                    statusElement.className = "status-warning";
                } else if (data.status.includes("FALL")) {
                    statusElement.className = "status-danger";
                } else {
                    statusElement.className = "";
                }
            }
        }

        // ==========================================
        // HEART RATE LOGIC
        // ==========================================
        if (data.heartRate !== undefined && data.heartRate > 40) {
            lastKnownBPM = data.heartRate;
            const bpmElement = document.getElementById('big-bpm');
            if (bpmElement) bpmElement.innerText = `${lastKnownBPM} BPM`;
        }
        
        hrChart.data.labels.push(now);
        hrChart.data.datasets[0].data.push(lastKnownBPM);
        
        if (hrChart.data.labels.length > maxDataPoints) {
            hrChart.data.labels.shift();
            hrChart.data.datasets[0].data.shift();
        }
        hrChart.update();

        // ==========================================
        // MOTION (IMU) LOGIC
        // ==========================================
        motionChart.data.labels.push(now);
        motionChart.data.datasets[0].data.push(data.accelX !== undefined ? data.accelX : 0);
        motionChart.data.datasets[1].data.push(data.accelY !== undefined ? data.accelY : 0);
        motionChart.data.datasets[2].data.push(data.accelZ !== undefined ? data.accelZ : 0);
        
        if (motionChart.data.labels.length > maxDataPoints) {
            motionChart.data.labels.shift();
            motionChart.data.datasets.forEach(dataset => dataset.data.shift());
        }
        motionChart.update();
    }
});
