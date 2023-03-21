const trackLink = document.querySelector('#track-link');
const aboutLink = document.querySelector('#about-link');
const trackArea = document.querySelector('#track-area');
const body = document.querySelector('body');
const aboutArea = document.querySelector('#about');
const motto = document.querySelector('#motto');

trackLink.addEventListener('click', (e) => {
    e.preventDefault();
    trackArea.classList.toggle('hidden');
    trackArea.classList.toggle('show');
    motto.classList.toggle('hidden');
    motto.classList.toggle('show');
    body.classList.toggle('no-scroll');
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
