
document.getElementById("showUpdatesBtn").addEventListener("click", function() {
    var updatesContainer = document.getElementById("updatesContainer");
    var arrow = document.getElementById("arrow");
if (updatesContainer.style.maxHeight) {
    updatesContainer.style.maxHeight = null;
    arrow.style.transform = "rotate(0deg)";
}else {
    updatesContainer.style.maxHeight = updatesContainer.scrollHeight + "px";
    arrow.style.transform = "rotate(180deg)";
}
});
