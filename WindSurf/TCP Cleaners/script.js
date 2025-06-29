document.addEventListener('DOMContentLoaded', () => {
    // Initialize pricing calculator
    initPricingCalculator();
    
    // Initialize service tabs
    initServiceTabs();

    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Animate sections on scroll
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });

    // Form submission handling
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            // Add form submission logic here
            alert('Thank you for your message! We will get back to you soon.');
            contactForm.reset();
        });
    }

    // Add hover effect to service cards
    const serviceCards = document.querySelectorAll('.service-card');
    serviceCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-10px)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });

    // File Upload Handling
    function initFileUpload() {
        const fileInput = document.getElementById('photos');
        const uploadPreview = document.getElementById('upload-preview');
        const uploadPlaceholder = document.querySelector('.upload-placeholder');

        if (!fileInput || !uploadPreview || !uploadPlaceholder) return;

        uploadPlaceholder.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadPlaceholder.style.borderColor = 'var(--color-accent)';
            uploadPlaceholder.style.background = 'var(--color-gray-light)';
        });

        uploadPlaceholder.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadPlaceholder.style.borderColor = 'var(--color-gray)';
            uploadPlaceholder.style.background = 'var(--color-white)';
        });

        uploadPlaceholder.addEventListener('drop', (e) => {
            e.preventDefault();
            fileInput.files = e.dataTransfer.files;
            handleFiles(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        function handleFiles(files) {
            uploadPreview.innerHTML = '';
            Array.from(files).forEach(file => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        const preview = createPreviewItem(e.target.result, file.name);
                        uploadPreview.appendChild(preview);
                    };
                    reader.readAsDataURL(file);
                } else if (file.type.startsWith('video/')) {
                    const preview = createVideoPreviewItem(file);
                    uploadPreview.appendChild(preview);
                }
            });
        }

        function createPreviewItem(src, name) {
            const div = document.createElement('div');
            div.className = 'preview-item';
            div.innerHTML = `
                <img src="${src}" alt="${name}">
                <button class="remove-btn" onclick="this.parentElement.remove()">×</button>
            `;
            return div;
        }

        function createVideoPreviewItem(file) {
            const div = document.createElement('div');
            div.className = 'preview-item';
            div.innerHTML = `
                <video width="100%" height="100%">
                    <source src="${URL.createObjectURL(file)}" type="${file.type}">
                </video>
                <button class="remove-btn" onclick="this.parentElement.remove()">×</button>
            `;
            return div;
        }
    }

    // Form Submission
    function initQuoteForm() {
        const form = document.getElementById('quoteForm');
        if (!form) return;
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const summaryService = document.getElementById('summary-service');
            const summaryFrequency = document.getElementById('summary-frequency');
            const summaryPrice = document.getElementById('summary-price');
            const serviceType = document.getElementById('service-type');
            const frequency = document.getElementById('frequency');
            const totalPrice = document.getElementById('total-price');

            if (summaryService && serviceType) {
                summaryService.textContent = serviceType.value;
            }
            if (summaryFrequency && frequency) {
                summaryFrequency.textContent = frequency.value;
            }
            if (summaryPrice && totalPrice) {
                summaryPrice.textContent = totalPrice.textContent;
            }

            alert('Thank you for your quote request! We will contact you shortly.');
        });
    }

    // Initialize all components
    initFileUpload();
    initQuoteForm();
    initRoomCalculator();
    initPricingCalculator();
    initSlideshow();
    initSeasonalSlider();
    updateFeaturedPromotion();
    initSeasonalBanner();

    // Mobile Menu Toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            document.body.style.overflow = navLinks.classList.contains('active') ? 'hidden' : '';
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!mobileMenuBtn.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.remove('active');
                document.body.style.overflow = '';
            }
        });

        // Close menu when clicking on a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                document.body.style.overflow = '';
            });
        });
    }

    // Handle smooth scrolling for anchor links
    function handleSmoothScroll() {
        // Check if there's a hash in the URL
        if (window.location.hash) {
            const targetSection = document.querySelector(window.location.hash);
            if (targetSection) {
                // Add a small delay to ensure the page is fully loaded
                setTimeout(() => {
                    targetSection.scrollIntoView({ behavior: 'smooth' });
                }, 100);
            }
        }
    }

    // Add event listener for page load
    window.addEventListener('load', handleSmoothScroll);

    // Handle clicks on navigation links
    document.addEventListener('click', (e) => {
        if (e.target.tagName === 'A' && e.target.getAttribute('href')?.includes('#')) {
            const targetPage = e.target.getAttribute('href').split('#')[0];
            const currentPage = window.location.pathname.split('/').pop();
            
            // If we're on the same page, handle smooth scroll
            if (!targetPage || targetPage === currentPage) {
                const targetId = e.target.getAttribute('href').split('#')[1];
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }
            }
        }
    });
});

