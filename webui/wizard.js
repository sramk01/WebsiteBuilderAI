const TOTAL_STEPS = 18;
let currentStep = 1;
let sectionCatalog = []; // cached per site_type
let templateCatalog = [];
let testimonialRowsAdded = 0;
let generatedThemeContent = null;
let generatedThemeContentKey = '';
const previewImageUrls = {};
const templateSampleImages = {
  'cardio-slim-tea': {
    'image_hero': 'cardio-slim-tea-3-pouch.webp',
    'image_product-main': 'cardio-slim-tea-2-pouch.webp',
    'image_product-package-3': 'cardio-slim-tea-6-pouch.webp',
    'image_pricing': 'cardio-slim-tea-price.webp',
    'image_product-6-bottles': 'cardio-slim-tea-price.webp',
    'image_customer-review-1': 'cardio-slim-tea-customer-reviews-1.webp',
    'image_customer-review-2': 'cardio-slim-tea-customer-reviews-2.webp',
    'image_customer-review-3': 'cardio-slim-tea-customer-reviews-3.webp',
    'image_guarantee': 'cardio-slim-tea-money-back-gurantee.webp',
    'image_certified': 'certifications.webp',
    'image_free-shipping': 'cardio-slim-tea-free-shipping.webp',
    'image_checkout-page': 'cardio-slim-tea-checkout-page.webp',
  },
  'sodaslim-health': {
    'image_hero': 'sodaslim-banner.webp',
    'image_product-main': 'sodaslim-3.webp',
    'image_product-package-1': 'sodaslim-1.webp',
    'image_product-package-2': 'sodaslim-3.webp',
    'image_product-package-3': 'sodaslim-6.webp',
    'image_pricing': 'sodaslim-6.webp',
    'image_product-6-bottles': 'sodaslim-6.webp',
    'image_customer-review-1': 'sodaslim-rev1.webp',
    'image_customer-review-2': 'sodaslim-rev2.webp',
    'image_customer-review-3': 'sodaslim-rev3.webp',
    'image_guarantee': 'sodaslim-moneyback.webp',
    'image_certified': 'sodaslim-gmp.webp',
    'image_free-shipping': 'sodaslim-level.webp',
    'image_checkout-page': 'sodaslim-checkout.webp',
  },
  'mind-wake': {
    'image_hero': 'Hero.webp',
    'image_product-main': 'mindwake6.webp',
    'image_product-package-1': 'mindwake-1.webp',
    'image_product-package-2': 'mindwake-2.webp',
    'image_product-package-3': 'mindwake-3.webp',
    'image_pricing': 'mindwake-3.webp',
    'image_product-6-bottles': 'mindwake-3.webp',
    'image_customer-review-1': 'mindwake-reviwes1.webp',
    'image_customer-review-2': 'mindwake-reviwes2.webp',
    'image_customer-review-3': 'mindwake-reviwes3.webp',
    'image_guarantee': 'mindwake-guarantee.webp',
    'image_certified': 'mindwake-gmp.webp',
    'image_free-shipping': 'mindwake-natural.webp',
    'image_checkout-page': 'mindwake-orderpage.webp',
  },
};
const previewTextBindings = {
  previewNavBrand: { field: 'theme_header_brand', multiline: false },
  previewNavAbout: { field: 'theme_header_nav_1', multiline: false },
  previewNavBenefits: { field: 'theme_header_nav_2', multiline: false },
  previewNavPricing: { field: 'theme_header_nav_3', multiline: false },
  previewNavFaq: { field: 'theme_header_nav_4', multiline: false },
  previewNavCta: { field: 'theme_header_cta', multiline: false },
  previewHeroTitle: { field: 'theme_hero_title', multiline: false },
  previewHeroBody: { field: 'theme_hero_body', multiline: true },
  previewWhatTitle: { field: 'theme_what_title', multiline: false },
  previewWhatBody: { field: 'theme_what_body', multiline: true },
  previewHowTitle: { field: 'theme_how_title', multiline: false },
  previewHowBody: { field: 'theme_how_body', multiline: true },
  previewBenefitsTitle: { field: 'theme_benefits_title', multiline: false },
  previewBenefitsBody: { field: 'theme_benefits_body', multiline: true },
  previewIngredientsTitle: { field: 'theme_ingredients_title', multiline: false },
  previewIngredientsBody: { field: 'theme_ingredients_body', multiline: true },
  previewGuaranteeTitle: { field: 'theme_guarantee_title', multiline: false },
  previewGuaranteeBody: { field: 'theme_guarantee_body', multiline: true },
  previewUsageTitle: { field: 'theme_usage_title', multiline: false },
  previewUsageBody: { field: 'theme_usage_body', multiline: true },
  previewWhereTitle: { field: 'theme_where_title', multiline: false },
  previewWhereBody: { field: 'theme_where_body', multiline: true },
  previewNextTitle: { field: 'theme_post_purchase_title', multiline: false },
  previewNextBody: { field: 'theme_post_purchase_body', multiline: true },
  previewCheckoutBody: { field: 'theme_post_purchase_body', multiline: true },
  previewConclusionTitle: { field: 'theme_conclusion_title', multiline: false },
  previewConclusionBody: { field: 'theme_conclusion_body', multiline: true },
  previewFooterTitle: { field: 'theme_footer_title', multiline: false },
  previewFooterCopyright: { field: 'theme_footer_copyright', multiline: false },
};

const form = document.getElementById('wizardForm');
const nextBtn = document.getElementById('nextBtn');
const backBtn = document.getElementById('backBtn');
const generateBtn = document.getElementById('generateBtn');
const progressFill = document.getElementById('progressFill');
const stepCounter = document.getElementById('stepCounter');
const statusBox = document.getElementById('statusBox');
const sectionPickerList = document.getElementById('sectionPickerList');
const templateGrid = document.getElementById('templateGrid');
const themeEditor = document.getElementById('themeEditor');
const pagesList = document.getElementById('pagesList');
const ingredientsContentStep = document.getElementById('ingredientsContentStep');
const extraTestimonialRows = document.getElementById('extraTestimonialRows');
const addTestimonialBtn = document.getElementById('addTestimonialBtn');

