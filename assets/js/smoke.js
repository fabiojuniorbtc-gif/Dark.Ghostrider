/**
 * DARK GHOSTRIDER - REALISTIC CANVAS SMOKE & AUDIO ENGINE
 */

class SmokeEngine {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.particles = [];
    this.numParticles = 55;
    this.width = window.innerWidth;
    this.height = window.innerHeight;
    this.mouseX = this.width / 2;
    this.mouseY = this.height / 2;
    this.isRunning = true;

    this.resize();
    window.addEventListener('resize', () => this.resize());
    window.addEventListener('mousemove', (e) => {
      this.mouseX = e.clientX;
      this.mouseY = e.clientY;
    });

    this.initParticles();
    this.animate();
  }

  resize() {
    this.width = window.innerWidth;
    this.height = window.innerHeight;
    this.canvas.width = this.width;
    this.canvas.height = this.height;
  }

  initParticles() {
    this.particles = [];
    for (let i = 0; i < this.numParticles; i++) {
      this.particles.push(this.createParticle(true));
    }
  }

  createParticle(randomY = false) {
    return {
      x: Math.random() * this.width,
      y: randomY ? Math.random() * this.height : this.height + Math.random() * 80,
      vx: (Math.random() - 0.5) * 1.2,
      vy: -(Math.random() * 1.8 + 0.8), // Rising up
      radius: Math.random() * 90 + 70,
      maxRadius: Math.random() * 220 + 160,
      growthRate: Math.random() * 0.4 + 0.2,
      alpha: Math.random() * 0.35 + 0.08,
      initialAlpha: Math.random() * 0.35 + 0.08,
      rotation: Math.random() * Math.PI * 2,
      rotSpeed: (Math.random() - 0.5) * 0.015,
      // Hue tint: subtle dark crimson red to dark charcoal
      tint: Math.random() > 0.7 ? 'yellow' : (Math.random() > 0.5 ? 'red' : 'charcoal')
    };
  }

  animate() {
    if (!this.isRunning) return;

    this.ctx.clearRect(0, 0, this.width, this.height);

    for (let i = 0; i < this.particles.length; i++) {
      const p = this.particles[i];

      p.x += p.vx + (this.mouseX - this.width / 2) * 0.0003;
      p.y += p.vy;
      p.rotation += p.rotSpeed;

      if (p.radius < p.maxRadius) {
        p.radius += p.growthRate;
      }

      // Fade out as it climbs to the top
      const lifeProgress = p.y / this.height;
      p.alpha = p.initialAlpha * Math.max(0, Math.min(1, lifeProgress));

      this.ctx.save();
      this.ctx.translate(p.x, p.y);
      this.ctx.rotate(p.rotation);

      // Create radial gradient for soft puff
      const grad = this.ctx.createRadialGradient(0, 0, 0, 0, 0, p.radius);
      if (p.tint === 'yellow') {
        grad.addColorStop(0, `rgba(255, 230, 0, ${p.alpha * 0.45})`);
        grad.addColorStop(0.4, `rgba(220, 180, 0, ${p.alpha * 0.22})`);
        grad.addColorStop(1, 'rgba(10, 10, 15, 0)');
      } else if (p.tint === 'red') {
        grad.addColorStop(0, `rgba(230, 20, 38, ${p.alpha * 0.45})`);
        grad.addColorStop(0.4, `rgba(180, 15, 25, ${p.alpha * 0.25})`);
        grad.addColorStop(1, 'rgba(10, 10, 15, 0)');
      } else {
        grad.addColorStop(0, `rgba(45, 48, 60, ${p.alpha * 0.6})`);
        grad.addColorStop(0.5, `rgba(22, 24, 32, ${p.alpha * 0.3})`);
        grad.addColorStop(1, 'rgba(8, 8, 10, 0)');
      }

      this.ctx.fillStyle = grad;
      this.ctx.beginPath();
      this.ctx.arc(0, 0, p.radius, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.restore();

      // Recycle particle when off screen
      if (p.y + p.radius < 0 || p.alpha <= 0.005) {
        this.particles[i] = this.createParticle(false);
      }
    }

    requestAnimationFrame(() => this.animate());
  }

  stop() {
    this.isRunning = false;
  }
}

