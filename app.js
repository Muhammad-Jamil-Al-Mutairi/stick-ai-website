// app.js

// 1. Heart Rate Chart Setup
const ctxHeart = document.getElementById('heartRateChart').getContext('2d');
const heartRateChart = new Chart(ctxHeart, {
    type: 'line',
    data: {
        labels: ['10s', '8s', '6s', '4s', '2s', 'Now'],
        datasets: [{
            label: 'Heart Rate (BPM)',
            data: [72, 74, 73, 75, 74, 76], // Mock pulse data
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231, 76, 60, 0.2)',
            borderWidth: 2,
            tension: 0.4, // Makes the line curve smoothly
            fill: true
        }]
    },
    options: {
        responsive: true,
        plugins: { title: { display: true, text: 'MAX30102 PPG Sensor' } },
        scales: { y: { suggestedMin: 60, suggestedMax: 100 } }
    }
});

// 2. Motion (IMU) Chart Setup
const ctxMotion = document.getElementById('motionChart').getContext('2d');
const motionChart = new Chart(ctxMotion, {
    type: 'line',
    data: {
        labels: ['10s', '8s', '6s', '4s', '2s', 'Now'],
        datasets: [
            { label: 'Accel X', data: [0.1, 0.2, 0.1, -0.1, 0.0, 0.1], borderColor: '#3498db', tension: 0.1 },
            { label: 'Accel Y', data: [9.8, 9.7, 9.8, 9.9, 9.8, 9.8], borderColor: '#2ecc71', tension: 0.1 },
            { label: 'Accel Z', data: [-0.2, -0.1, 0.0, 0.1, 0.0, -0.1], borderColor: '#f1c40f', tension: 0.1 }
        ]
    },
    options: {
        responsive: true,
        plugins: { title: { display: true, text: 'MPU-6050 Accelerometer (g)' } }
    }
});