const NAME_LABELS = {
  supplement: 'Product name', education: 'Course name',
  business: 'Business name', product: 'Product name',
  betting: 'Platform name',
};
const URL_LABELS = {
  supplement: 'Official website / checkout URL', education: 'Enrollment URL',
  business: 'Contact / booking URL', product: 'Signup URL',
  betting: 'Signup / registration URL',
};
const URL_HELP = {
  supplement: 'Where the "Buy Now" buttons should link.',
  education: 'Where the "Enroll Now" buttons should link.',
  business: 'Where the "Get a Quote" buttons should link.',
  product: 'Where the "Start Free Trial" buttons should link.',
  betting: 'Where the "Claim Your Bonus" buttons should link.',
};

// Legal/utility pages that always generate, plus ones conditional on site_type
const ALWAYS_PAGES = [
  'index.html', 'privacy-policy.html', 'disclaimer.html',
  'terms-and-conditions.html', 'shipping-policy.html', 'refund-policy.html',
  'contact.html', '404.html', 'sitemap.xml', 'robots.txt', '.htaccess', 'llms.txt',
];

function currentSiteType() {
  return form.querySelector('input[name="site_type"]:checked').value;
}

function updateDynamicLabels() {
  const type = currentSiteType();
  document.getElementById('nameLabel').textContent = NAME_LABELS[type];
  document.getElementById('urlLabel').textContent = URL_LABELS[type];
  document.getElementById('urlHelp').textContent = URL_HELP[type];
  sectionCatalog = []; // invalidate cache, refetch when the section-picker step is shown
  renderTemplatePicker();
}

function isStepSkipped(n) {
  return n === 13 && currentSiteType() !== 'supplement';
}

function showStep(n) {
  document.querySelectorAll('.step').forEach(el => {
    el.classList.toggle('active', Number(el.dataset.step) === n);
  });
  progressFill.style.width = `${(n / TOTAL_STEPS) * 100}%`;
  stepCounter.textContent = `Step ${n} of ${TOTAL_STEPS}`;
  backBtn.style.visibility = n === 1 ? 'hidden' : 'visible';
  nextBtn.classList.toggle('d-none', n === TOTAL_STEPS);
  generateBtn.classList.toggle('d-none', n !== TOTAL_STEPS);

  if (n === 10) loadTemplatePicker();
  if (n === 15) loadSectionPicker();
  if (n === 17) {
    renderThemeEditor();
    renderPagesList();
  }
  if (n === 18) buildReview();
  document.body.classList.toggle('theme-editor-active', n === 17);
}

function validateStep(n) {
  const stepEl = document.querySelector(`.step[data-step="${n}"]`);
  const requiredInputs = stepEl.querySelectorAll('[required]');
  for (const input of requiredInputs) {
    if (!input.value.trim()) {
      input.reportValidity();
      return false;
    }
  }
  return true;
}

nextBtn.addEventListener('click', () => {
  if (!validateStep(currentStep)) return;
  if (currentStep < TOTAL_STEPS) {
    currentStep++;
    while (isStepSkipped(currentStep) && currentStep < TOTAL_STEPS) currentStep++;
    showStep(currentStep);
  }
});

backBtn.addEventListener('click', () => {
  if (currentStep > 1) {
    currentStep--;
    while (isStepSkipped(currentStep) && currentStep > 1) currentStep--;
    showStep(currentStep);
  }
});

form.querySelectorAll('input[name="site_type"]').forEach(el => {
  el.addEventListener('change', updateDynamicLabels);
});

let ingredientRowsAdded = 0;
const extraIngredientRows = document.getElementById('extraIngredientRows');
const addIngredientBtn = document.getElementById('addIngredientBtn');

addIngredientBtn.addEventListener('click', () => {
  if (ingredientRowsAdded >= 6) return; // 4 base rows + 6 extra = 10 max
  ingredientRowsAdded++;
  const i = 4 + ingredientRowsAdded;
  const row = document.createElement('div');
  row.className = 'content-row row g-2 mb-2 align-items-center';
  row.innerHTML = `
    <div class="col-md-3"><input type="text" class="form-control" name="ingredient_name_${i}" placeholder="Ingredient name"></div>
    <div class="col-md-6"><input type="text" class="form-control" name="ingredient_desc_${i}" placeholder="Real, factual description"></div>
    <div class="col-md-3"><input type="file" class="form-control form-control-sm" name="image_ingredient-${i}" accept="image/*"><span class="text-muted small">Photo (optional)</span></div>
  `;
  extraIngredientRows.classList.remove('d-none');
  extraIngredientRows.appendChild(row);
  if (ingredientRowsAdded >= 6) addIngredientBtn.classList.add('d-none');
});

// ---------------------------------------------------------------------
// Step 13: Add extra testimonial rows (up to 6 total)
// ---------------------------------------------------------------------
addTestimonialBtn.addEventListener('click', () => {
  if (testimonialRowsAdded >= 3) return; // 3 base rows + 3 extra = 6 max
  testimonialRowsAdded++;
  const i = 3 + testimonialRowsAdded;
  const row = document.createElement('div');
  row.className = 'testimonial-row border rounded-3 p-3 mb-3';
  row.innerHTML = `
    <textarea class="form-control mb-2" name="testimonial_quote_${i}" rows="2" placeholder="Real customer quote"></textarea>
    <div class="row g-2">
      <div class="col-6"><input type="text" class="form-control" name="testimonial_name_${i}" placeholder="Real name (with permission)"></div>
      <div class="col-6"><input type="text" class="form-control" name="testimonial_role_${i}" placeholder="Role / location (optional)"></div>
    </div>
  `;
  extraTestimonialRows.classList.remove('d-none');
  extraTestimonialRows.appendChild(row);
  if (testimonialRowsAdded >= 3) addTestimonialBtn.classList.add('d-none');
});

