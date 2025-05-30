document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultsDiv = document.getElementById('results');
    const resultContent = document.getElementById('resultContent');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('Form submitted');

        // Show loading state
        submitBtn.disabled = true;
        btnText.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');
        resultsDiv.classList.add('hidden');

        try {
            const formData = new FormData(form);
            console.log('Sending request to /upload');

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            console.log('Response received:', response.status);
            const data = await response.json();
            console.log('Response data:', data);

            if (data.success) {
                resultContent.innerHTML = `
                    <div class='text-white'>
                        <div class='mb-4'>
                            <h4 class='text-xl font-bold text-purple-300'>Classification</h4>
                            <p>Format: ${data.classification.format}</p>
                            <p>Intent: ${data.classification.intent}</p>
                            <p>Confidence: ${Math.round(data.classification.confidence * 100)}%</p>
                        </div>
                        
                        <div class='mb-4'>
                            <h4 class='text-xl font-bold text-purple-300'>Extracted Data</h4>
                            <pre class='bg-gray-800 p-4 rounded-lg overflow-auto'>${JSON.stringify(data.result, null, 2)}</pre>
                        </div>
                        
                        ${data.actions ? `
                            <div class='mb-4'>
                                <h4 class='text-xl font-bold text-purple-300'>Actions Taken</h4>
                                <ul class='list-disc list-inside'>
                                    ${data.actions.actions.map(action => `
                                        <li>${action.service}: ${action.action} - ${action.status}</li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                `;
            } else {
                resultContent.innerHTML = `
                    <div class='text-red-500'>
                        <h4 class='text-xl font-bold'>Error</h4>
                        <p>${data.error || 'An unknown error occurred'}</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error:', error);
            resultContent.innerHTML = `
                <div class="text-red-500">
                    <h3 class="text-xl font-bold">Error</h3>
                    <p>${error.message}</p>
                </div>
            `;
        } finally {
            // Reset loading state
            submitBtn.disabled = false;
            btnText.classList.remove('hidden');
            loadingSpinner.classList.add('hidden');
            resultsDiv.classList.remove('hidden');
        }
    });
});
