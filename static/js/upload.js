document.addEventListener("DOMContentLoaded", function () {
  // --- Info Modal Code ---
  const infoIcon = document.getElementById('info-icon');
  const infoModal = document.getElementById('info-modal');
  const closeBtn = document.querySelector('.info-modal .close');

  if (infoIcon && infoModal && closeBtn) {
    infoIcon.addEventListener('click', () => {
      infoModal.style.display = 'flex';
      setTimeout(() => {
        infoModal.style.opacity = 1;
      }, 10);
    });

    closeBtn.addEventListener('click', () => {
      infoModal.style.opacity = 0;
      setTimeout(() => {
        infoModal.style.display = 'none';
      }, 500);
    });
  }

  // --- Upload Section: AJAX file upload ---
  const uploadForm = document.getElementById('file-upload-form');
  uploadForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const messageArea = document.getElementById('message-area');
    messageArea.innerHTML = '';

    const formData = new FormData(this);

    fetch("{{ url_for('upload_file') }}", {
      method: "POST",
      body: formData
    })
      .then(response => response.json().then(data => ({ status: response.status, body: data })))
      .then(result => {
        if (result.status === 200) {
          messageArea.innerHTML = '<div class="message success">' + result.body.message + '</div>';
          window.uploadedFilename = result.body.filename;
          document.getElementById('upload-section').classList.remove('active');
          document.getElementById('preprocessing-section').classList.add('active');
        } else {
          messageArea.innerHTML = '<div class="message error">' + result.body.error + '</div>';
        }
      })
      .catch(error => {
        console.error("Upload error:", error);
        messageArea.innerHTML = '<div class="message error">An unexpected error occurred.</div>';
      });
  });

  // --- Preprocessing Section: AJAX call to /preprocess ---
  const preprocessBtn = document.getElementById('preprocess-btn');
  preprocessBtn.addEventListener('click', function () {
    const preprocessMessage = document.getElementById('preprocess-message');
    const preprocessLogs = document.getElementById('preprocess-logs');
    const nextToTrainingBtn = document.getElementById('training');

    preprocessMessage.innerHTML = '<div class="message info">Preprocessing started...</div>';
    preprocessLogs.innerHTML = '';
    nextToTrainingBtn.disabled = true;

    fetch("{{ url_for('preprocess_file') }}", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename: window.uploadedFilename })
    })
      .then(response => response.json().then(data => ({ status: response.status, body: data })))
      .then(result => {
        if (result.status === 200) {
          preprocessMessage.innerHTML += '<div class="message success">' + result.body.message + '</div>';

          let logs = result.body.logs;
          let index = 0;

          function displayNextLog() {
            if (index < logs.length) {
              let logItem = document.createElement('div');
              logItem.className = 'log-entry';
              logItem.textContent = logs[index];
              preprocessLogs.appendChild(logItem);

              setTimeout(() => {
                logItem.classList.add('show');
              }, 10);

              preprocessLogs.scrollTop = preprocessLogs.scrollHeight;
              index++;
              setTimeout(displayNextLog, 800);
            } else {
              const downloadLink = document.getElementById('download-link');
              downloadLink.href = result.body.download_url;
              downloadLink.style.display = 'inline-block';
              nextToTrainingBtn.disabled = false;
            }
          }

          displayNextLog();
        } else {
          preprocessMessage.innerHTML = '<div class="message error">' + result.body.error + '</div>';
        }
      })
      .catch(error => {
        console.error("Preprocessing error:", error);
        preprocessMessage.innerHTML = '<div class="message error">An unexpected error occurred during preprocessing.</div>';
      });
  });

  // --- Next Button: Transition to Training Section ---
  const trainingTransitionBtn = document.getElementById('training');
  trainingTransitionBtn.addEventListener('click', function () {
    document.getElementById('preprocessing-section').classList.remove('active');
    document.getElementById('training-section').classList.add('active');
    document.getElementById('training-section').scrollIntoView({ behavior: 'smooth' });
  });

  // --- Training Section: Trigger Model Training ---
  const trainModelBtn = document.getElementById('train-model-btn');
  const downloadModelBtn = document.getElementById('download-model-btn');
  

  if (trainModelBtn) {
    trainModelBtn.addEventListener('click', function() {
      const trainingLogs = document.getElementById('training-logs');
      const bestModelDetails = document.getElementById('best-model-details');
      const modelMetrics = document.getElementById('model-metrics');

      trainingLogs.innerHTML = '<div class="message info">Training started... Please wait.</div>';
      bestModelDetails.innerHTML = '';
      modelMetrics.innerHTML = '';

      const preprocessedFilePath = 'path/to/preprocessed.csv';

      fetch("{{ url_for('start_training') }}", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ preprocessed_file_path: preprocessedFilePath })
      })
      .then(response => response.json())
      .then(data => {
        if (data.error) {
          trainingLogs.innerHTML = `<div class="message error">${data.error}</div>`;
          return;
        }

        trainingLogs.innerHTML = '<div class="message success">Training completed successfully.</div>';
        downloadModelBtn.style.display = 'inline-block';
        downloadModelBtn.href = "{{ url_for('download_best_model') }}";

        bestModelDetails.innerHTML = `
          <h2>Best Model: ${data.best_model_name}</h2>
          <p>${data.best_model_details}</p>
          <p>Score: ${data.best_model_score}</p>
        `;

        let tableHTML = `
          <table class="metrics-table">
            <thead>
              <tr>
                <th>Model</th>
                <th>${data.model_details[0].accuracy !== undefined ? 'Accuracy' : 'MSE'}</th>
                <th>${data.model_details[0].precision !== undefined ? 'Precision' : 'R2 Score'}</th>
                <th>Training Time (s)</th>
              </tr>
            </thead>
            <tbody>
        `;

        data.model_details.forEach(model => {
          if (model.accuracy !== undefined) {
            tableHTML += `
              <tr>
                <td>${model.name}</td>
                <td>${model.accuracy}</td>
                <td>${model.precision}</td>
                <td>${model.training_time}</td>
              </tr>
            `;
          } else {
            tableHTML += `
              <tr>
                <td>${model.name}</td>
                <td>${model.mse}</td>
                <td>${model.r2_score}</td>
                <td>${model.training_time}</td>
              </tr>
            `;
          }
          
        });

        tableHTML += '</tbody></table>';
        modelMetrics.innerHTML = tableHTML;

        // ✅ Show the download button after table is rendered
          
        
      })
      .catch(error => {
        console.error("Training error:", error);
        trainingLogs.innerHTML = '<div class="message error">An error occurred during training.</div>';
      });
    });
  }
});