// ---------------------------------------------------------------------
// Step 10: Curated color palettes
// ---------------------------------------------------------------------
const COLOR_PALETTES = [
  { name: 'Trustworthy Green', primary: '#1F6F54', secondary: '#F4A63E', dark: '#123328', light: '#FBF7EE' },
  { name: 'Modern Purple', primary: '#6D28D9', secondary: '#F59E0B', dark: '#241242', light: '#F5F3FF' },
  { name: 'Professional Blue', primary: '#2E5EAA', secondary: '#F4A63E', dark: '#132A4F', light: '#F0F4FB' },
  { name: 'Bold Orange', primary: '#C1440E', secondary: '#1F1F1F', dark: '#2B1B12', light: '#FBF3EE' },
  { name: 'Elegant Black & Gold', primary: '#B8912F', secondary: '#2C2C2C', dark: '#1A1A1A', light: '#FAF7EF' },
  { name: 'Calm Teal', primary: '#0E7C86', secondary: '#F4A63E', dark: '#0A3B40', light: '#EFFAFA' },
  { name: 'Energetic Red', primary: '#D62839', secondary: '#1F1F1F', dark: '#3A0D12', light: '#FDF0F1' },
  { name: 'Soft Rose', primary: '#B5546B', secondary: '#3F6C51', dark: '#3B1E27', light: '#FBF1F3' },
];

const paletteGrid = document.getElementById('paletteGrid');
const colorInputs = {
  primary: document.getElementById('colorPrimary'),
  secondary: document.getElementById('colorSecondary'),
  dark: document.getElementById('colorDark'),
  light: document.getElementById('colorLight'),
};

function applyPalette(p) {
  colorInputs.primary.value = p.primary;
  colorInputs.secondary.value = p.secondary;
  colorInputs.dark.value = p.dark;
  colorInputs.light.value = p.light;
  document.querySelectorAll('.palette-swatch').forEach(el => el.classList.remove('active'));
  const match = document.querySelector(`.palette-swatch[data-name="${p.name || ''}"]`);
  if (match) match.classList.add('active');
}

paletteGrid.innerHTML = COLOR_PALETTES.map(p => `
  <button type="button" class="palette-swatch" data-name="${p.name}" title="${p.name}">
    <span class="swatch-dots">
      <span style="background:${p.primary}"></span>
      <span style="background:${p.secondary}"></span>
      <span style="background:${p.dark}"></span>
    </span>
    <span class="swatch-label">${p.name}</span>
  </button>
`).join('');

paletteGrid.querySelectorAll('.palette-swatch').forEach((btn, i) => {
  btn.addEventListener('click', () => applyPalette(COLOR_PALETTES[i]));
});

// ---------------------------------------------------------------------
// Step 15: Suggest colors from a reference site's favicon
// ---------------------------------------------------------------------
const suggestColorsBtn = document.getElementById('suggestColorsBtn');
const suggestColorsNote = document.getElementById('suggestColorsNote');
const referenceSitesInput = document.getElementById('referenceSitesInput');

suggestColorsBtn.addEventListener('click', async () => {
  const firstUrl = (referenceSitesInput.value.split(/\n|,/)[0] || '').trim();
  if (!firstUrl) {
    suggestColorsNote.textContent = 'Add a URL above first.';
    return;
  }
  suggestColorsBtn.disabled = true;
  suggestColorsNote.textContent = 'Looking up that site\'s favicon...';
  try {
    const res = await fetch(`/api/suggest-colors?url=${encodeURIComponent(firstUrl)}`);
    const data = await res.json();
    if (data.palette) {
      applyPalette(data.palette);
      suggestColorsNote.innerHTML = `<i class="bi bi-check-circle-fill text-success"></i> Applied a palette derived from ${escapeHtml(firstUrl)}'s icon. Adjust further in Step 11 if you like.`;
    } else {
      suggestColorsNote.textContent = 'Could not detect a usable color from that site — try a different URL or pick a palette manually in Step 11.';
    }
  } catch (err) {
    suggestColorsNote.textContent = 'Something went wrong fetching that site — pick a palette manually in Step 11 instead.';
  } finally {
    suggestColorsBtn.disabled = false;
  }
});

// ---------------------------------------------------------------------
// Step 10: Template picker
// ---------------------------------------------------------------------
async function loadTemplatePicker() {
  if (templateCatalog.length === 0) {
    try {
      const res = await fetch('/api/templates');
      const data = await res.json();
      templateCatalog = data.templates || [];
    } catch (err) {
      templateGrid.innerHTML = `<p class="text-danger">Could not load templates: ${err.message}</p>`;
      return;
    }
  }
  renderTemplatePicker();
}

function renderTemplatePicker() {
  if (!templateGrid || templateCatalog.length === 0) return;

  const type = currentSiteType();
  const templates = templateCatalog.filter(t => (t.site_types || []).includes(type));
  const current = form.querySelector('input[name="template_id"]:checked')?.value || 'default';
  const selected = templates.some(t => t.id === current) ? current : 'default';

  templateGrid.innerHTML = templates.map(t => `
    <div class="template-card ${t.id === selected ? 'active' : ''}">
      <label>
        <input type="radio" name="template_id" value="${escapeHtml(t.id)}" ${t.id === selected ? 'checked' : ''}>
        <div>
          <h3>${escapeHtml(t.label)}</h3>
          <p>${escapeHtml(t.description)}</p>
        </div>
      </label>
      <div>
        ${t.id !== 'default' ? `<button type="button" class="template-preview-btn" data-template-preview="${escapeHtml(t.id)}"><i class="bi bi-eye"></i> Preview theme</button>` : ''}
      </div>
    </div>
  `).join('');

  templateGrid.querySelectorAll('.template-card input').forEach(input => {
    input.addEventListener('change', () => {
      templateGrid.querySelectorAll('.template-card').forEach(card => card.classList.remove('active'));
      input.closest('.template-card').classList.add('active');
    });
  });
  templateGrid.querySelectorAll('[data-template-preview]').forEach(btn => {
    btn.addEventListener('click', () => openTemplatePreview(btn.dataset.templatePreview));
  });
}

function sampleImageUrl(fieldName, templateId = currentTemplateId()) {
  const sample = templateSampleImages[templateId]?.[fieldName];
  return sample ? `/template-assets/${templateId}/images/${sample}` : '';
}

