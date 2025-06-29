# TCP Cleaners - Professional Cleaning Service Platform

A modern web application for managing a professional cleaning service, featuring user account management, booking system, loyalty program, and comprehensive analytics.

## Project Structure

```
tcp_cleaners/
│
├── app/                            # Application package
│   ├── __init__.py                # App initialization
│   ├── config.py                  # Configuration settings
│   │
│   ├── api/                       # API endpoints
│   │   ├── __init__.py
│   │   ├── bookings.py           # Booking management endpoints
│   │   ├── loyalty.py            # Loyalty program endpoints
│   │   ├── notifications.py       # Notification system endpoints
│   │   └── analytics.py          # Analytics data endpoints
│   │
│   ├── auth/                      # Authentication package
│   │   ├── __init__.py
│   │   ├── routes.py             # Auth routes
│   │   └── utils.py              # Auth utilities
│   │
│   ├── models/                    # Database models
│   │   ├── __init__.py
│   │   ├── user.py               # User model
│   │   ├── booking.py            # Booking model
│   │   ├── service.py            # Service model
│   │   ├── loyalty.py            # Loyalty model
│   │   └── notification.py       # Notification model
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── booking_service.py    # Booking business logic
│   │   ├── loyalty_service.py    # Loyalty program logic
│   │   └── notification_service.py# Notification handling
│   │
│   ├── static/                    # Static files
│   │   ├── css/                  # Stylesheets
│   │   │   ├── main.css
│   │   │   ├── admin/
│   │   │   └── customer/
│   │   ├── js/                   # JavaScript files
│   │   │   ├── main.js
│   │   │   ├── admin/
│   │   │   └── customer/
│   │   └── images/               # Image assets
│   │
│   ├── templates/                 # HTML templates
│   │   ├── base.html            # Base template
│   │   ├── admin/               # Admin templates
│   │   ├── customer/            # Customer templates
│   │   └── auth/                # Auth templates
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── decorators.py         # Custom decorators
│       ├── validators.py         # Input validators
│       └── helpers.py            # Helper functions
│
├── migrations/                     # Database migrations
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_api/                 # API tests
│   ├── test_auth/                # Auth tests
│   └── test_models/              # Model tests
│
├── .env                           # Environment variables
├── .gitignore                     # Git ignore file
├── config.py                      # Configuration file
├── requirements.txt               # Project dependencies
└── run.py                         # Application entry point
```

## Features

1. **User Account Management**
   - JWT authentication
   - Password strength validation
   - Input sanitization
   - Rate limiting
   - Activity logging

2. **Advanced Booking System**
   - Conflict detection
   - Cancellation policies
   - Admin booking overview
   - Booking history

3. **Loyalty Program**
   - Points tracking
   - Reward redemption
   - Referral system
   - Transaction history

4. **Notification System**
   - Multi-channel notifications (email, push, SMS)
   - Customizable preferences
   - Read/unread tracking
   - Admin broadcast capabilities

5. **Analytics Dashboard**
   - User statistics
   - Revenue analytics
   - Service performance metrics
   - Customer insights
   - Retention analysis

## Setup and Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/tcp-cleaners.git
cd tcp-cleaners
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database
```bash
flask db upgrade
python init_db.py
```

6. Run the application
```bash
flask run
```

## Development

- Follow PEP 8 style guide
- Write tests for new features
- Update documentation when making changes
- Use meaningful commit messages

## Testing

Run the test suite:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Image Credits and Sources

All images used in this website are from free-to-use sources with appropriate licenses:

1. Hero Image: Photo by RODNAE Productions from Pexels
   - Source: https://www.pexels.com/photo/woman-in-blue-long-sleeve-shirt-cleaning-glass-window-7414039/
   - License: Pexels License (Free to use)

2. Services Images:
   - Regular Cleaning: Photo by Karolina Grabowska from Pexels
     Source: https://www.pexels.com/photo/crop-person-cleaning-wooden-floor-with-mop-4239091/
   - Deep Cleaning: Photo by Andrea Piacquadio from Pexels
     Source: https://www.pexels.com/photo/person-holding-blue-and-white-plastic-bottle-3768916/
   - Move In/Out: Photo by Ketut Subiyanto from Pexels
     Source: https://www.pexels.com/photo/woman-in-white-shirt-cleaning-glass-window-4429561/

3. Additional Service Icons:
   - All icons sourced from Material Icons (Google)
   - License: Apache License 2.0

# North Carolina Cleaning Service Market Research (December 2024)

Average pricing research conducted across major NC cities including Charlotte, Raleigh, Durham, and Winston-Salem:

// Update PRICING object with NC market rates
const PRICING = {
    baseRates: {
        residential: 0.14,    // $0.12-0.15 per sq ft (NC average)
        commercial: 0.12,     // $0.11-0.13 per sq ft
        apartment: 0.15      // $0.13-0.16 per sq ft
    },
    serviceMultipliers: {
        regular: 1.0,
        deep: 1.65,         // 1.5x-1.8x (using 1.65x average)
        'move-in-out': 1.85 // 1.7x-2.0x (using 1.85x average)
    },
    frequencyDiscounts: {
        once: 1.0,
        weekly: 0.825,      // 15-20% discount (using 17.5%)
        biweekly: 0.875,    // 10-15% discount (using 12.5%)
        monthly: 0.925      // 5-10% discount (using 7.5%)
    },
    additionalServices: {
        windows: 5,         // $4-6 per window
        carpet: 0.28,       // $0.25-0.30 per sq ft
        oven: 35,          // $30-45
        refrigerator: 30,   // $25-35
        cabinets: 50,      // $40-60
        baseboards: 0.50    // $0.50 per linear foot
    },
    minimumCharges: {
        residential: 135,   // $120-150
        commercial: 175,    // $150-200
        apartment: 115      // $100-130
    }
};

Sources:
- Local cleaning service websites in NC
- Service provider interviews
- Consumer review platforms (Yelp, Google Reviews)
- Industry reports
