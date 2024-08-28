document.getElementById('uploadButton').addEventListener('click', () => {
    const fileInput = document.getElementById('fileInput');
    const message = document.getElementById('message');
    const downloadButton = document.getElementById('downloadButton');
    const modelDetails = document.getElementById('modelDetails');
    const bestModelName = document.getElementById('bestModelName');
    const bestModelScore = document.getElementById('bestModelScore');
    const bestModelDetails = document.getElementById('bestModelDetails');
    const modelList = document.getElementById('modelList');

    if (fileInput.files.length === 0) {
        message.textContent = 'Please select a file to upload';
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            message.textContent = `Success! Best model score: ${data.best_model_score.toFixed(2)}`;
            bestModelName.textContent = `Best Model: ${data.best_model_name}`;
            bestModelScore.textContent = `Best Model Score: ${data.best_model_score.toFixed(2)}`;
            bestModelDetails.textContent = `Details: ${data.best_model_details}`;

            // Populate the table with model details
            modelList.innerHTML = '';
            data.model_details.forEach(model => {
                const row = document.createElement('tr');
                row.classList.add('fade-in');
                row.innerHTML = `
                    <td>${model.name}</td>
                    <td>${model.accuracy.toFixed(2)}</td>
                    <td>${model.precision.toFixed(2)}</td>
                    <td>${model.recall.toFixed(2)}</td>
                    <td>${model.f1_score.toFixed(2)}</td>
                    <td>${model.training_time.toFixed(2)} seconds</td>
                `;
                modelList.appendChild(row);
            });

            modelDetails.style.display = 'block';
            downloadButton.style.display = 'block';
            downloadButton.href = '/download_best_model';
        } else {
            message.textContent = `Error: ${data.error}`;
        }
    })
    .catch(error => {
        message.textContent = 'Error uploading file';
        console.error('Error:', error);
    });
});



// info model js
// Get the info icon and modal elements
const infoIcon = document.getElementById('info-icon');
const infoModal = document.getElementById('info-modal');

// Add an event listener to the info icon to toggle the modal
infoIcon.addEventListener('click', () => {
  // Display the modal
  infoModal.style.display = 'block';
  // Reset the opacity for showing the modal again
  infoModal.style.opacity = 1;
});

// Add an event listener to the close button to toggle the modal
document.querySelector('.close').addEventListener('click', () => {
  // Add a fade-out effect to the modal
  infoModal.style.opacity = 0;
  setTimeout(() => {
    infoModal.style.display = 'none';
  }, 500);
});