function openTemplatePreview(templateId) {
  const template = templateCatalog.find(t => t.id === templateId);
  const modal = document.getElementById('templatePreviewModal');
  const body = document.getElementById('templatePreviewBody');
  const title = document.getElementById('templatePreviewTitle');
  if (!modal || !body || !template) return;
  title.textContent = template.label;
  body.dataset.template = templateId;
  const product = fieldValue('product_name') || 'Mitolyn';
  body.innerHTML = `
    <nav class="tpl-nav"><strong>${escapeHtml(product)}</strong><span>About ${escapeHtml(product)}</span><span>Benefits</span><span>Pricing</span><button>ORDER NOW</button></nav>
    <section class="tpl-hero"><div class="tpl-image"><img src="${sampleImageUrl('image_hero', templateId)}" alt=""></div><div><h1>${escapeHtml(product)} - Premium Health Support</h1><p>Preview this theme style before selecting it. In the editor, this text is replaced by generated copy from your details.</p><button>VISIT OFFICIAL WEBSITE</button></div></section>
    <section class="tpl-two-col"><div><h2>What is ${escapeHtml(product)}</h2><p>This preview shows the layout, colors, spacing, and image positions for the custom template.</p></div><img src="${sampleImageUrl('image_product-main', templateId)}" alt=""></section>
    <section class="tpl-band"><h2>Don't Miss Out on Your Chance to Save on ${escapeHtml(product)}</h2></section>
    <section class="tpl-gray"><img src="${sampleImageUrl('image_pricing', templateId)}" alt=""></section>
    <section class="tpl-band"><h2>What Our Customers Are Saying?</h2></section>
    <section class="tpl-reviews"><div><img src="${sampleImageUrl('image_customer-review-1', templateId)}" alt=""><div><h3>Verified Customer</h3><p>Customer sections follow this row layout.</p><button>VERIFIED CUSTOMER</button></div></div></section>
    <section class="tpl-pink-card"><div><h2>Our ${escapeHtml(product)} Guarantee</h2><p>Trust and guarantee content appears in this card style.</p><button>BUY NOW</button></div><img src="${sampleImageUrl('image_guarantee', templateId)}" alt=""></section>
  `;
  modal.classList.remove('d-none');
}

document.getElementById('closeTemplatePreview')?.addEventListener('click', () => {
  document.getElementById('templatePreviewModal')?.classList.add('d-none');
});

document.getElementById('templatePreviewModal')?.addEventListener('click', (e) => {
  if (e.target.id === 'templatePreviewModal') e.currentTarget.classList.add('d-none');
});

function currentTemplateId() {
  return form.querySelector('input[name="template_id"]:checked')?.value || 'default';
}

function renderThemeEditor() {
  if (!themeEditor) return;
  themeEditor.classList.toggle('d-none', currentTemplateId() === 'default');
  document.getElementById('themeLivePreview')?.setAttribute('data-template', currentTemplateId());
  if (currentTemplateId() !== 'default') loadGeneratedPreviewContent();
  updateThemePreview();
}

function fieldValue(name) {
  return (form.querySelector(`[name="${name}"]`)?.value || '').trim();
}

function themeValue(name, fallback) {
  return fieldValue(name) || fallback;
}

function textToParagraphs(text) {
  const clean = (text || '').trim();
  if (!clean) return '';
  return clean.split(/\n\s*\n/).map(p => `<p>${escapeHtml(p)}</p>`).join('');
}

function htmlToPlainText(html) {
  const div = document.createElement('div');
  div.innerHTML = html || '';
  const paragraphs = Array.from(div.querySelectorAll('p')).map(p => p.textContent.trim()).filter(Boolean);
  if (paragraphs.length) return paragraphs.join('\n\n');
  return div.textContent.trim();
}

function generatedSection(sectionId) {
  return generatedThemeContent?.[sectionId] || {};
}

function seedThemeField(name, value) {
  const field = form.querySelector(`[name="${name}"]`);
  if (field && !field.value.trim() && value) field.value = value;
}

async function loadGeneratedPreviewContent() {
  const key = [
    currentTemplateId(),
    currentSiteType(),
    fieldValue('product_name'),
    fieldValue('category'),
    fieldValue('primary_keyword'),
    fieldValue('secondary_keywords'),
  ].join('|');
  if (generatedThemeContent && generatedThemeContentKey === key) return;

  try {
    const res = await fetch('/api/preview-content', {
      method: 'POST',
      body: new FormData(form),
    });
    if (!res.ok) throw new Error(await res.text());
    generatedThemeContent = await res.json();
    generatedThemeContentKey = key;
    const product = fieldValue('product_name') || 'Your Product';
    seedThemeField('theme_header_brand', product);
    seedThemeField('theme_header_nav_1', `About ${product}`);
    seedThemeField('theme_header_nav_2', 'Benefits');
    seedThemeField('theme_header_nav_3', 'Pricing');
    seedThemeField('theme_header_nav_4', 'FAQ');
    seedThemeField('theme_header_cta', 'Order Now');
    seedThemeField('theme_hero_title', generatedSection('hero').title);
    seedThemeField('theme_hero_body', htmlToPlainText(generatedSection('hero').body));
    seedThemeField('theme_what_title', generatedSection('what_is').title);
    seedThemeField('theme_what_body', htmlToPlainText(generatedSection('what_is').body));
    seedThemeField('theme_how_title', generatedSection('how_it_works').title);
    seedThemeField('theme_how_body', htmlToPlainText(generatedSection('how_it_works').body));
    seedThemeField('theme_benefits_title', generatedSection('benefits').title);
    seedThemeField('theme_benefits_body', htmlToPlainText(generatedSection('benefits').body));
    seedThemeField('theme_ingredients_title', generatedSection('ingredients').title);
    seedThemeField('theme_ingredients_body', htmlToPlainText(generatedSection('ingredients').body));
    seedThemeField('theme_guarantee_title', generatedSection('guarantee').title);
    seedThemeField('theme_guarantee_body', htmlToPlainText(generatedSection('guarantee').body));
    seedThemeField('theme_usage_title', generatedSection('usage').title);
    seedThemeField('theme_usage_body', htmlToPlainText(generatedSection('usage').body));
    seedThemeField('theme_where_title', generatedSection('where_to_buy').title);
    seedThemeField('theme_where_body', htmlToPlainText(generatedSection('where_to_buy').body));
    seedThemeField('theme_post_purchase_title', generatedSection('post_purchase').title);
    seedThemeField('theme_post_purchase_body', htmlToPlainText(generatedSection('post_purchase').body));
    seedThemeField('theme_conclusion_title', generatedSection('conclusion').title);
    seedThemeField('theme_conclusion_body', htmlToPlainText(generatedSection('conclusion').body));
    seedThemeField('theme_footer_title', 'Conclusion');
    seedThemeField('theme_footer_copyright', `© Copyright ${new Date().getFullYear()} | ${product} | All rights reserved.`);
    (generatedSection('faq').items || []).slice(0, 6).forEach((item, index) => {
      const i = index + 1;
      seedThemeField(`theme_faq_q_${i}`, item.q || item.question || item.title);
      seedThemeField(`theme_faq_a_${i}`, item.a || item.answer || item.text);
    });
    updateThemePreview();
  } catch (err) {
    console.warn('Could not load generated preview copy', err);
  }
}

