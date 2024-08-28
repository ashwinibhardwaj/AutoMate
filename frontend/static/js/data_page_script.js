document.addEventListener('DOMContentLoaded', function() {
    const menuIcon = document.querySelector('.menu-icon');
    const menu = document.querySelector('.menu ul');

    menuIcon.addEventListener('click', function() {
        menu.classList.toggle('hidden');
    });
});



document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('dataset-file');
    const uploadButton = document.getElementById('upload-btn');
    const nextButton = document.getElementById('next-btn');
    const messageElem = document.getElementById('message');
    const preprocessingSection = document.getElementById('preprocessing-section');
    const uploadSection = document.getElementById('upload-section');
    const progressBar = document.getElementById('progress-bar');

    if (!fileInput || !uploadButton || !nextButton || !messageElem || !uploadSection || !preprocessingSection || !progressBar) {
        console.error('One or more elements are missing');
        return;
    }

    let uploadSuccess = false; // Flag to track upload success

    // Handle file upload
    uploadButton.addEventListener('click', () => {
        const file = fileInput.files[0];
        if (!file) {
            messageElem.textContent = 'Please select a file to upload.';
            nextButton.disabled = true;
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Server response:', data);
            if (data.success) {
                messageElem.textContent = data.success;
                nextButton.disabled = false;
                uploadSuccess = true; // Mark as successful upload
                progressBar.style.width = '10%'; // Initial progress
            } else {
                messageElem.textContent = data.error;
                nextButton.disabled = true;
                uploadSuccess = false; // Mark as failed upload
            }
        })
        .catch(error => {
            console.error('Error:', error);
            messageElem.textContent = 'An unexpected error occurred. Please try again.';
            nextButton.disabled = true;
            uploadSuccess = false; // Mark as failed upload
        });
    });

    // Handle next button click
    nextButton.addEventListener('click', () => {
        if (uploadSuccess) { // Only change visibility if upload was successful
            uploadSection.style.display = 'none'; // Hide upload section
            preprocessingSection.style.display = 'block'; // Show preprocessing section
            progressBar.style.width = '35%'; // Update progress
        } else {
            messageElem.textContent = 'Please upload a file before proceeding.';
        }
    });

    // Info modal script
    const infoIcon = document.getElementById('info-icon');
    const infoModal = document.getElementById('info-modal');
    const closeBtn = document.querySelector('.info-modal .close');

    infoIcon.addEventListener('click', () => {
        infoModal.style.display = 'flex'; // Use flex for centering content
        setTimeout(() => {
            infoModal.style.opacity = 1; // Show modal with opacity
        }, 10); // Timeout to ensure display changes before opacity
    });

    closeBtn.addEventListener('click', () => {
        infoModal.style.opacity = 0; // Fade out the modal
        setTimeout(() => {
            infoModal.style.display = 'none'; // Hide modal after fade out
        }, 500); // Match the duration of the opacity transition
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const startPreprocessingBtn = document.getElementById('start-preprocessing-btn');
    const nextButton = document.getElementById('next-btn2');
    const preprocessingSection = document.getElementById('preprocessing-section');
    const modelGenerationSection = document.getElementById('model-generation-section');
    const preprocessingMessages = document.getElementById('preprocessing-messages');
    const progressBar = document.getElementById('progress-bar');
    const downloadButton = document.getElementById('downloadButton');


    if (!startPreprocessingBtn || !nextButton || !preprocessingSection || !modelGenerationSection || !preprocessingMessages || !progressBar) {
        console.error('One or more elements are missing');
        return;
    }

    // Ensure next button is initially disabled
    nextButton.disabled = true;

    // Handle form submission for preprocessing
    startPreprocessingBtn.addEventListener('click', function(event) {
        event.preventDefault();
        startPreprocessingBtn.disabled = true;

        const fileInput = document.getElementById('dataset-file');
        const file = fileInput.files[0];

        if (!file) {
            alert("Please upload a dataset first.");
            startPreprocessingBtn.disabled = false;
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        preprocessingMessages.innerHTML = "<p>Starting preprocessing...</p>";

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(uploadResult => {
            if (uploadResult.error) {
                preprocessingMessages.innerHTML = "<p>Error: " + uploadResult.error + "</p>";
                startPreprocessingBtn.disabled = false;
                return;
            }

            return fetch('/preprocess', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ file_path: uploadResult.file_path })
            });
        })
        .then(response => response.json())
        .then(preprocessResult => {
            preprocessingMessages.innerHTML = "";

            if (preprocessResult.error) {
                preprocessingMessages.innerHTML = "<p>Error: " + preprocessResult.error + "</p>";
                startPreprocessingBtn.disabled = false;
                return;
            }

            preprocessResult.messages.forEach(message => {
                const p = document.createElement('p');
                p.textContent = message;
                preprocessingMessages.appendChild(p);
            });

            if (preprocessResult.messages.includes("Data is ready for training.")) {
                nextButton.disabled = false; // Enable the next button
            }

            startPreprocessingBtn.disabled = false;
        })
        .catch(error => {
            console.error('Error:', error);
            preprocessingMessages.innerHTML = "<p>An error occurred during preprocessing.</p>";
            startPreprocessingBtn.disabled = false;
        });
    });

    // Handle the Next button click
    nextButton.addEventListener('click', () => {
        const messages = Array.from(preprocessingMessages.getElementsByTagName('p')).map(p => p.textContent);

        if (messages.includes("Data is ready for training.")) {
            preprocessingSection.style.display = 'none'; // Hide preprocessing section
            modelGenerationSection.style.display = 'block'; // Show model generation section
            progressBar.style.width = '70%'; // Update progress to 70%
        } else {
            alert('Please complete the preprocessing step before proceeding.');
        }
    });
});

