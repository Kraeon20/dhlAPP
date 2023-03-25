const trackMottoButton = document.querySelector('#track-motto-button');
const aboutLink = document.querySelector('#about-link');
const trackArea = document.querySelector('#track-area');
const body = document.querySelector('body');
const aboutArea = document.querySelector('#about');
const motto = document.querySelector('#motto');

trackMottoButton.addEventListener('click', (e) => {
    e.preventDefault();
    toggleTrackArea();
    trackMottoButton.classList.add('hidden');
});

aboutLink.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({ top: aboutArea.offsetTop - 60, behavior: 'smooth' });
});

window.addEventListener('scroll', () => {
    if (window.scrollY > 0) {
        aboutArea.classList.remove('hidden');
    } else {
        aboutArea.classList.add('hidden');
    }
});

function toggleTrackArea() {
    if (trackArea.classList.contains('hidden')) {
        motto.style.opacity = '0';
        motto.classList.add('hidden');
        setTimeout(() => {
            trackArea.style.opacity = '1';
            trackArea.classList.remove('hidden');
        }, 300);
    } else {
        trackArea.style.opacity = '0';
        trackArea.classList.add('hidden');
        setTimeout(() => {
            motto.style.opacity = '1';
            motto.classList.remove('hidden');
            trackMottoButton.classList.remove('hidden');
        }, 300);
    }
}