function setPreviewText(id, value) {
  const el = document.getElementById(id);
  if (el && document.activeElement !== el) el.textContent = value || '';
}

function setPreviewHtml(id, value) {
  const el = document.getElementById(id);
  if (el && document.activeElement !== el) el.innerHTML = value || '';
}

function uploadedImageUrl(fieldName) {
  const inputs = Array.from(form.querySelectorAll(`[name="${fieldName}"]`));
  const input = inputs.reverse().find(el => el.files && el.files[0]);
  if (!input) return previewImageUrls[fieldName] || '';
  if (!input.dataset.previewUrl) {
    if (previewImageUrls[fieldName]) URL.revokeObjectURL(previewImageUrls[fieldName]);
    input.dataset.previewUrl = URL.createObjectURL(input.files[0]);
    previewImageUrls[fieldName] = input.dataset.previewUrl;
  }
  return previewImageUrls[fieldName];
}

function setPreviewImage(id, fieldName) {
  const img = document.getElementById(id);
  if (!img) return;
  const url = uploadedImageUrl(fieldName);
  img.dataset.imageField = fieldName;
  if (url) {
    img.src = url;
    img.closest('.tpl-image, .tpl-image-strip, .tpl-reviews')?.classList.add('has-image');
    img.style.display = '';
  } else {
    const templateId = currentTemplateId();
    const sample = templateSampleImages[templateId]?.[fieldName];
    if (sample) {
      img.src = `/template-assets/${templateId}/images/${sample}`;
    } else {
      img.removeAttribute('src');
    }
    img.style.display = '';
  }
}

function applyInlineEditing() {
  Object.entries(previewTextBindings).forEach(([id, binding]) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.dataset.editField = binding.field;
    el.dataset.multiline = binding.multiline ? 'true' : 'false';
    el.contentEditable = 'true';
    el.spellcheck = true;
    el.title = 'Click to edit';
  });
  document.querySelectorAll('#themeLivePreview img').forEach(img => {
    img.title = 'Click to replace image';
  });
}

