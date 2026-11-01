/**
 * RecyConnect – Modern Interactive Frontend Engine
 * 3D Ecosystem Scene, Calculators, Micro-Interactions & Analytics
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Initialize Lucide Icons if loaded
  if (typeof lucide !== 'undefined' && lucide.createIcons) {
    lucide.createIcons();
  }

  // 2. Initialize Bootstrap Tooltips
  if (typeof bootstrap !== 'undefined') {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
      new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }

  // 3. Navbar Scroll Elevation
  const navbar = document.querySelector('.navbar-recy');
  if (navbar) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 20) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  }

  // 4. Interactive 3D Recycling Ecosystem Experience
  init3DEcosystemScene();

  // 5. Interactive Scrap Price Estimator (on Homepage)
  initScrapEstimator();

  // 6. Complete Pickup Modal / Form Dynamic Calculation (Collector Weighing)
  initCollectorWeighingCalculator();

  // 7. Recycler Bulk Purchase Form Dynamic Calculation
  initRecyclerBulkCalculator();

  // 8. Animated Counters for Impact Numbers
  initImpactCounters();

  // 9. Auto dismiss alert messages
  setTimeout(function () {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
      if (typeof bootstrap !== 'undefined') {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      }
    });
  }, 6000);
});

/**
 * 3D Interactive Ecosystem Canvas
 * Renders an interactive 3D circular economy node with orbital satellites and glowing particle links.
 */
