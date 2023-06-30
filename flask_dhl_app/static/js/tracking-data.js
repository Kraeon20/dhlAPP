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


  const statusCodeVariable = document.getElementById("statusCode");
  const progressBar = document.getElementById("progress-bar");
  
  if (statusCodeVariable && progressBar) {
    console.log(statusCodeVariable.innerHTML);
    const display = statusCodeVariable.innerHTML;
  
    let progressWidth;
  
  //   if (display === 'delivered') {
  //     console.log('MOVE')
  //     progressBar.style.width = '90%';
  //     progressWidth = '100%';
  //   } else {
  //     progressBar.style.width = '0%';
  //     console.log('STAY');
  //     progressWidth = 0;
  //   }
  // } else {
  //   if (!statusCodeVariable) {
  //     console.error('Error: Cannot find the "statusCode" element.');
  //   }
  //   if (!progressBar) {
  //     console.error('Error: Cannot find the "progress-bar" element.');
  //   }
  }
  


}

document.addEventListener('DOMContentLoaded', function() {
  const packageStatus = '{{ packageStatus }}';
  updateProgressBar(packageStatus);
});



// Function to update the current date and time
function updateDateTime() {
  const dateTimeElement = document.getElementById('currentDateTime');
  const currentDate = new Date();
  const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
  const formattedDate = currentDate.toLocaleDateString('en-US', options);
  const formattedTime = currentDate.toLocaleTimeString('en-US', { hour12: true, hour: 'numeric', minute: '2-digit', second: '2-digit' });
  dateTimeElement.innerHTML = `${formattedDate}<br>${formattedTime}`;

}

// Call the updateDateTime function initially to set the date and time
updateDateTime();

// Update the date and time every second
setInterval(updateDateTime, 1000);
