document.getElementById("showUpdatesBtn").addEventListener("click", toggleUpdatesContainer);

document.getElementById("track-another-package-form").addEventListener("submit", function(event) {
  event.preventDefault();
  const trackInput = document.getElementById("track-input");
  const trackingNumber = trackInput.value;

  window.location.href = `/tracking_number/${trackingNumber}`;
});

function toggleUpdatesContainer() {
  const updatesContainer = document.getElementById("updatesContainer");
  const arrow = document.getElementById("arrow");
  
  if (updatesContainer.style.maxHeight) {
    // if updates container is already open, close it slowly
    updatesContainer.style.maxHeight = null;
    updatesContainer.style.transition = "max-height 0.9s ease-out";
    arrow.style.transform = "rotate(0deg)";
  } else {
    // if updates container is closed, open it slowly
    updatesContainer.style.maxHeight = updatesContainer.scrollHeight + "px";
    updatesContainer.style.transition = "max-height 0.9s ease-out";
    arrow.style.transform = "rotate(180deg)";
  }
}


function updateProgressBar(statusCode) {
  const progressBar = document.querySelector('.progress');
  const animateImage = document.querySelector('.animate-image');

  let progressWidth;
  let imagePosition;

  if (statusCode === 'delivered') {
    progressWidth = '100%';
    imagePosition = 'calc(100% - 50px)';
  } else if (statusCode === 'transit') {
    progressWidth = '50%';
    imagePosition = 'calc(50% - 25px)';
  } else {
    progressWidth = '0';
    imagePosition = '0';
  }

  progressBar.style.width = progressWidth;
  animateImage.style.left = imagePosition;
}


const showUpdatesBtn = document.getElementById("showUpdatesBtn");
showUpdatesBtn.addEventListener("click", toggleUpdatesContainer);

document.addEventListener('DOMContentLoaded', function() {
  const packageStatus = document.getElementById('progress').dataset.packageStatus;
  updateProgressBar(packageStatus);
});