// Audio Synthesizer for MT-07 Twin CP2 Rumble
class MotoAudioSynth {
  constructor() {
    this.ctx = null;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.ctx = new AudioContext();
      }
    }
  }

  playRev() {
    try {
      this.init();
      if (!this.ctx) return;
      if (this.ctx.state === 'suspended') {
        this.ctx.resume();
      }

      const now = this.ctx.currentTime;
      // Twin Crossplane CP2 270-degree low frequency rumble
      const osc1 = this.ctx.createOscillator();
      const osc2 = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      const filter = this.ctx.createBiquadFilter();

      osc1.type = 'sawtooth';
      osc2.type = 'triangle';

      // Pitch sweep mimicking a throttle blip
      osc1.frequency.setValueAtTime(65, now);
      osc1.frequency.exponentialRampToValueAtTime(140, now + 0.4);
      osc1.frequency.exponentialRampToValueAtTime(55, now + 1.2);

      osc2.frequency.setValueAtTime(63, now);
      osc2.frequency.exponentialRampToValueAtTime(138, now + 0.4);
      osc2.frequency.exponentialRampToValueAtTime(53, now + 1.2);

      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(250, now);
      filter.frequency.exponentialRampToValueAtTime(800, now + 0.4);
      filter.frequency.exponentialRampToValueAtTime(180, now + 1.2);

      gain.gain.setValueAtTime(0.01, now);
      gain.gain.linearRampToValueAtTime(0.25, now + 0.2);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 1.3);

      osc1.connect(filter);
      osc2.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);

      osc1.start(now);
      osc2.start(now);
      osc1.stop(now + 1.35);
      osc2.stop(now + 1.35);
    } catch (e) {
      console.log('Audio rev unavailable or muted:', e);
    }
  }
}

// Global instances
let smokeInstance = null;
const motoAudio = new MotoAudioSynth();

document.addEventListener('DOMContentLoaded', () => {
  const introScreen = document.getElementById('intro-screen');
  
  // Se o utilizador já viu a intro nesta sessão, se a URL tem ?nointro ou se veio de um link com hash, não mostra a intro
  const shouldSkipIntro = 
    window.location.search.includes('nointro') ||
    (window.location.hash && window.location.hash !== '#' && window.location.hash !== '#hero-section') ||
    sessionStorage.getItem('dark_intro_seen') === 'true';

  if (introScreen && shouldSkipIntro) {
    introScreen.style.display = 'none';
    document.body.style.overflow = 'auto';
    if (window.location.hash) {
      setTimeout(() => {
        const target = document.querySelector(window.location.hash);
        if (target) target.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  } else if (introScreen) {
    smokeInstance = new SmokeEngine('smoke-canvas');
  }

  const btnEnter = document.getElementById('btn-enter');
  const btnSkip = document.getElementById('btn-skip');
  const btnIntroBadge = document.getElementById('btn-intro-badge');

  function closeIntro(target = null) {
    if (!introScreen) return;
    try { sessionStorage.setItem('dark_intro_seen', 'true'); } catch (e) {}
    motoAudio.playRev();
    introScreen.classList.add('fade-out');
    setTimeout(() => {
      if (smokeInstance) smokeInstance.stop();
      introScreen.style.display = 'none';
      document.body.style.overflow = 'auto';
      
      let targetId = null;
      if (typeof target === 'string') {
        targetId = target;
      }

      if (targetId) {
        const el = document.getElementById(targetId);
        if (el) {
          el.scrollIntoView({ behavior: 'smooth' });
          try {
            history.pushState(null, null, '#' + targetId);
          } catch (err) {}
        }
      }
    }, 700);
  }

  // Clicar no logo DARK GHOSTRIDER STORE no cabeçalho vai SEMPRE direto para o início da página (Hero com vídeo), nunca para a intro
  const headerBrandLogo = document.getElementById('header-brand-logo');
  if (headerBrandLogo) {
    headerBrandLogo.addEventListener('click', (e) => {
      try { sessionStorage.setItem('dark_intro_seen', 'true'); } catch (err) {}
      if (introScreen) {
        introScreen.style.display = 'none';
        if (smokeInstance) smokeInstance.stop();
        document.body.style.overflow = 'auto';
      }
      const isHomePage = window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/');
      if (isHomePage) {
        e.preventDefault();
        const hero = document.getElementById('hero-section');
        if (hero) {
          hero.scrollIntoView({ behavior: 'smooth' });
        } else {
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        try { history.pushState(null, null, '#hero-section'); } catch (err) {}
      }
    });
  }

  // Direcionar diretamente para "Quem é o Dark?" ao clicar em DARK RIDER GARAGE
  if (btnIntroBadge) {
    btnIntroBadge.addEventListener('click', (e) => {
      e.preventDefault();
      closeIntro('quem-e-o-dark');
    });
  }

  // Fallback para qualquer elemento com classe .intro-badge
  const anyBadge = document.querySelector('.intro-badge');
  if (anyBadge && anyBadge !== btnIntroBadge) {
    anyBadge.addEventListener('click', (e) => {
      e.preventDefault();
      closeIntro('quem-e-o-dark');
    });
  }

  if (btnEnter) {
    btnEnter.addEventListener('click', (e) => {
      e.preventDefault();
      closeIntro(null);
    });
  }

  if (btnSkip) {
    btnSkip.addEventListener('click', (e) => {
      e.preventDefault();
      closeIntro(null);
    });
  }

  // Allow clicking anywhere or pressing Enter/Space to enter
  window.addEventListener('keydown', (e) => {
    if (introScreen && !introScreen.classList.contains('fade-out')) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'Escape') {
        closeIntro(null);
      }
    }
  });
});