// Room Size Calculator
function initRoomCalculator() {
    const toggleButtons = document.querySelectorAll('.toggle-button');
    const footageInput = document.querySelector('.footage-input');
    const roomsInput = document.querySelector('.rooms-input');
    
    if (!toggleButtons.length || !footageInput || !roomsInput) return;

    const roomSizes = {
        bedrooms: 132,
        bathrooms: 50,
        kitchen: 200,
        living: 280,
        other: 120
    };

    function updateEstimatedFootage() {
        let totalFootage = 0;
        Object.keys(roomSizes).forEach(room => {
            const input = document.getElementById(room);
            if (input) {
                const count = parseInt(input.value) || 0;
                totalFootage += count * roomSizes[room];
            }
        });
        
        const estimatedFootageDisplay = document.getElementById('estimated-footage');
        if (estimatedFootageDisplay) {
            estimatedFootageDisplay.textContent = `${totalFootage} sq ft`;
        }
        
        const squareFootageInput = document.getElementById('square-footage');
        if (squareFootageInput) {
            squareFootageInput.value = totalFootage;
            squareFootageInput.dispatchEvent(new Event('change'));
        }
    }

    // Initialize room count inputs
    Object.keys(roomSizes).forEach(room => {
        const input = document.getElementById(room);
        if (input) {
            input.addEventListener('change', () => {
                validateInput(input);
                updateEstimatedFootage();
            });
        }
    });

    // Toggle between calculation methods
    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const method = button.dataset.method;
            
            toggleButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            if (method === 'footage') {
                footageInput.style.display = 'block';
                roomsInput.style.display = 'none';
            } else {
                footageInput.style.display = 'none';
                roomsInput.style.display = 'block';
            }
            
            // Clear values when switching methods
            if (method === 'footage') {
                Object.keys(roomSizes).forEach(room => {
                    const input = document.getElementById(room);
                    if (input) input.value = '0';
                });
            } else {
                const squareFootageInput = document.getElementById('square-footage');
                if (squareFootageInput) squareFootageInput.value = '';
            }
            
            calculatePrice();
        });
    });

    // Initialize with footage method
    const footageButton = document.querySelector('.toggle-button[data-method="footage"]');
    if (footageButton) {
        footageButton.click();
    }
}

