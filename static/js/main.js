async function predictReview() {
    const text = document.getElementById('reviewInput').value;
    const btn = document.getElementById('predictBtn');
    const resultSection = document.getElementById('resultSection');
    const label = document.getElementById('predictionLabel');
    const confidenceBar = document.getElementById('confidenceBar');
    const confidenceValue = document.getElementById('confidenceValue');

    if (!text.trim()) {
        alert("Please enter a review.");
        return;
    }

    btn.disabled = true;
    btn.textContent = "Analyzing...";

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ review: text })
        });

        const data = await response.json();

        resultSection.classList.remove('hidden');
        label.textContent = data.prediction;

        // Reset classes
        label.className = '';
        if (data.prediction === 'Fake') {
            label.classList.add('label-fake');
            confidenceBar.style.backgroundColor = '#f44336';
        } else {
            label.classList.add('label-genuine');
            confidenceBar.style.backgroundColor = '#4caf50';
        }

        // Parse confidence string "XX.XX%" to number for width
        const confNum = parseFloat(data.confidence);
        confidenceBar.style.width = confNum + '%';
        confidenceValue.textContent = `Confidence: ${data.confidence}`;

    } catch (error) {
        console.error('Error:', error);
        alert("An error occurred during analysis.");
    } finally {
        btn.disabled = false;
        btn.textContent = "Analyze Review";
    }
}
