# Revisit - Chrome Extension

A modern Chrome extension for saving and organizing your favorite links with custom categories.

## Features

- 🔖 Save links from your current tab
- 📁 Create and manage custom categories
- 🎨 Dark/Light theme support
- 📤 Export your links to JSON
- 🗑️ Easy deletion of links and categories
- 💾 Local storage for data persistence

## Installation

1. Clone this repository or download the ZIP file
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" in the top right
4. Click "Load unpacked" and select the extension directory

## Usage

1. Click the extension icon in your Chrome toolbar
2. Create categories using the + button
3. Save the current tab's link to a category
4. Toggle between dark and light themes
5. Export your links when needed

## Project Structure

```
├── manifest.json           # Extension configuration
├── popup.html             # Main extension popup
├── css/
│   └── styles.css        # Styling
├── js/
│   ├── popup.js         # Main functionality
│   └── background.js    # Background service worker
└── images/              # Extension icons
```

## Development

The extension is built using:
- HTML5
- CSS3
- Vanilla JavaScript
- Chrome Extension APIs
- FontAwesome for icons

## Contributing

Feel free to open issues or submit pull requests for any improvements or bug fixes.

## License

MIT License - feel free to use and modify as needed.
