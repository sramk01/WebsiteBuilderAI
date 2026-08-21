// Sticky navbar gains a shadow once the page is scrolled
const mainNav = document.getElementById('mainNav');
if (mainNav) {
  const toggleNavShadow = () => {
    mainNav.classList.toggle('is-scrolled', window.scrollY > 10);
  };
  window.addEventListener('scroll', toggleNavShadow, { passive: true });
  toggleNavShadow();
}

// Smooth scroll for in-page anchor links
document.querySelectorAll('a[href^="#"]').forEach(function (link) {
  link.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// Lightweight scroll-reveal for sections (no external library)
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in-view');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.reveal').forEach((sec) => observer.observe(sec));

// Animated count-up for the stats band. Parses a leading number out of
// each stat (handles "2,143", "4.8/5", "30-Day", "100%", "24/7") and
// counts up to it when scrolled into view; non-numeric stats like
// "Lifetime" are left as static text.
function animateStatNumber(el) {
  const original = el.textContent.trim();
  const match = original.match(/^([\d,]+(?:\.\d+)?)(.*)$/);
  if (!match) return; // no leading number (e.g. "Lifetime") - leave as-is

  const target = parseFloat(match[1].replace(/,/g, ''));
  const suffix = match[2];
  const decimals = match[1].includes('.') ? match[1].split('.')[1].length : 0;
  const useComma = match[1].includes(',');
  const duration = 1200;
  const start = performance.now();

  function frame(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const current = target * eased;
    const formatted = useComma
      ? Math.round(current).toLocaleString('en-US')
      : current.toFixed(decimals);
    el.textContent = formatted + suffix;
    if (progress < 1) requestAnimationFrame(frame);
    else el.textContent = original; // snap to exact original text at the end
  }
  requestAnimationFrame(frame);
}

const statObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      animateStatNumber(entry.target);
      statObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.4 });

document.querySelectorAll('.stat-number').forEach((el) => statObserver.observe(el));