function updateThemePreview() {
  if (!themeEditor || themeEditor.classList.contains('d-none')) return;
  const product = fieldValue('product_name') || 'Your Product';
  const category = fieldValue('category') || 'Wellness Support';
  const cta = 'Visit Official Website';
  const oneBottle = fieldValue('price_low') || '49';

  setPreviewText('previewNavBrand', themeValue('theme_header_brand', product));
  setPreviewText('previewNavAbout', themeValue('theme_header_nav_1', `About ${product}`));
  setPreviewText('previewNavBenefits', themeValue('theme_header_nav_2', 'Benefits'));
  setPreviewText('previewNavPricing', themeValue('theme_header_nav_3', 'Pricing'));
  setPreviewText('previewNavFaq', themeValue('theme_header_nav_4', 'FAQ'));
  setPreviewText('previewNavCta', themeValue('theme_header_cta', 'Order Now'));
  setPreviewText('previewHeroTitle', themeValue('theme_hero_title', `${product} - Premium ${category}`));
  setPreviewHtml('previewHeroBody', textToParagraphs(themeValue('theme_hero_body', `${product} is designed for people who want a clear, trustworthy way to support their daily goals.\n\nUse this editor to shape the exact message before generating your ZIP.`)));
  setPreviewText('previewCta', cta);

  setPreviewText('previewWhatTitle', themeValue('theme_what_title', `What is ${product}`));
  setPreviewHtml('previewWhatBody', textToParagraphs(themeValue('theme_what_body', `${product} is a premium ${category.toLowerCase()} option built around your product details, pricing, testimonials, and uploaded images.`)));

  setPreviewText('previewHowTitle', themeValue('theme_how_title', `How Does ${product} Work?`));
  setPreviewHtml('previewHowBody', textToParagraphs(themeValue('theme_how_body', `${product} is explained here with a clear step-by-step flow. Edit this copy to match the exact mechanism, usage, or service promise.`)));

  setPreviewText('previewPricingTitle', `Don't Miss Out on Your Chance to Save on ${product}`);
  setPreviewText('previewPricingSubtitle', `Claim Your Discounted ${product} Well While Stocks Last!`);
  setPreviewText('previewBenefitsTitle', themeValue('theme_benefits_title', `The Key Benefits of ${product}`));
  setPreviewHtml('previewBenefitsBody', textToParagraphs(themeValue('theme_benefits_body', `Add your most important benefits here, or leave this blank to use the generator's dynamic benefit copy.`)));
  setPreviewText('previewSecondPricingTitle', `Don't Miss Out Purchase and Save Discount on ${product}?`);

  setPreviewText('previewIngredientsTitle', themeValue('theme_ingredients_title', `The Key Ingredients of ${product}`));
  setPreviewHtml('previewIngredientsBody', textToParagraphs(themeValue('theme_ingredients_body', `Ingredient details entered in Step 13 will appear in the generated site. This preview shows the intro text you type here.`)));
  setPreviewText('previewProsTitle', `${product} - Pros & Cons`);

  setPreviewText('previewGuaranteeTitle', themeValue('theme_guarantee_title', 'Satisfaction Guarantee'));
  setPreviewHtml('previewGuaranteeBody', textToParagraphs(themeValue('theme_guarantee_body', `Use this section to explain refund terms, trust badges, or reassurance details.`)));

  setPreviewText('previewUsageTitle', themeValue('theme_usage_title', `How to Use ${product}`));
  setPreviewHtml('previewUsageBody', textToParagraphs(themeValue('theme_usage_body', `Explain how visitors should use or start with ${product}.`)));

  setPreviewText('previewWhereTitle', themeValue('theme_where_title', `Where to Buy ${product}`));
  setPreviewHtml('previewWhereBody', textToParagraphs(themeValue('theme_where_body', `Tell visitors where to buy safely and why they should use your official link.`)));

  setPreviewText('previewNextTitle', themeValue('theme_post_purchase_title', 'What Happens Next'));
  setPreviewHtml('previewNextBody', textToParagraphs(themeValue('theme_post_purchase_body', `Describe the checkout, confirmation, shipping, access, or onboarding flow.`)));
  setPreviewHtml('previewCheckoutBody', textToParagraphs(themeValue('theme_post_purchase_body', `Describe the checkout, confirmation, shipping, access, or onboarding flow.`)));

  setPreviewText('previewFinalOfferTitle', `Don't Wait Any Longer! Order Discounted ${product} Now!`);
  setPreviewText('previewFinalPrice', `$${oneBottle}/ Pouch`);
  setPreviewText('previewFooterTitle', themeValue('theme_footer_title', 'Conclusion'));
  setPreviewText('previewConclusionTitle', themeValue('theme_conclusion_title', 'Conclusion'));
  setPreviewHtml('previewConclusionBody', textToParagraphs(themeValue('theme_conclusion_body', `${product} gives visitors a polished, theme-based page that you can edit online before downloading.`)));
  setPreviewText('previewFooterCopyright', themeValue('theme_footer_copyright', `© Copyright ${new Date().getFullYear()} | ${product} | All rights reserved.`));

  const faqList = document.getElementById('previewFaqList');
  if (faqList) {
    const faqs = [];
    for (let i = 1; i <= 6; i++) {
      const q = fieldValue(`theme_faq_q_${i}`);
      const a = fieldValue(`theme_faq_a_${i}`);
      if (q || a) faqs.push({ q: q || `Question ${i}`, a });
    }
    const fallbackFaqs = faqs.length ? faqs : [
      { q: `What is ${product}?`, a: `${product} is presented using your selected theme and generated content.` },
      { q: 'Can I edit this theme?', a: 'Yes. Changes in this editor update the preview immediately.' },
    ];
    faqList.innerHTML = fallbackFaqs.map(item =>
      `<div class="tpl-faq-item"><strong>${escapeHtml(item.q)}</strong><span>${escapeHtml(item.a)}</span></div>`
    ).join('');
  }

  setPreviewImage('previewHeroImage', 'image_hero');
  if (!document.getElementById('previewHeroImage')?.getAttribute('src')) {
    setPreviewImage('previewHeroImage', 'image_product-main');
  }
  setPreviewImage('previewMainImage', 'image_product-main');
  setPreviewImage('previewPricingImage', 'image_pricing');
  if (!document.getElementById('previewPricingImage')?.getAttribute('src')) {
    setPreviewImage('previewPricingImage', 'image_product-6-bottles');
  }
  setPreviewImage('previewPricingImage2', 'image_pricing');
  if (!document.getElementById('previewPricingImage2')?.getAttribute('src')) {
    setPreviewImage('previewPricingImage2', 'image_product-6-bottles');
  }
  setPreviewImage('previewCustomer1', 'image_customer-review-1');
  setPreviewImage('previewCustomer2', 'image_customer-review-2');
  setPreviewImage('previewCustomer3', 'image_customer-review-3');
  setPreviewImage('previewGuaranteeImage', 'image_guarantee');
  setPreviewImage('previewCertifiedImage', 'image_certified');
  setPreviewImage('previewShippingImage', 'image_free-shipping');
  setPreviewImage('previewCheckoutImage', 'image_checkout-page');
  setPreviewImage('previewFinalProductImage', 'image_product-package-3');
  if (!document.getElementById('previewFinalProductImage')?.getAttribute('src')) {
    setPreviewImage('previewFinalProductImage', 'image_product-main');
  }
  applyInlineEditing();
}

form.addEventListener('input', (e) => {
  if (e.target.name && ['product_name', 'category', 'primary_keyword', 'secondary_keywords'].includes(e.target.name)) {
    generatedThemeContent = null;
    generatedThemeContentKey = '';
  }
  if (e.target.name && (e.target.name.startsWith('theme_') ||
      ['product_name', 'category', 'official_website'].includes(e.target.name))) {
    updateThemePreview();
  }
});

form.addEventListener('change', (e) => {
  if (e.target.name && (e.target.name.startsWith('image_') || e.target.name === 'template_id')) {
    if (e.target.name === 'template_id') {
      generatedThemeContent = null;
      generatedThemeContentKey = '';
    }
    if (e.target.name.startsWith('image_')) {
      if (e.target.dataset.previewUrl) URL.revokeObjectURL(e.target.dataset.previewUrl);
      if (previewImageUrls[e.target.name]) URL.revokeObjectURL(previewImageUrls[e.target.name]);
      delete e.target.dataset.previewUrl;
      delete previewImageUrls[e.target.name];
    }
    renderThemeEditor();
  }
});

document.getElementById('themeSectionNav')?.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-editor-section]');
  if (!btn) return;
  const section = btn.dataset.editorSection;
  document.querySelectorAll('#themeSectionNav button').forEach(b => b.classList.toggle('active', b === btn));
  document.querySelectorAll('[data-editor-panel]').forEach(panel => {
    panel.classList.toggle('active', panel.dataset.editorPanel === section);
  });
  const preview = document.getElementById('themeLivePreview');
  const targetMap = {
    header: '.tpl-nav',
    hero: '.tpl-hero',
    about: '#previewWhatTitle',
    benefits: '#previewBenefitsTitle',
    ingredients: '#previewIngredientsTitle',
    proof: '.tpl-reviews',
    images: '.tpl-image-strip',
    faq: '#previewFaqTitle',
    finish: '.tpl-footer',
  };
  const target = preview?.querySelector(targetMap[section]);
  if (target) preview.scrollTo({ top: target.offsetTop - 8, behavior: 'smooth' });
});