function init3DEcosystemScene() {
  const canvas = document.getElementById('recy3DCanvas');
  if (!canvas) return;

  const container = canvas.parentElement;
  let width = container.clientWidth || 500;
  let height = container.clientHeight || 480;

  // Set high DPI canvas resolution
  const dpr = window.devicePixelRatio || 1;
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);

  let mouseX = 0;
  let mouseY = 0;
  let targetRotX = 0;
  let targetRotY = 0;
  let currentRotX = 0;
  let currentRotY = 0;

  container.addEventListener('mousemove', function (e) {
    const rect = container.getBoundingClientRect();
    const x = e.clientX - rect.left - width / 2;
    const y = e.clientY - rect.top - height / 2;
    targetRotY = (x / (width / 2)) * 0.45;
    targetRotX = -(y / (height / 2)) * 0.45;
  });

  container.addEventListener('mouseleave', function () {
    targetRotX = 0;
    targetRotY = 0;
  });

  // Orbital Nodes representing materials
  const nodes = [
    { name: 'PET Plastic', color: '#16A477', radius: 140, angle: 0, speed: 0.012, yOffset: -20, size: 9 },
    { name: 'Metals & Alloys', color: '#B8F36B', radius: 175, angle: 1.2, speed: 0.009, yOffset: 25, size: 10 },
    { name: 'Paper & Pulp', color: '#38BDF8', radius: 120, angle: 2.6, speed: 0.015, yOffset: 15, size: 8 },
    { name: 'E-Waste', color: '#F59E0B', radius: 195, angle: 3.9, speed: 0.007, yOffset: -30, size: 9 },
    { name: 'Glass', color: '#A78BFA', radius: 155, angle: 5.1, speed: 0.011, yOffset: 0, size: 8 }
  ];

  // Background ambient floating particles
  const particles = [];
  for (let i = 0; i < 40; i++) {
    particles.push({
      x: (Math.random() - 0.5) * width,
      y: (Math.random() - 0.5) * height,
      z: (Math.random() - 0.5) * 300,
      size: Math.random() * 2.5 + 1,
      opacity: Math.random() * 0.5 + 0.2,
      speedY: Math.random() * 0.3 + 0.1
    });
  }

  let time = 0;

  function render() {
    time += 0.016;

    // Smooth rotation dampening
    currentRotX += (targetRotX - currentRotX) * 0.08;
    currentRotY += (targetRotY - currentRotY) * 0.08;

    ctx.clearRect(0, 0, width, height);

    const centerX = width / 2;
    const centerY = height / 2;

    // 1. Draw Ambient Particles
    particles.forEach(function (p) {
      p.y -= p.speedY;
      if (p.y < -height / 2) p.y = height / 2;

      const px = centerX + p.x;
      const py = centerY + p.y;
      ctx.beginPath();
      ctx.arc(px, py, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(22, 164, 119, ${p.opacity * 0.6})`;
      ctx.fill();
    });

    // 2. Draw Orbit Rings in 3D perspective
    const ringRadii = [120, 155, 185];
    ringRadii.forEach(function (r, index) {
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate(currentRotY * 0.4);
      ctx.scale(1, 0.42 + currentRotX * 0.25);

      ctx.beginPath();
      ctx.arc(0, 0, r, 0, Math.PI * 2);
      ctx.strokeStyle = index === 1 ? 'rgba(184, 243, 107, 0.28)' : 'rgba(22, 164, 119, 0.18)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([6, 8]);
      ctx.stroke();
      ctx.restore();
    });

    // 3. Central Core Glowing Circular Hub
    ctx.save();
    ctx.translate(centerX, centerY);

    // Core Outer Glow
    const gradient = ctx.createRadialGradient(0, 0, 10, 0, 0, 65);
    gradient.addColorStop(0, 'rgba(184, 243, 107, 0.45)');
    gradient.addColorStop(0.5, 'rgba(22, 164, 119, 0.25)');
    gradient.addColorStop(1, 'rgba(18, 61, 50, 0)');
    ctx.beginPath();
    ctx.arc(0, 0, 65, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();

    // Core Solid Emerald Sphere
    const coreGrad = ctx.createLinearGradient(-35, -35, 35, 35);
    coreGrad.addColorStop(0, '#16A477');
    coreGrad.addColorStop(0.7, '#123D32');
    coreGrad.addColorStop(1, '#0B261F');
    ctx.beginPath();
    ctx.arc(0, 0, 36, 0, Math.PI * 2);
    ctx.fillStyle = coreGrad;
    ctx.shadowColor = 'rgba(22, 164, 119, 0.4)';
    ctx.shadowBlur = 18;
    ctx.fill();
    ctx.shadowBlur = 0;

    // Core Inner Recycle Icon / Ring
    ctx.beginPath();
    ctx.arc(0, 0, 22, time * 0.8, time * 0.8 + Math.PI * 1.5);
    ctx.strokeStyle = '#B8F36B';
    ctx.lineWidth = 2.5;
    ctx.stroke();

    ctx.restore();

    // 4. Draw Orbiting Material Nodes and Connection Lines
    nodes.forEach(function (node) {
      node.angle += node.speed;

      // Calculate 3D projected coordinates
      const x = Math.cos(node.angle) * node.radius;
      const z = Math.sin(node.angle) * node.radius;
      const y = node.yOffset + Math.sin(node.angle * 2) * 12;

      // Apply tilt transformations
      const projX = centerX + x * Math.cos(currentRotY) - z * Math.sin(currentRotY);
      const projY = centerY + (y * Math.cos(currentRotX) + (z * 0.35 + x * currentRotX * 0.2));

      // Beam to Center
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(projX, projY);
      ctx.strokeStyle = `rgba(22, 164, 119, ${0.15 + (z / node.radius) * 0.1})`;
      ctx.lineWidth = 1;
      ctx.stroke();

      // Node Outer Halo
      ctx.beginPath();
      ctx.arc(projX, projY, node.size + 4, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
      ctx.fill();

      // Node Core
      ctx.beginPath();
      ctx.arc(projX, projY, node.size, 0, Math.PI * 2);
      ctx.fillStyle = node.color;
      ctx.shadowColor = node.color;
      ctx.shadowBlur = 10;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Small Label
      ctx.font = '600 10px Plus Jakarta Sans, sans-serif';
      ctx.fillStyle = '#17211D';
      ctx.textAlign = 'center';
      ctx.fillText(node.name, projX, projY + node.size + 13);
    });

    requestAnimationFrame(render);
  }

  render();

  // Resize listener
  window.addEventListener('resize', function () {
    width = container.clientWidth || 500;
    height = container.clientHeight || 480;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);
  });
}

/**
 * Scrap Value Estimator Logic
 */
function initScrapEstimator() {
  const calcCategory = document.getElementById('calcCategory');
  const calcWeight = document.getElementById('calcWeight');
  const calcWeightRange = document.getElementById('calcWeightRange');
  const calcEstimatedAmount = document.getElementById('calcEstimatedAmount');
  const calcRateBadge = document.getElementById('calcRateBadge');
  const weightDisplay = document.getElementById('weightDisplay');

  if (calcCategory && calcWeight && calcEstimatedAmount) {
    function updateEstimate() {
      const selectedOption = calcCategory.options[calcCategory.selectedIndex];
      const rate = parseFloat(selectedOption.getAttribute('data-rate')) || 0;
      const weight = parseFloat(calcWeight.value) || 0;
      const total = (rate * weight).toFixed(2);

      calcEstimatedAmount.textContent = '₹' + Number(total).toLocaleString('en-IN', { minimumFractionDigits: 2 });
      if (calcRateBadge) {
        calcRateBadge.textContent = '₹' + rate.toFixed(2) + '/kg';
      }
      if (weightDisplay) {
        weightDisplay.textContent = weight;
      }
    }

    calcCategory.addEventListener('change', updateEstimate);

    calcWeight.addEventListener('input', function () {
      if (calcWeightRange) calcWeightRange.value = this.value;
      updateEstimate();
    });

    if (calcWeightRange) {
      calcWeightRange.addEventListener('input', function () {
        calcWeight.value = this.value;
        updateEstimate();
      });
    }

    updateEstimate();
  }
}

/**
 * Collector Digital Scale Live Formula
 */
function initCollectorWeighingCalculator() {
  const completeWeightInput = document.getElementById('id_actual_weight');
  const completeRateInput = document.getElementById('id_agreed_rate');
  const liveTotalDisplay = document.getElementById('liveTotalDisplay');

  if (completeWeightInput && completeRateInput && liveTotalDisplay) {
    function calculateTotal() {
      const weight = parseFloat(completeWeightInput.value) || 0;
      const rate = parseFloat(completeRateInput.value) || 0;
      const total = (weight * rate).toFixed(2);
      liveTotalDisplay.textContent = '₹' + Number(total).toLocaleString('en-IN', { minimumFractionDigits: 2 });
    }

    completeWeightInput.addEventListener('input', calculateTotal);
    completeRateInput.addEventListener('input', calculateTotal);
    calculateTotal();
  }
}

/**
 * Recycler Bulk Purchase Dynamic Calculation
 */
function initRecyclerBulkCalculator() {
  const bulkQtyInput = document.getElementById('id_requested_quantity_kg');
  const bulkPriceInput = document.getElementById('id_offered_price_per_kg');
  const bulkTotalDisplay = document.getElementById('bulkTotalDisplay');

  if (bulkQtyInput && bulkPriceInput && bulkTotalDisplay) {
    function calculateBulkTotal() {
      const qty = parseFloat(bulkQtyInput.value) || 0;
      const price = parseFloat(bulkPriceInput.value) || 0;
      const total = (qty * price).toFixed(2);
      bulkTotalDisplay.textContent = '₹' + Number(total).toLocaleString('en-IN');
    }
    bulkQtyInput.addEventListener('input', calculateBulkTotal);
    bulkPriceInput.addEventListener('input', calculateBulkTotal);
    calculateBulkTotal();
  }
}

/**
 * Number Counter Animation for Impact Stats
 */
function initImpactCounters() {
  const counters = document.querySelectorAll('.animate-counter');
  if (!counters.length) return;

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseFloat(el.getAttribute('data-target')) || 0;
        let count = 0;
        const duration = 1600;
        const stepTime = 25;
        const steps = duration / stepTime;
        const increment = target / steps;

        const timer = setInterval(function () {
          count += increment;
          if (count >= target) {
            count = target;
            clearInterval(timer);
          }
          el.textContent = Math.round(count).toLocaleString('en-IN');
        }, stepTime);

        observer.unobserve(el);
      }
    });
  }, { threshold: 0.2 });

  counters.forEach(function (c) {
    observer.observe(c);
  });
}
