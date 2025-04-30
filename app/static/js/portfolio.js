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
    
    // Detect page type
    const isPortfolioCreationPage = allocationContainer && noAssetsDiv && totalAllocationDisplay;
    const isPortfolioListPage = document.getElementById('listViewBtn') || 
                               document.getElementById('portfolios-container') || 
                               document.querySelector('.portfolios-table');
    
    console.log('Page detection:', { 
        isPortfolioCreationPage, 
        isPortfolioListPage 
    });
    
    // Only initialize portfolio creation features if we're on the creation page
    if (isPortfolioCreationPage) {
        console.log('Portfolio creation page detected, initializing allocation features');
        initPortfolioCreation();
    } else {
        console.log('Not on portfolio creation page, skipping allocation features');
    }
    
    // Only initialize portfolio list features (including share modal) if on list page
    if (isPortfolioListPage) {
        console.log('Portfolio list page detected, initializing list features');
        initPortfolioListView();
        initSharePortfolioModal();
    }
    
    /**
     * Initialize portfolio creation features
     */
    function initPortfolioCreation() {
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
    }
    
    /**
     * Initialize portfolio list view/card view toggle functionality
     * And other portfolio list page features
     */
    function initPortfolioListView() {
        const listViewBtn = document.getElementById('listViewBtn');
        const cardViewBtn = document.getElementById('cardViewBtn');
        const listView = document.getElementById('listView');
        const cardView = document.getElementById('cardView');
        const includeSharedToggle = document.getElementById('includeSharedToggle');
        
        if (listViewBtn && cardViewBtn && listView && cardView) {
            console.log('Portfolio list view elements found, initializing view toggles');
            
            // Add event listeners for view switching
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
                console.log('Include shared portfolios:', this.checked);
                // For now, we'll just log the change
            });
        }
        
        // Setup sort functionality for table columns
        const sortableHeaders = document.querySelectorAll('.portfolios-table th .sort-icon');
        sortableHeaders.forEach(header => {
            header.parentElement.addEventListener('click', function() {
                console.log('Sort by:', this.textContent.trim());
            });
        });
    }
    
    /**
     * Initialize the share portfolio modal
     * Only used on portfolio list pages
     */
    function initSharePortfolioModal() {
        console.log('Initializing share portfolio modal');
        
        // Check if modal exists first
        const modalEl = document.getElementById('sharePortfolioModal');
        if (!modalEl) {
            console.warn('Share portfolio modal not found in the DOM, skipping initialization');
            return;
        }
        
        // Find all share links with standard DOM selectors
        // Use various approaches to find all possible share links
        const shareLinks = [];
        
        // Method 1: Find links with text content "Share"
        document.querySelectorAll('a').forEach(link => {
            if (link.textContent.trim() === 'Share') {
                shareLinks.push(link);
            }
        });
        
        // Method 2: Use standard attribute selectors
        document.querySelectorAll('a[data-action="share"], .share-btn').forEach(link => {
            if (!shareLinks.includes(link)) {
                shareLinks.push(link);
            }
        });
        
        console.log('Found share links:', shareLinks.length);
        
        // For each share link, add click handler
        shareLinks.forEach(link => {
            console.log('Found share link:', link.outerHTML);
            
            // Remove existing listeners first to avoid duplication
            const newLink = link.cloneNode(true);
            link.parentNode.replaceChild(newLink, link);
            
            // Add click event handler with debugging
            newLink.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('Share link clicked!');
                
                // Get the portfolio ID
                // First try from data attributes
                let portfolioId = this.dataset.portfolioId || this.dataset.id;
                
                // Then try from parent elements
                if (!portfolioId) {
                    const row = this.closest('tr, .portfolio-card');
                    if (row) {
                        portfolioId = row.dataset.portfolioId || row.dataset.id;
                    }
                }
                
                // Last resort - check href if it's a link
                if (!portfolioId && this.href) {
                    const matches = this.href.match(/portfolio[\/=](\d+)/i);
                    if (matches && matches[1]) {
                        portfolioId = matches[1];
                    }
                }
                
                portfolioId = portfolioId || 'unknown';
                console.log('Sharing portfolio ID:', portfolioId);
                
                // Store portfolio ID in modal for later use
                modalEl.dataset.portfolioId = portfolioId;
                
                // Try multiple methods to show the modal
                try {
                    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                        // Bootstrap 5 method
                        const modal = new bootstrap.Modal(modalEl);
                        modal.show();
                        console.log('Modal shown using Bootstrap API');
                    } else if (typeof $ !== 'undefined' && $(modalEl).modal) {
                        // jQuery Bootstrap method (version 4 or earlier)
                        $(modalEl).modal('show');
                        console.log('Modal shown using jQuery Bootstrap API');
                    } else {
                        // Fallback to manual display
                        console.log('Using fallback modal display method');
                        fallbackModalDisplay(modalEl);
                    }
                    
                    // Set up share button handler
                    setupShareButton(portfolioId);
                } catch (err) {
                    console.error('Error showing modal:', err);
                    fallbackModalDisplay(modalEl);
                }
            });
        });
        
        // If no share links were found with the above methods, try a more direct approach
        if (shareLinks.length === 0) {
            console.warn('No share links found with standard methods, trying direct table cell access');
            
            // Look for links inside the last column of each table row
            const tableRows = document.querySelectorAll('.portfolios-table tr');
            tableRows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length > 0) {
                    // Get the last cell
                    const lastCell = cells[cells.length - 1];
                    const links = lastCell.querySelectorAll('a');
                    
                    links.forEach(link => {
                        if (link.textContent.trim() === 'Share') {
                            console.log('Found share link in table cell:', link.outerHTML);
                            
                            // Attach event listener directly
                            link.addEventListener('click', function(e) {
                                e.preventDefault();
                                console.log('Share link clicked from table cell!');
                                
                                // Get portfolio ID from row if available
                                const portfolioId = row.dataset.portfolioId || row.dataset.id || 'unknown';
                                console.log('Portfolio ID from table row:', portfolioId);
                                
                                // Show modal
                                modalEl.dataset.portfolioId = portfolioId;
                                
                                // Create and show bootstrap modal
                                try {
                                    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                                        const modal = new bootstrap.Modal(modalEl);
                                        modal.show();
                                    } else {
                                        fallbackModalDisplay(modalEl);
                                    }
                                    
                                    setupShareButton(portfolioId);
                                } catch (err) {
                                    console.error('Error showing modal from table cell click:', err);
                                    fallbackModalDisplay(modalEl);
                                }
                            });
                        }
                    });
                }
            });
        }
    }
    
    /**
     * Set up share button click handler
     * @param {string} portfolioId - The ID of the portfolio to share
     */
    function setupShareButton(portfolioId) {
        const shareBtn = document.getElementById('sharePortfolioBtn');
        if (!shareBtn) {
            console.error('Share button not found in modal!');
            return;
        }
        
        // Create new button to avoid duplicate listeners
        const newShareBtn = shareBtn.cloneNode(true);
        shareBtn.parentNode.replaceChild(newShareBtn, shareBtn);
        
        // Add click handler with debugging
        newShareBtn.addEventListener('click', function() {
            const username = document.getElementById('userSearch')?.value || '';
            console.log(`Attempting to share portfolio ${portfolioId} with user: ${username}`);
            
            if (!username.trim()) {
                alert('Please enter a username to share with');
                return;
            }
            
            // Here you would normally send an AJAX request to share the portfolio
            // For demo purposes, just log and show success message
            console.log(`Successfully shared portfolio ${portfolioId} with ${username}`);
            alert(`Portfolio shared with ${username}`);
            
            // Hide modal
            const modalEl = document.getElementById('sharePortfolioModal');
            try {
                if (modalEl && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                } else if ($(modalEl).modal) {
                    $(modalEl).modal('hide');
                } else {
                    // Fallback hide
                    modalEl.style.display = 'none';
                    const backdrop = document.querySelector('.modal-backdrop');
                    if (backdrop) backdrop.parentNode.removeChild(backdrop);
                    document.body.classList.remove('modal-open');
                }
            } catch (err) {
                console.error('Error hiding modal:', err);
                // Force hide as last resort
                modalEl.style.display = 'none';
            }
            
            // Clear input
            if (document.getElementById('userSearch')) {
                document.getElementById('userSearch').value = '';
            }
        });
    }
    
    /**
     * Fallback method to display modal without Bootstrap
     * @param {HTMLElement} modalEl - The modal element
     */
    function fallbackModalDisplay(modalEl) {
        // Show modal manually
        modalEl.style.display = 'block';
        modalEl.classList.add('show');
        document.body.classList.add('modal-open');
        
        // Create backdrop if it doesn't exist
        let backdrop = document.querySelector('.modal-backdrop');
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            document.body.appendChild(backdrop);
        }
        
        // Set up close buttons
        const closeButtons = modalEl.querySelectorAll('[data-bs-dismiss="modal"], .close, .btn-close');
        closeButtons.forEach(btn => {
            // Replace with new element to avoid duplicate listeners
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            
            newBtn.addEventListener('click', function() {
                modalEl.style.display = 'none';
                modalEl.classList.remove('show');
                document.body.classList.remove('modal-open');
                if (backdrop && document.body.contains(backdrop)) {
                    document.body.removeChild(backdrop);
                }
            });
        });
        
        // Also close when clicking backdrop
        backdrop.addEventListener('click', function() {
            modalEl.style.display = 'none';
            modalEl.classList.remove('show');
            document.body.classList.remove('modal-open');
            if (document.body.contains(backdrop)) {
                document.body.removeChild(backdrop);
            }
        });
        
        // Set up portfolio ID for sharing
        const portfolioId = modalEl.dataset.portfolioId;
        setupShareButton(portfolioId);
    }
});

// View Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    const listViewBtn = document.getElementById('listViewBtn');
    const cardViewBtn = document.getElementById('cardViewBtn');
    const listView = document.getElementById('listView');
    const cardView = document.getElementById('cardView');
    
    if (listViewBtn && cardViewBtn) {
        listViewBtn.addEventListener('click', function() {
            listViewBtn.classList.add('active');
            cardViewBtn.classList.remove('active');
            listView.classList.remove('d-none');
            cardView.classList.add('d-none');
        });
        
        cardViewBtn.addEventListener('click', function() {
            cardViewBtn.classList.add('active');
            listViewBtn.classList.remove('active');
            cardView.classList.remove('d-none');
            listView.classList.add('d-none');
        });
    }
});