document.getElementById('previewDeviceToggle')?.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-preview-size]');
  if (!btn) return;
  const size = btn.dataset.previewSize;
  document.querySelectorAll('#previewDeviceToggle [data-preview-size]').forEach(b => b.classList.toggle('active', b === btn));
  const preview = document.getElementById('themeLivePreview');
  preview?.classList.remove('preview-desktop', 'preview-tablet', 'preview-mobile');
  preview?.classList.add(`preview-${size}`);
});

document.getElementById('themePreviewTop')?.addEventListener('click', () => {
  document.getElementById('themeLivePreview')?.scrollTo({ top: 0, behavior: 'smooth' });
});

document.getElementById('themeLivePreview')?.addEventListener('click', (e) => {
  const img = e.target.closest('img[data-image-field]');
  if (!img) return;
  const fieldName = img.dataset.imageField;
  const inputs = Array.from(form.querySelectorAll(`[name="${fieldName}"]`));
  const input = inputs.reverse().find(el => el.type === 'file');
  input?.click();
});

document.getElementById('themeLivePreview')?.addEventListener('keydown', (e) => {
  const el = e.target.closest('[data-edit-field]');
  if (!el) return;
  if (el.dataset.multiline !== 'true' && e.key === 'Enter') {
    e.preventDefault();
    el.blur();
  }
});

document.getElementById('themeLivePreview')?.addEventListener('input', (e) => {
  const el = e.target.closest('[data-edit-field]');
  if (!el) return;
  const field = form.querySelector(`[name="${el.dataset.editField}"]`);
  if (!field) return;
  field.value = el.innerText.trim();
});

// ---------------------------------------------------------------------
// Step 15: Section picker
// ---------------------------------------------------------------------
async function loadSectionPicker() {
  if (sectionCatalog.length === 0) {
    try {
      const res = await fetch(`/api/sections?site_type=${currentSiteType()}`);
      const data = await res.json();
      sectionCatalog = data.sections || [];
    } catch (err) {
      sectionPickerList.innerHTML = `<p class="text-danger">Could not load sections: ${err.message}</p>`;
      return;
    }
    renderSectionPicker(); // only rebuild the DOM when the catalog actually (re)loaded -
                            // NOT on every revisit, or the user's checkbox/order changes
                            // would get silently wiped every time they navigate back here.
  }
}

function renderSectionPicker() {
  sectionPickerList.innerHTML = sectionCatalog.map(s => `
    <div class="col-md-6 section-pick-col" data-id="${s.id}">
      <div class="section-pick ${s.default_checked ? 'checked' : ''}">
        <div class="reorder-controls">
          <button type="button" class="reorder-btn" data-dir="up" title="Move up"><i class="bi bi-chevron-up"></i></button>
          <button type="button" class="reorder-btn" data-dir="down" title="Move down"><i class="bi bi-chevron-down"></i></button>
        </div>
        <label class="section-pick-label">
          <input type="checkbox" name="selected_sections" value="${s.id}" ${s.default_checked ? 'checked' : ''}>
          <div>
            <div class="label">${escapeHtml(s.label)}</div>
            <div class="desc">${escapeHtml(s.description)}</div>
          </div>
        </label>
      </div>
    </div>
  `).join('');
  attachSectionPickerListeners();
}

function attachSectionPickerListeners() {
  sectionPickerList.querySelectorAll('.section-pick input').forEach(cb => {
    cb.addEventListener('change', () => {
      cb.closest('.section-pick').classList.toggle('checked', cb.checked);
    });
  });
  sectionPickerList.querySelectorAll('.reorder-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const col = btn.closest('.section-pick-col');
      const dir = btn.dataset.dir;
      const sibling = dir === 'up' ? col.previousElementSibling : col.nextElementSibling;
      if (!sibling) return;
      if (dir === 'up') col.parentNode.insertBefore(col, sibling);
      else col.parentNode.insertBefore(sibling, col);
      // Manually reordering implies the user wants to control order themselves
      randomizeOrderToggle.checked = false;
    });
  });
}

document.getElementById('selectAllSections').addEventListener('click', () => {
  sectionPickerList.querySelectorAll('.section-pick input').forEach(cb => {
    cb.checked = true;
    cb.closest('.section-pick').classList.add('checked');
  });
});

document.getElementById('selectDefaultSections').addEventListener('click', () => {
  // Full re-render restores both the default checked state AND the
  // original recommended order, regardless of any manual reordering.
  renderSectionPicker();
  randomizeOrderToggle.checked = true;
});

const randomizeOrderToggle = document.getElementById('randomizeSectionOrder');

// ---------------------------------------------------------------------
// Step 17: Pages preview
// ---------------------------------------------------------------------
function renderPagesList() {
  const type = currentSiteType();
  const pages = [...ALWAYS_PAGES];
  if (type === 'supplement') pages.push('medical-disclaimer.html');
  if (type === 'supplement' || type === 'product' || type === 'betting') pages.push('affiliate-disclosure.html');
  if (type === 'betting') pages.push('responsible-gambling.html');
  if (currentTemplateId() !== 'default') {
    pages.push('about.html', 'benefits.html', 'pricing.html', 'order.html');
  }
  pagesList.innerHTML = pages.sort().map(p =>
    `<li><i class="bi bi-check-circle-fill"></i> ${p}</li>`
  ).join('');
}