// Pricing Calculator
function initPricingCalculator() {
    const buildingTypeSelect = document.getElementById('building-type');
    const serviceTypeSelect = document.getElementById('service-type');
    const frequencySelect = document.getElementById('frequency');
    const squareFootageInput = document.getElementById('square-footage');
    const estimatedFootageSpan = document.getElementById('estimated-footage');
    const basePriceElement = document.getElementById('base-price');
    const additionalPriceElement = document.getElementById('additional-price');
    const discountElement = document.getElementById('discount');
    const totalPriceElement = document.getElementById('total-price');
    const requestQuoteBtn = document.getElementById('request-quote');

    // Room size constants (in sq ft)
    const ROOM_SIZES = {
        bedrooms: 132,
        bathrooms: 50,
        kitchen: 200,
        living: 280,
        other: 120
    };

    // Base rates per square foot
    const BASE_RATES = {
        apartment: 0.12,
        house: 0.14,
        office: 0.10,
        retail: 0.11,
        medical: 0.15
    };

    // Service type multipliers
    const SERVICE_MULTIPLIERS = {
        regular: 1.0,
        deep: 1.5,
        'move-in-out': 1.8
    };

    // Frequency discounts
    const FREQUENCY_DISCOUNTS = {
        once: 1.0,
        weekly: 0.85,
        biweekly: 0.90,
        monthly: 0.95
    };

    // Additional service rates
    const ADDITIONAL_RATES = {
        windows: 5,
        carpet: 0.28,
        oven: 35,
        refrigerator: 30,
        cabinets: 45,
        baseboards: 0.50
    };

    // Initialize size calculation method toggle
    const toggleButtons = document.querySelectorAll('.toggle-button');
    const footageInput = document.querySelector('.footage-input');
    const roomsInput = document.querySelector('.rooms-input');

    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            toggleButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            const method = button.dataset.method;
            footageInput.style.display = method === 'footage' ? 'block' : 'none';
            roomsInput.style.display = method === 'rooms' ? 'block' : 'none';
            
            calculateTotal();
        });
    });

    // Initialize room counters
    const roomCounters = document.querySelectorAll('.room-counters .counter-controls');
    roomCounters.forEach(counter => {
        const input = counter.querySelector('input');
        const minusBtn = counter.querySelector('.minus');
        const plusBtn = counter.querySelector('.plus');

        if (minusBtn) {
            minusBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value) || 0;
                if (currentValue > 0) {
                    input.value = currentValue - 1;
                    updateEstimatedFootage();
                    calculateTotal();
                }
            });
        }

        if (plusBtn) {
            plusBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value) || 0;
                input.value = currentValue + 1;
                updateEstimatedFootage();
                calculateTotal();
            });
        }

        if (input) {
            input.addEventListener('change', () => {
                updateEstimatedFootage();
                calculateTotal();
            });
        }
    });

    // Initialize additional service counters
    document.querySelectorAll('.service-option .quantity-input').forEach(container => {
        const input = container.querySelector('input');
        const minusBtn = container.querySelector('.minus');
        const plusBtn = container.querySelector('.plus');

        if (minusBtn) {
            minusBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value) || 0;
                if (currentValue > 0) {
                    input.value = currentValue - 1;
                    calculateTotal();
                }
            });
        }

        if (plusBtn) {
            plusBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value) || 0;
                input.value = currentValue + 1;
                calculateTotal();
            });
        }

        if (input) {
            input.addEventListener('change', calculateTotal);
            input.addEventListener('input', calculateTotal);
        }
    });

    function updateEstimatedFootage() {
        let totalFootage = 0;
        Object.keys(ROOM_SIZES).forEach(roomType => {
            const input = document.getElementById(roomType);
            if (input) {
                const count = parseInt(input.value) || 0;
                totalFootage += count * ROOM_SIZES[roomType];
            }
        });
        if (estimatedFootageSpan) {
            estimatedFootageSpan.textContent = `${totalFootage} sq ft`;
        }
        if (squareFootageInput) {
            squareFootageInput.value = totalFootage;
        }
    }

    function getSquareFootage() {
        const activeMethod = document.querySelector('.toggle-button.active')?.dataset.method;
        if (activeMethod === 'footage') {
            return parseFloat(squareFootageInput.value) || 0;
        } else {
            return parseFloat(estimatedFootageSpan?.textContent) || 0;
        }
    }

    function formatPrice(amount) {
        return `$${amount.toFixed(2)}`;
    }

    function calculateTotal() {
        const buildingType = buildingTypeSelect?.value;
        const serviceType = serviceTypeSelect?.value;
        const frequency = frequencySelect?.value;
        const squareFootage = getSquareFootage();

        if (!buildingType || !serviceType || !frequency || squareFootage === 0) {
            updatePriceDisplay(0, 0, 0, 0);
            return;
        }

        // Calculate base price
        const baseRate = BASE_RATES[buildingType];
        const serviceMultiplier = SERVICE_MULTIPLIERS[serviceType];
        const frequencyDiscount = FREQUENCY_DISCOUNTS[frequency];
        
        let basePrice = squareFootage * baseRate * serviceMultiplier;

        // Calculate additional services
        let additionalTotal = 0;
        document.querySelectorAll('.service-option .quantity-input').forEach(container => {
            const service = container.dataset.service;
            const input = container.querySelector('input');
            const quantity = parseInt(input?.value) || 0;
            
            if (quantity > 0 && ADDITIONAL_RATES[service]) {
                if (service === 'carpet') {
                    additionalTotal += squareFootage * ADDITIONAL_RATES[service];
                } else if (service === 'baseboards') {
                    const estimatedLinearFeet = Math.ceil(Math.sqrt(squareFootage) * 4);
                    additionalTotal += estimatedLinearFeet * ADDITIONAL_RATES[service];
                } else {
                    additionalTotal += quantity * ADDITIONAL_RATES[service];
                }
            }
        });

        const subtotal = basePrice + additionalTotal;
        const discountAmount = subtotal * (1 - frequencyDiscount);
        const total = subtotal * frequencyDiscount;

        updatePriceDisplay(basePrice, additionalTotal, discountAmount, total);

        // Update quote form if it exists
        const quoteForm = document.getElementById('quoteForm');
        if (quoteForm) {
            const totalInput = quoteForm.querySelector('input[name="estimated_total"]');
            if (totalInput) {
                totalInput.value = total.toFixed(2);
            }
        }
    }

    function updatePriceDisplay(basePrice, additionalTotal, discountAmount, total) {
        if (basePriceElement) {
            basePriceElement.textContent = formatPrice(basePrice);
        }
        if (additionalPriceElement) {
            additionalPriceElement.textContent = formatPrice(additionalTotal);
        }
        if (discountElement) {
            discountElement.textContent = `-${formatPrice(discountAmount)}`;
        }
        if (totalPriceElement) {
            totalPriceElement.textContent = formatPrice(total);
        }
    }

    // Add event listeners for all inputs
    [buildingTypeSelect, serviceTypeSelect, frequencySelect, squareFootageInput].forEach(input => {
        if (input) {
            input.addEventListener('change', calculateTotal);
            input.addEventListener('input', calculateTotal);
        }
    });

    // Set default calculation method
    const defaultToggle = document.querySelector('.toggle-button[data-method="footage"]');
    if (defaultToggle) {
        defaultToggle.click();
    }

    // Initialize calculator
    calculateTotal();

    // Initialize request quote button
    if (requestQuoteBtn) {
        requestQuoteBtn.addEventListener('click', function() {
            // Get all the calculator information
            const buildingType = buildingTypeSelect?.value || '';
            const serviceType = serviceTypeSelect?.value || '';
            const frequency = frequencySelect?.value || '';
            const squareFootage = squareFootageInput?.value || '0';
            
            // Get room counts if using room method
            const roomCounts = {};
            const roomTypes = ['bedrooms', 'bathrooms', 'kitchen', 'living', 'other'];
            roomTypes.forEach(type => {
                const input = document.getElementById(type);
                if (input && parseInt(input.value) > 0) {
                    roomCounts[type] = input.value;
                }
            });

            // Get additional services
            const additionalServices = [];
            document.querySelectorAll('.service-option .quantity-input').forEach(container => {
                const service = container.dataset.service;
                const input = container.querySelector('input');
                const quantity = parseInt(input?.value) || 0;
                if (quantity > 0) {
                    additionalServices.push(`${service}: ${quantity}`);
                }
            });

            // Create detailed summary
            let summary = `Service Request Details:\n`;
            summary += `Building Type: ${buildingType}\n`;
            summary += `Service Type: ${serviceType}\n`;
            summary += `Frequency: ${frequency}\n`;
            summary += `Square Footage: ${squareFootage} sq ft\n\n`;

            if (Object.keys(roomCounts).length > 0) {
                summary += 'Room Counts:\n';
                Object.entries(roomCounts).forEach(([room, count]) => {
                    summary += `- ${room.charAt(0).toUpperCase() + room.slice(1)}: ${count}\n`;
                });
                summary += '\n';
            }

            if (additionalServices.length > 0) {
                summary += 'Additional Services:\n';
                additionalServices.forEach(service => {
                    summary += `- ${service}\n`;
                });
                summary += '\n';
            }

            summary += 'Price Breakdown:\n';
            summary += `Base Price: ${basePriceElement?.textContent || '$0'}\n`;
            
            const additionalPrice = additionalPriceElement?.textContent || '$0.00';
            if (additionalPrice !== '$0.00') {
                summary += `Additional Services: ${additionalPrice}\n`;
            }
            
            const discount = discountElement?.textContent || '-$0.00';
            if (discount !== '-$0.00') {
                summary += `Discount: ${discount}\n`;
            }
            
            summary += `Total Estimate: ${totalPriceElement?.textContent || '$0'}`;

            // Scroll to contact section
            const contactSection = document.getElementById('contact');
            if (contactSection) {
                contactSection.scrollIntoView({ behavior: 'smooth' });
            }

            // Update the message field with the summary
            const messageField = document.getElementById('message');
            if (messageField) {
                messageField.value = summary;
            }
        });
    }
}

