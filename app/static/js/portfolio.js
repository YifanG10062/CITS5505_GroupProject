/**
 * Portfolio creation and management functionality
 * Handles asset selection, allocation adjustments, and form validation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Constants
    const MAX_ASSETS = 3;
    
    // DOM elements
    const assetCards = document.querySelectorAll('.asset-card');
    const allocationContainer = document.getElementById('allocation-container');
    const noAssetsDiv = document.getElementById('no-assets');
    const totalAllocationDisplay = document.getElementById('allocation-total');
    const createButton = document.getElementById('create-portfolio-btn');
    const portfolioForm = document.getElementById('portfolio-form');
    
    // Portfolio name editing functionality
    const portfolioNameDisplay = document.querySelector('.portfolio-name-display');
    const portfolioNameEdit = document.querySelector('.portfolio-name-edit');
    const portfolioNameText = document.querySelector('.portfolio-name-text');
    const portfolioNameInput = document.getElementById('portfolio_name');
    
    if (portfolioNameDisplay && portfolioNameEdit && portfolioNameInput) {
        // Click on display view to show edit view
        portfolioNameDisplay.addEventListener('click', function() {
            portfolioNameDisplay.style.display = 'none';
            portfolioNameEdit.style.display = 'block';
            
            // Clear the input if it shows "click to edit"
            if (portfolioNameText.textContent.trim() === 'click to edit') {
                portfolioNameInput.value = '';
            }
            
            portfolioNameInput.focus();
            
            // Store original value in case we need to revert
            portfolioNameInput.dataset.originalValue = portfolioNameInput.value;
        });
        
        // Handle saving on enter or blur
        portfolioNameInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                savePortfolioName();
            } else if (e.key === 'Escape') {
                cancelPortfolioNameEdit();
            }
        });
        
        portfolioNameInput.addEventListener('blur', function() {
            savePortfolioName();
        });
        
        function savePortfolioName() {
            const newValue = portfolioNameInput.value.trim();
            
            if (newValue) {
                // If user entered a value, use it and update styling
                portfolioNameText.textContent = newValue;
                portfolioNameText.classList.remove('empty');
            } else {
                // When empty, show "click to edit" with proper styling
                portfolioNameText.textContent = 'click to edit';
                portfolioNameText.classList.add('empty');
            }
            
            portfolioNameEdit.style.display = 'none';
            portfolioNameDisplay.style.display = 'flex';
        }
        
        function cancelPortfolioNameEdit() {
            // Revert to original value or placeholder
            if (portfolioNameInput.dataset.originalValue) {
                portfolioNameInput.value = portfolioNameInput.dataset.originalValue;
                if (portfolioNameInput.dataset.originalValue) {
                    portfolioNameText.textContent = portfolioNameInput.dataset.originalValue;
                    portfolioNameText.classList.remove('empty');
                } else {
                    portfolioNameText.textContent = 'click to edit';
                    portfolioNameText.classList.add('empty');
                }
            } else {
                portfolioNameInput.value = '';
                portfolioNameText.textContent = 'click to edit';
                portfolioNameText.classList.add('empty');
            }
            
            portfolioNameEdit.style.display = 'none';
            portfolioNameDisplay.style.display = 'flex';
        }
    }
    
    // Exit early if required elements are not found (not on portfolio page)
    if (!allocationContainer || !noAssetsDiv || !totalAllocationDisplay) {
        console.log('Portfolio page elements not found, skipping portfolio.js initialization');
        return;
    }
    
    // State variables
    let selectedAssets = [];
    let allocations = {};
    
    /**
     * Update the disabled state of asset cards based on selection count
     */
    function updateCardStates() {
        // If maximum number of assets are selected, disable unselected cards
        const shouldDisableUnselected = selectedAssets.length >= MAX_ASSETS;
        
        assetCards.forEach(card => {
            const isSelected = card.classList.contains('selected');
            
            if (!isSelected && shouldDisableUnselected) {
                card.classList.add('disabled');
            } else {
                card.classList.remove('disabled');
            }
        });
    }
    
    /**
     * Handle asset card click event
     */
    assetCards.forEach(card => {
        card.addEventListener('click', function() {
            // Ignore clicks on disabled cards
            if (this.classList.contains('disabled')) {
                return;
            }
            
            const assetCode = this.dataset.assetCode;
            const assetName = this.querySelector('.asset-name').innerText;
            const assetCompany = this.querySelector('.asset-company').innerText;
            const assetLogoSrc = this.querySelector('.asset-icon img').src;
            
            if (this.classList.contains('selected')) {
                // Deselect asset
                this.classList.remove('selected');
                removeAssetAllocation(assetCode);
                selectedAssets = selectedAssets.filter(asset => asset.code !== assetCode);
                
                // Check if all assets are removed and show no-assets div if needed
                if (selectedAssets.length === 0) {
                    updateAllocationItems(); // Make sure no-assets div is added back
                }
            } else {
                // Select asset if under limit
                if (selectedAssets.length < MAX_ASSETS) {
                    this.classList.add('selected');
                    selectedAssets.push({
                        code: assetCode,
                        name: assetName,
                        company: assetCompany,
                        logoSrc: assetLogoSrc
                    });
                    addAssetAllocation(assetCode, assetName, assetLogoSrc);
                }
            }
            
            // Update UI based on selection
            updateAllocationUI();
            updateCardStates();
        });
    });
    
    /**
     * Add asset allocation to the UI and update the allocation object
     */
    function addAssetAllocation(assetCode, assetName, logoSrc) {
        // Update allocations based on number of selected assets
        if (selectedAssets.length === 1) {
            allocations[assetCode] = 100;
        } else if (selectedAssets.length === 2) {
            // Reset to 50/50
            const keys = Object.keys(allocations);
            keys.forEach(key => allocations[key] = 50);
            allocations[assetCode] = 50;
        } else if (selectedAssets.length === 3) {
            // Reset to 33/33/34 with the last asset getting 34%
            const keys = Object.keys(allocations);
            
            // First reset all to 33%
            keys.forEach(key => allocations[key] = 33);
            
            // Then give the last added asset 34% to ensure total of 100%
            allocations[assetCode] = 34;
        }
        
        // Create allocation items in UI
        updateAllocationItems();
    }
    
    /**
     * Remove asset allocation and redistribute percentages
     */
    function removeAssetAllocation(assetCode) {
        delete allocations[assetCode];
        
        // Redistribute allocations
        const remainingAssets = Object.keys(allocations);
        if (remainingAssets.length === 1) {
            allocations[remainingAssets[0]] = 100;
        } else if (remainingAssets.length === 2) {
            allocations[remainingAssets[0]] = 50;
            allocations[remainingAssets[1]] = 50;
        }
        
        // Force complete recreation of allocation items
        updateAllocationItems();
        
        // Make sure to update the UI after removing assets
        updateAllocationUI();
    }
    
    /**
     * Update all allocation UI elements
     */
    function updateAllocationUI() {
        if (selectedAssets.length === 0) {
            // Make sure no-assets div is visible when no assets are selected
            if (noAssetsDiv) {
                noAssetsDiv.style.display = 'block';
                
                // Make sure it's actually in the DOM
                if (!allocationContainer.contains(noAssetsDiv)) {
                    allocationContainer.innerHTML = ''; // Clear any existing content
                    allocationContainer.appendChild(noAssetsDiv);
                }
            }
            
            createButton.disabled = true;
            totalAllocationDisplay.textContent = '0%';
            
            // Handle class replacement safely
            if (totalAllocationDisplay.classList.contains('valid')) {
                totalAllocationDisplay.classList.remove('valid');
                totalAllocationDisplay.classList.add('invalid');
            }
        } else {
            if (noAssetsDiv) {
                noAssetsDiv.style.display = 'none';
            }
            
            const total = calculateTotalAllocation();
            totalAllocationDisplay.textContent = `${total}%`;
            
            if (total === 100) {
                // Handle class replacement safely
                if (totalAllocationDisplay.classList.contains('invalid')) {
                    totalAllocationDisplay.classList.remove('invalid');
                    totalAllocationDisplay.classList.add('valid');
                }
                createButton.disabled = false;
            } else {
                // Handle class replacement safely
                if (totalAllocationDisplay.classList.contains('valid')) {
                    totalAllocationDisplay.classList.remove('valid');
                    totalAllocationDisplay.classList.add('invalid');
                }
                createButton.disabled = true;
            }
        }
    }
    
    /**
     * Calculate total allocation percentage
     */
    function calculateTotalAllocation() {
        return Object.values(allocations).reduce((sum, value) => sum + value, 0);
    }
    
    /**
     * Update allocation items in the UI
     */
    function updateAllocationItems() {
        try {
            // Clear ALL existing items including the no-assets div
            while (allocationContainer.firstChild) {
                allocationContainer.removeChild(allocationContainer.firstChild);
            }
            
            // Re-add the no-assets div if needed
            if (selectedAssets.length === 0) {
                allocationContainer.appendChild(noAssetsDiv);
                noAssetsDiv.style.display = 'block'; // Ensure it's visible
            } else {
                // Create items for each selected asset
                selectedAssets.forEach(asset => {
                    const allocation = allocations[asset.code];
                    
                    // Skip assets that don't have an allocation or have 0 allocation
                    if (!allocation || allocation <= 0) {
                        return;
                    }
                    
                    const allocationItem = document.createElement('div');
                    allocationItem.className = 'allocation-item';
                    allocationItem.dataset.assetCode = asset.code;
                    
                    // Create allocation item with edit icon on the left side of percentage
                    allocationItem.innerHTML = `
                        <div class="allocation-asset">
                            <div class="asset-code">${asset.code}</div>
                        </div>
                        <div class="allocation-value" data-asset-code="${asset.code}">
                            <img src="/static/icons/edit.svg" alt="Edit" class="edit-icon">
                            <span>${allocation}%</span>
                            <input type="hidden" name="allocation[${asset.code}]" value="${allocation}" required>
                        </div>
                    `;
                    
                    allocationContainer.appendChild(allocationItem);
                    
                    // Add event listener to allocation value
                    const allocationValueEl = allocationItem.querySelector('.allocation-value');
                    allocationValueEl.addEventListener('click', function() {
                        enableDirectEdit(this, asset.code, allocation);
                    });
                });
            }
            
            updateAllocationUI();
        } catch (error) {
            console.error('Error updating allocation items:', error);
        }
    }
    
    /**
     * Helper function to get static URL
     */
    function getStaticUrl(path) {
        // Remove leading slash if present
        if (path.startsWith('/')) {
            path = path.substring(1);
        }
        // If we're in a Flask app, we should have a BASE_URL variable
        // Otherwise, just return the path as is
        return path;
    }
    
    /**
     * Enable direct editing of allocation value
     */
    function enableDirectEdit(element, assetCode, currentValue) {
        // Replace the display with an input field
        const originalHTML = element.innerHTML;
        
        element.innerHTML = `
            <div class="allocation-value-edit">
                <input type="number" min="0" max="100" value="${currentValue}" class="allocation-edit-input form-control">
                <span class="percentage">%</span>
            </div>
        `;
        
        const input = element.querySelector('input');
        input.focus();
        input.select();
        
        // Add primary color style to indicate edit mode
        element.classList.add('editing');
        
        // Handle input changes
        function handleInputChange() {
            let newValue = parseInt(input.value);
            
            // Validate input
            if (isNaN(newValue) || newValue < 0) {
                newValue = 0;
            } else if (newValue > 100) {
                newValue = 100;
            }
            
            // Update allocation
            allocations[assetCode] = newValue;
            
            // Restore the original display with new value
            updateAllocationItems();
        }
        
        // Add event listeners
        input.addEventListener('blur', handleInputChange);
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                handleInputChange();
            } else if (e.key === 'Escape') {
                // Restore original without changes
                element.innerHTML = originalHTML;
            }
        });
    }
    
    /**
     * Form validation
     */
    if (portfolioForm) {
        portfolioForm.addEventListener('submit', function(e) {
            const total = calculateTotalAllocation();
            if (total !== 100) {
                e.preventDefault();
                alert('Total allocation must equal 100%');
                return false;
            }
            
            const portfolioName = document.getElementById('portfolio_name').value.trim();
            if (!portfolioName) {
                e.preventDefault();
                alert('Please provide a portfolio name');
                return false;
            }
            
            if (selectedAssets.length === 0) {
                e.preventDefault();
                alert('Please select at least one asset');
                return false;
            }
        });
    }
    
    // Initialize UI on page load
    updateCardStates();

    // Portfolio list view/card view toggle functionality
    const listViewBtn = document.getElementById('listViewBtn');
    const cardViewBtn = document.getElementById('cardViewBtn');
    const listView = document.getElementById('listView');
    const cardView = document.getElementById('cardView');
    const includeSharedToggle = document.getElementById('includeSharedToggle');
    
    // Add event listeners for view switching
    if (listViewBtn && cardViewBtn) {
        listViewBtn.addEventListener('click', function() {
            // Switch to list view
            listViewBtn.classList.add('active');
            cardViewBtn.classList.remove('active');
            listView.classList.remove('d-none');
            cardView.classList.add('d-none');
        });
        
        cardViewBtn.addEventListener('click', function() {
            // Switch to card view
            cardViewBtn.classList.add('active');
            listViewBtn.classList.remove('active');
            cardView.classList.remove('d-none');
            listView.classList.add('d-none');
        });
    }
    
    // Toggle for including shared portfolios
    if (includeSharedToggle) {
        includeSharedToggle.addEventListener('change', function() {
            // In a real implementation, this would reload the portfolios
            // based on the toggle state
            console.log('Include shared portfolios:', this.checked);
            // For now, we'll just log the change
        });
    }
    
    // Setup sort functionality for table columns
    const sortableHeaders = document.querySelectorAll('.portfolios-table th .sort-icon');
    sortableHeaders.forEach(header => {
        header.parentElement.addEventListener('click', function() {
            // In a real implementation, this would sort the table
            // based on the clicked column
            console.log('Sort by:', this.textContent.trim());
            // For now, we'll just log the click
        });
    });

    // Initialize share portfolio modal with simplified implementation
    initSharePortfolioModal();

    /**
     * Initialize the share portfolio modal
     * Uses a simplified approach to avoid potential conflicts
     */
    function initSharePortfolioModal() {
        console.log('Initializing share portfolio modal');
        
        // Find all share links
        const shareLinks = document.querySelectorAll('a.action-link');
        shareLinks.forEach(link => {
            if(link.textContent.trim() === 'Share') {
                // Add click event handler
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('Share link clicked');
                    
                    // Get the modal element
                    const modalEl = document.getElementById('sharePortfolioModal');
                    if (!modalEl) {
                        console.error('Modal element not found');
                        return;
                    }
                    
                    // Store portfolio ID
                    const portfolioId = this.dataset.portfolioId;
                    console.log('Portfolio ID:', portfolioId);
                    
                    // Try to show modal using Bootstrap API
                    if (typeof bootstrap !== 'undefined') {
                        try {
                            const modal = new bootstrap.Modal(modalEl);
                            modal.show();
                            console.log('Modal shown using Bootstrap API');
                            
                            // Set up share button handler
                            setupShareButton(portfolioId);
                        } catch (err) {
                            console.error('Error showing modal with Bootstrap:', err);
                            fallbackModalDisplay(modalEl, portfolioId);
                        }
                    } else {
                        console.warn('Bootstrap not available, using fallback');
                        fallbackModalDisplay(modalEl, portfolioId);
                    }
                });
            }
        });
    }
    
    /**
     * Set up share button click handler
     * @param {string} portfolioId - The ID of the portfolio to share
     */
    function setupShareButton(portfolioId) {
        const shareBtn = document.getElementById('sharePortfolioBtn');
        if (!shareBtn) return;
        
        // Create new button to avoid duplicate listeners
        const newShareBtn = shareBtn.cloneNode(true);
        shareBtn.parentNode.replaceChild(newShareBtn, shareBtn);
        
        // Add click handler
        newShareBtn.addEventListener('click', function() {
            const username = document.getElementById('userSearch').value;
            console.log(`Sharing portfolio ${portfolioId} with user: ${username}`);
            
            // Hide modal
            const modalEl = document.getElementById('sharePortfolioModal');
            if (modalEl && typeof bootstrap !== 'undefined') {
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
            } else {
                // Fallback hide
                document.getElementById('sharePortfolioModal').style.display = 'none';
            }
            
            // Clear input
            document.getElementById('userSearch').value = '';
        });
    }
    
    /**
     * Fallback method to display modal without Bootstrap
     * @param {HTMLElement} modalEl - The modal element
     * @param {string} portfolioId - The ID of the portfolio to share
     */
    function fallbackModalDisplay(modalEl, portfolioId) {
        // Show modal
        modalEl.style.display = 'block';
        modalEl.classList.add('show');
        document.body.classList.add('modal-open');
        
        // Add backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        document.body.appendChild(backdrop);
        
        // Set up close buttons
        const closeButtons = modalEl.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                modalEl.style.display = 'none';
                modalEl.classList.remove('show');
                document.body.classList.remove('modal-open');
                if (document.body.contains(backdrop)) {
                    document.body.removeChild(backdrop);
                }
            });
        });
        
        // Set up share button
        setupShareButton(portfolioId);
    }
});