// ---------------------------------------------------------------------
// Step 18: Review
// ---------------------------------------------------------------------
function buildReview() {
  const fd = new FormData(form);
  const checkedSections = sectionPickerList.querySelectorAll('input:checked').length;
  const totalSections = sectionCatalog.length;
  const refCount = (fd.get('reference_sites') || '').split(/\n|,/).map(s => s.trim()).filter(Boolean).length;
  const template = templateCatalog.find(t => t.id === fd.get('template_id'));

  const rows = [
    ['Site type', currentSiteType()],
    ['Template', template ? template.label : 'Default Generator'],
    ['Name', fd.get('product_name') || '—'],
    ['Category', fd.get('category') || '—'],
    ['URL', fd.get('official_website') || '—'],
    ['Primary keyword', fd.get('primary_keyword') || '—'],
    ['Secondary keywords', fd.get('secondary_keywords') || '—'],
    ['Domain', fd.get('domain') || '—'],
    ['Business name', fd.get('business_name') || fd.get('product_name') || '—'],
    ['Contact email', fd.get('contact_email') || '—'],
    ['Pricing', `$${fd.get('price_low')} / $${fd.get('price_mid')} / $${fd.get('price_high')}`],
    ['Sections selected', `${checkedSections} of ${totalSections}`],
    ['Reference sites', refCount ? `${refCount} URL(s)` : 'None'],
  ];
  const box = document.getElementById('reviewSummary');
  box.innerHTML = '<dl class="row mb-0">' + rows.map(([k, v]) =>
    `<dt class="col-5 col-md-4">${k}</dt><dd class="col-7 col-md-8">${escapeHtml(v)}</dd>`
  ).join('') + '</dl>';
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

function setStatus(message, type) {
  statusBox.classList.remove('d-none', 'info', 'error', 'success');
  statusBox.classList.add(type);
  statusBox.innerHTML = message;
}

// ---------------------------------------------------------------------
// Submit
// ---------------------------------------------------------------------
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!validateStep(TOTAL_STEPS)) return;

  generateBtn.disabled = true;
  generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Generating...';
  setStatus('Building your site... this usually takes a few seconds.', 'info');

  try {
    const fd = new FormData(form);
    const res = await fetch('/api/generate', { method: 'POST', body: fd });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(err.error || `Server error (${res.status})`);
    }

    const blob = await res.blob();
    const disposition = res.headers.get('Content-Disposition') || '';
    const match = disposition.match(/filename="?([^"]+)"?/);
    const filename = match ? match[1] : 'website.zip';

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    setStatus(`<i class="bi bi-check-circle-fill"></i> Done! "${filename}" downloaded. Unzip it, open index.html with a local server, or upload it to any static host.`, 'success');
  } catch (err) {
    setStatus(`<i class="bi bi-exclamation-triangle-fill"></i> ${escapeHtml(err.message)}`, 'error');
  } finally {
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<i class="bi bi-download"></i> Generate &amp; Download ZIP';
  }
});

// ---------------------------------------------------------------------
// Step 17: AI content toggle + API key visibility + server key detection
// ---------------------------------------------------------------------
const useAiCheckbox = document.getElementById('useAi');
const apiKeyBlock = document.getElementById('apiKeyBlock');
const apiKeyInput = document.getElementById('apiKeyInput');
const anthropicApiKeyInput = document.getElementById('anthropicApiKeyInput');
const aiProviderSelect = document.getElementById('aiProviderSelect');
const apiKeyLabel = document.getElementById('apiKeyLabel');
const apiKeyHelpLink = document.getElementById('apiKeyHelpLink');
const toggleApiKeyBtn = document.getElementById('toggleApiKey');
const aiConfiguredNote = document.getElementById('aiConfiguredNote');
const useDifferentKeyLink = document.getElementById('useDifferentKeyLink');

let serverAiProviders = {};

function selectedAiProvider() {
  return aiProviderSelect?.value || 'openai';
}

function syncAiProviderUi() {
  const provider = selectedAiProvider();
  const isOpenAi = provider === 'openai';
  if (apiKeyInput) {
    apiKeyInput.name = isOpenAi ? 'openai_api_key' : 'anthropic_api_key';
    apiKeyInput.placeholder = isOpenAi ? 'sk-...' : 'sk-ant-...';
  }
  if (anthropicApiKeyInput) {
    anthropicApiKeyInput.disabled = !isOpenAi;
  }
  if (apiKeyLabel) apiKeyLabel.textContent = isOpenAi ? 'OpenAI API key' : 'Anthropic API key';
  if (apiKeyHelpLink) {
    apiKeyHelpLink.href = isOpenAi ? 'https://platform.openai.com/api-keys' : 'https://console.anthropic.com/settings/keys';
  }
}

function currentProviderConfigured() {
  return !!serverAiProviders[selectedAiProvider()]?.configured;
}

function refreshAiKeyVisibility() {
  syncAiProviderUi();
  if (!useAiCheckbox.checked) {
    apiKeyBlock.classList.add('d-none');
    aiConfiguredNote.classList.add('d-none');
    apiKeyInput.required = false;
    return;
  }
  if (currentProviderConfigured()) {
    aiConfiguredNote.classList.remove('d-none');
    apiKeyBlock.classList.remove('d-none');
    apiKeyInput.required = false;
  } else {
    aiConfiguredNote.classList.add('d-none');
    apiKeyBlock.classList.remove('d-none');
    apiKeyInput.required = true;
  }
}

async function checkAiStatus() {
  try {
    const res = await fetch('/api/ai-status');
    const data = await res.json();
    serverAiProviders = data.providers || {};
  } catch (err) {
    serverAiProviders = {};
  }
  refreshAiKeyVisibility();
}
checkAiStatus();

useAiCheckbox.addEventListener('change', refreshAiKeyVisibility);
aiProviderSelect?.addEventListener('change', refreshAiKeyVisibility);

useDifferentKeyLink.addEventListener('click', (e) => {
  e.preventDefault();
  aiConfiguredNote.classList.add('d-none');
  apiKeyBlock.classList.remove('d-none');
  syncAiProviderUi();
  apiKeyInput.required = false; // still optional -- blank falls back to the server key
});

toggleApiKeyBtn.addEventListener('click', () => {
  const isPassword = apiKeyInput.type === 'password';
  apiKeyInput.type = isPassword ? 'text' : 'password';
  toggleApiKeyBtn.innerHTML = isPassword ? '<i class="bi bi-eye-slash"></i>' : '<i class="bi bi-eye"></i>';
});

updateDynamicLabels();
showStep(currentStep);
