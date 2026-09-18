const bar = document.getElementById('progress');
function updateProgress() {
  const distance = document.documentElement.scrollHeight - innerHeight;
  bar.style.width = `${distance > 0 ? scrollY / distance * 100 : 0}%`;
}
addEventListener('scroll', updateProgress, { passive: true });
addEventListener('resize', updateProgress);
updateProgress();
const links = [...document.querySelectorAll('nav a')];
const observer = new IntersectionObserver(entries => {
  const visible = entries.filter(e => e.isIntersecting);
  if (!visible.length) return;
  const id = visible[0].target.id;
  links.forEach(a => a.classList.toggle('active', a.hash === '#' + id));
}, { rootMargin: '-10% 0px -70% 0px' });
document.querySelectorAll('article h2').forEach(h => observer.observe(h));
document.querySelectorAll('.mobile-toc nav a').forEach(a => a.addEventListener('click', () => {
  document.querySelector('.mobile-toc').open = false;
}));