document.getElementById('train-btn').addEventListener('click', function() {
    const fileInput = document.getElementById('dataset-file');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a file first.');
        return;
    }

    // Step 1: Upload the file
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(uploadResult => {
        if (uploadResult.error) {
            throw new Error(uploadResult.error);
        }

        // Step 2: Preprocess the file
        return fetch('/preprocess', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file_path: uploadResult.file_path })
        });
    })
    .then(response => response.json())
    .then(preprocessResult => {
        if (preprocessResult.error) {
            throw new Error(preprocessResult.error);
        }

        // Step 3: Train the model
        return fetch('/train', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ preprocessed_file_path: preprocessResult.preprocessed_file_path })
        });
    })
    .then(response => response.json())
    .then(trainResult => {
        if (trainResult.error) {
            throw new Error(trainResult.error);
        }

        // Step 4: Update progress bar to 100%
        document.getElementById('progress-bar').style.width = '100%';

        // Display the results
        let table = '<table>';
        table += '<thead><tr><th>Model Name</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1 Score</th><th>MSE</th><th>R2 Score</th><th>Training Time</th></tr></thead>';
        table += '<tbody>';

        trainResult.model_details.forEach(detail => {
            table += `<tr>
                <td>${detail.name}</td>
                <td>${detail.accuracy ? detail.accuracy.toFixed(2) : 'N/A'}</td>
                <td>${detail.precision ? detail.precision.toFixed(2) : 'N/A'}</td>
                <td>${detail.recall ? detail.recall.toFixed(2) : 'N/A'}</td>
                <td>${detail.f1_score ? detail.f1_score.toFixed(2) : 'N/A'}</td>
                <td>${detail.mse ? detail.mse.toFixed(2) : 'N/A'}</td>
                <td>${detail.r2_score ? detail.r2_score.toFixed(2) : 'N/A'}</td>
                <td>${detail.training_time} seconds</td>
            </tr>`;
        });

        table += '</tbody></table>';
        document.getElementById('model-details').innerHTML = table;

        // Best model summary
        const bestModelSummary = `
            <p><strong>Best Model:</strong> ${trainResult.best_model_name}</p>
            <p><strong>Best Model Score:</strong> ${trainResult.best_model_score.toFixed(2)}</p>
            <p><strong>Details:</strong> ${trainResult.best_model_details}</p>
        `;
        document.getElementById('best-model-summary').innerHTML = bestModelSummary;

        // Set download link for the best model
        const downloadButton = document.getElementById('downloadButton');
        downloadButton.style.display = 'block';
        const downloadfile = document.getElementById('download-btn');
        downloadfile.style.display = 'block';
        downloadButton.href = '/download_best_model';
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('model-details').innerHTML = `<p>Error: ${error.message}</p>`;
    });
});