function updateFeaturedPromotion() {
    const featuredPromotion = document.getElementById('featuredPromotion');
    if (!featuredPromotion) return;

    const date = new Date();
    const month = date.getMonth();
    let promotionContent = '';

    // Determine current season and set appropriate content
    if (month >= 2 && month <= 4) {
        // Spring (March-May)
        promotionContent = `
            <div class="featured-icon"><i class="fas fa-sun fa-3x"></i></div>
            <h3>Spring Cleaning Special</h3>
            <p class="promotion-highlight">Spring into Clean! 20% Off Deep Cleaning Services</p>
            <p>Refresh your home this spring with our professional deep cleaning services.</p>
            <button class="cta-button">Book Your Spring Cleaning</button>
        `;
    } else if (month >= 5 && month <= 7) {
        // Summer (June-August)
        promotionContent = `
            <div class="featured-icon"><i class="fas fa-umbrella-beach fa-3x"></i></div>
            <h3>Summer Refresh</h3>
            <p class="promotion-highlight">Keep Your Home Cool and Clean!</p>
            <p>Get free window cleaning with every standard cleaning package this summer.</p>
            <button class="cta-button">Book Your Summer Refresh</button>
        `;
    } else if (month === 8) {
        // Back to School (September)
        promotionContent = `
            <div class="featured-icon"><i class="fas fa-graduation-cap fa-3x"></i></div>
            <h3>Back-to-School Special</h3>
            <p class="promotion-highlight">Get Ready for the School Year!</p>
            <p>15% off all cleaning services for families with school-aged children.</p>
            <button class="cta-button">Schedule Your Cleaning</button>
        `;
    } else if (month >= 9 && month <= 11) {
        // Holiday (October-December)
        promotionContent = `
            <div class="featured-icon"><i class="fas fa-gift fa-3x"></i></div>
            <h3>Holiday Cleaning Extravaganza</h3>
            <p class="promotion-highlight">Make Your Home Shine for the Holidays!</p>
            <p>25% off all cleaning services to prepare your home for holiday gatherings.</p>
            <button class="cta-button">Book Holiday Cleaning</button>
        `;
    } else {
        // New Year (January-February)
        promotionContent = `
            <div class="featured-icon"><i class="fas fa-star fa-3x"></i></div>
            <h3>New Year, New Home</h3>
            <p class="promotion-highlight">Start the New Year Fresh!</p>
            <p>20% off your first cleaning service of the year.</p>
            <button class="cta-button">Book Your Fresh Start</button>
        `;
    }

    featuredPromotion.innerHTML = promotionContent;
}

