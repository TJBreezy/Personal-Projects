// DOM Elements
const categoriesList = document.getElementById('categoriesList');
const savedLinks = document.getElementById('savedLinks');
const addCategoryBtn = document.getElementById('addCategory');
const addCategoryModal = document.getElementById('addCategoryModal');
const categoryNameInput = document.getElementById('categoryName');
const confirmAddCategoryBtn = document.getElementById('confirmAddCategory');
const cancelAddCategoryBtn = document.getElementById('cancelAddCategory');
const saveLinkBtn = document.getElementById('saveLink');
const exportLinksBtn = document.getElementById('exportLinks');
const settingsBtn = document.getElementById('settingsButton');
const notification = document.getElementById('notification');

// State
let currentCategory = 'General';
let categories = [];
let links = {};

// Theme Management
function initializeTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', theme);
    updateThemeIcon(theme);
}

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const icon = settingsBtn.querySelector('i');
    icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
}

// Notification Management
function showNotification(message, duration = 3000) {
    notification.textContent = message;
    notification.style.display = 'block';
    setTimeout(() => {
        notification.style.display = 'none';
    }, duration);
}

// Category Management
function loadCategories() {
    chrome.storage.local.get(['categories', 'links'], (result) => {
        categories = result.categories || ['All', 'General'];
        links = result.links || {};
        renderCategories();
        renderLinks();
    });
}

function renderCategories() {
    categoriesList.innerHTML = '';
    categories.forEach(category => {
        const categoryElement = document.createElement('div');
        categoryElement.className = `category-item ${category === currentCategory ? 'active' : ''} ${category === 'All' ? 'all' : ''}`;
        
        const categoryName = document.createElement('span');
        categoryName.textContent = category;
        categoryElement.appendChild(categoryName);

        if (category !== 'General' && category !== 'All') {
            const deleteButton = document.createElement('button');
            deleteButton.className = 'delete-button';
            deleteButton.innerHTML = '<i class="fas fa-trash"></i>';
            deleteButton.onclick = (e) => {
                e.stopPropagation();
                deleteCategory(category);
            };
            categoryElement.appendChild(deleteButton);
        }

        categoryElement.onclick = () => selectCategory(category);
        categoriesList.appendChild(categoryElement);
    });
}

function selectCategory(category) {
    currentCategory = category;
    renderCategories();
    renderLinks();
}

function addCategory(name) {
    if (!name || categories.includes(name)) {
        showNotification('Category name must be unique and non-empty');
        return;
    }
    categories.push(name);
    chrome.storage.local.set({ categories }, () => {
        showNotification('Category added successfully');
        renderCategories();
    });
}

function deleteCategory(category) {
    const index = categories.indexOf(category);
    if (index > -1) {
        categories.splice(index, 1);
        // Move links from deleted category to General
        if (links[category]) {
            links['General'] = [...(links['General'] || []), ...links[category]];
            delete links[category];
        }
        chrome.storage.local.set({ categories, links }, () => {
            if (currentCategory === category) {
                currentCategory = 'General';
            }
            showNotification('Category deleted successfully');
            renderCategories();
            renderLinks();
        });
    }
}

// Link Management
function renderLinks() {
    savedLinks.innerHTML = '';
    let linksToShow = [];
    
    if (currentCategory === 'All') {
        // Gather all links from all categories
        Object.values(links).forEach(categoryLinks => {
            if (categoryLinks) {
                linksToShow = linksToShow.concat(categoryLinks.map(link => ({
                    ...link,
                    category: link.category || currentCategory
                })));
            }
        });
    } else {
        linksToShow = links[currentCategory] || [];
    }
    
    linksToShow.forEach(link => {
        const linkElement = document.createElement('div');
        linkElement.className = 'link-item';
        
        const linkContent = document.createElement('a');
        linkContent.href = link.url;
        linkContent.textContent = link.title;
        if (currentCategory === 'All') {
            linkContent.textContent += ` (${link.category})`;
        }
        linkContent.target = '_blank';
        linkElement.appendChild(linkContent);

        const deleteButton = document.createElement('button');
        deleteButton.className = 'delete-button';
        deleteButton.innerHTML = '<i class="fas fa-trash"></i>';
        deleteButton.onclick = (e) => {
            e.stopPropagation();
            deleteLink(link);
        };
        linkElement.appendChild(deleteButton);

        savedLinks.appendChild(linkElement);
    });
}

function saveCurrentLink() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const currentTab = tabs[0];
        const newLink = {
            url: currentTab.url,
            title: currentTab.title,
            category: currentCategory === 'All' ? 'General' : currentCategory,
            timestamp: Date.now()
        };

        if (!links[newLink.category]) {
            links[newLink.category] = [];
        }

        links[newLink.category].push(newLink);
        chrome.storage.local.set({ links }, () => {
            showNotification('Link saved successfully');
            renderLinks();
        });
    });
}

function deleteLink(linkToDelete) {
    if (currentCategory === 'All') {
        // Remove from specific category
        const categoryLinks = links[linkToDelete.category];
        if (categoryLinks) {
            links[linkToDelete.category] = categoryLinks.filter(
                link => link.url !== linkToDelete.url || link.timestamp !== linkToDelete.timestamp
            );
        }
    } else {
        links[currentCategory] = (links[currentCategory] || []).filter(
            link => link.url !== linkToDelete.url || link.timestamp !== linkToDelete.timestamp
        );
    }
    
    chrome.storage.local.set({ links }, () => {
        showNotification('Link deleted successfully');
        renderLinks();
    });
}

// Export Functionality
function exportLinks() {
    const exportData = {
        categories,
        links
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'revisit_links_export.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showNotification('Links exported successfully');
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    loadCategories();
});

addCategoryBtn.onclick = () => {
    addCategoryModal.style.display = 'block';
    categoryNameInput.focus();
};

confirmAddCategoryBtn.onclick = () => {
    addCategory(categoryNameInput.value.trim());
    categoryNameInput.value = '';
    addCategoryModal.style.display = 'none';
};

cancelAddCategoryBtn.onclick = () => {
    categoryNameInput.value = '';
    addCategoryModal.style.display = 'none';
};

saveLinkBtn.onclick = saveCurrentLink;
exportLinksBtn.onclick = exportLinks;
settingsBtn.onclick = toggleTheme;

// Close modal when clicking outside
window.onclick = (event) => {
    if (event.target === addCategoryModal) {
        addCategoryModal.style.display = 'none';
    }
};

// Handle Enter key in category input
categoryNameInput.addEventListener('keyup', (event) => {
    if (event.key === 'Enter') {
        confirmAddCategoryBtn.click();
    }
});