function initSeasonalSlider() {
    const slides = document.querySelectorAll('.seasonal-slide');
    const dots = document.querySelectorAll('.nav-dot');
    if (!slides.length || !dots.length) return;

    let currentSlide = 0;
    
    // Show current season's promotion by default
    const date = new Date();
    const month = date.getMonth();
    // Spring: 2-4, Summer: 5-7, Back to School: 8, Holiday: 9-11, New Year: 0-1
    if (month >= 2 && month <= 4) currentSlide = 0; // Spring
    else if (month >= 5 && month <= 7) currentSlide = 1; // Summer
    else if (month === 8) currentSlide = 2; // Back to School
    else if (month >= 9 && month <= 11) currentSlide = 3; // Holiday
    else currentSlide = 4; // New Year (months 0-1)

    function showSlide(index) {
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        slides[index].classList.add('active');
        dots[index].classList.add('active');
    }

    // Initialize with current season
    showSlide(currentSlide);

    // Add click events to dots
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            currentSlide = index;
            showSlide(currentSlide);
        });
    });

    // Auto-advance slides every 5 seconds
    setInterval(() => {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }, 5000);
}

function initSlideshow() {
    const slides = document.querySelectorAll('.hero-slideshow .slide');
    if (!slides || slides.length < 2) return;

    let currentSlide = 0;
    
    // Make sure first slide is active
    slides[0].classList.add('active');
    slides[1].classList.remove('active');
    
    function showSlide(index) {
        // Remove active class from all slides
        slides.forEach(slide => slide.classList.remove('active'));
        // Add active class to current slide
        slides[index].classList.add('active');
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }

    // Change slide every 2 seconds
    setInterval(nextSlide, 2000);
}

function initSeasonalBanner() {
    const bannerSlider = document.querySelector('.banner-slider');
    const slides = document.querySelectorAll('.banner-slide');
    const prevBtn = document.querySelector('.prev-banner');
    const nextBtn = document.querySelector('.next-banner');
    
    if (!bannerSlider || !slides.length) return;

    let currentSlide = 0;
    const totalSlides = slides.length;

    // Get current season
    function getCurrentSeason() {
        const date = new Date();
        const month = date.getMonth(); // 0-11 (January-December)
        
        // Winter (December-February): 11, 0, 1
        if (month === 11 || month === 0 || month === 1) return 3;
        // Spring (March-May): 2, 3, 4
        if (month >= 2 && month <= 4) return 0;
        // Summer (June-August): 5, 6, 7
        if (month >= 5 && month <= 7) return 1;
        // Fall (September-November): 8, 9, 10
        return 2;
    }

    // Initialize with current season
    currentSlide = getCurrentSeason();
    updateSlider();

    // Auto-advance slides every 5 seconds
    let autoSlideInterval = setInterval(nextSlide, 5000);

    function updateSlider() {
        const offset = currentSlide * -100;
        bannerSlider.style.transform = `translateX(${offset}%)`;
    }

    function nextSlide() {
        currentSlide = (currentSlide + 1) % totalSlides;
        updateSlider();
    }

    function prevSlide() {
        currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
        updateSlider();
    }

    // Add button event listeners
    if (prevBtn) {
        prevBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent event bubbling
            clearInterval(autoSlideInterval);
            prevSlide();
            autoSlideInterval = setInterval(nextSlide, 5000);
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent event bubbling
            clearInterval(autoSlideInterval);
            nextSlide();
            autoSlideInterval = setInterval(nextSlide, 5000);
        });
    }

    // Pause auto-advance on hover
    bannerSlider.addEventListener('mouseenter', () => {
        clearInterval(autoSlideInterval);
    });

    bannerSlider.addEventListener('mouseleave', () => {
        autoSlideInterval = setInterval(nextSlide, 5000);
    });

    // Handle touch events for mobile
    let touchStartX = 0;
    let touchEndX = 0;

    bannerSlider.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
        clearInterval(autoSlideInterval);
    }, false);

    bannerSlider.addEventListener('touchmove', (e) => {
        touchEndX = e.touches[0].clientX;
    }, false);

    bannerSlider.addEventListener('touchend', () => {
        const swipeDistance = touchEndX - touchStartX;
        if (Math.abs(swipeDistance) > 50) { // Minimum swipe distance
            if (swipeDistance > 0) {
                prevSlide();
            } else {
                nextSlide();
            }
        }
        autoSlideInterval = setInterval(nextSlide, 5000);
    }, false);
}

// Banner Functionality
function initializeBanners() {
    const banners = document.querySelectorAll('.promo-banner');
    
    banners.forEach(banner => {
        const slides = banner.querySelectorAll('.banner-slide');
        const prevBtn = banner.querySelector('.banner-nav.prev');
        const nextBtn = banner.querySelector('.banner-nav.next');
        let currentSlide = 0;
        
        // Set initial active slide
        slides[currentSlide].classList.add('active');
        
        // Auto slide functionality
        let slideInterval = setInterval(nextSlide, 5000);
        
        function nextSlide() {
            slides[currentSlide].classList.remove('active');
            currentSlide = (currentSlide + 1) % slides.length;
            slides[currentSlide].classList.add('active');
        }
        
        function prevSlide() {
            slides[currentSlide].classList.remove('active');
            currentSlide = (currentSlide - 1 + slides.length) % slides.length;
            slides[currentSlide].classList.add('active');
        }
        
        // Add click event listeners
        if (prevBtn && nextBtn) {
            prevBtn.addEventListener('click', () => {
                clearInterval(slideInterval);
                prevSlide();
                slideInterval = setInterval(nextSlide, 5000);
            });
            
            nextBtn.addEventListener('click', () => {
                clearInterval(slideInterval);
                nextSlide();
                slideInterval = setInterval(nextSlide, 5000);
            });
        }
        
        // Touch swipe functionality
        let touchStartX = 0;
        let touchEndX = 0;
        
        banner.addEventListener('touchstart', e => {
            touchStartX = e.changedTouches[0].screenX;
        }, false);
        
        banner.addEventListener('touchend', e => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, false);
        
        function handleSwipe() {
            const swipeThreshold = 50;
            const diff = touchStartX - touchEndX;
            
            if (Math.abs(diff) > swipeThreshold) {
                clearInterval(slideInterval);
                if (diff > 0) {
                    nextSlide();
                } else {
                    prevSlide();
                }
                slideInterval = setInterval(nextSlide, 5000);
            }
        }
    });
}

// Initialize banners when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeBanners();
});

// Initialize all components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initPromoBanner();
    initPricingCalculator();
    initServiceTabs();
    initFileUpload();
    initQuoteForm();
    initRoomCalculator();
    initSlideshow();
    initSeasonalSlider();
    updateFeaturedPromotion();
    initSeasonalBanner();
});
