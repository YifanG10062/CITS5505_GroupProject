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
    }
    
    /**
     * Update all allocation UI elements
     */
    function updateAllocationUI() {
        if (selectedAssets.length === 0) {
            noAssetsDiv.style.display = 'block';
            createButton.disabled = true;
            totalAllocationDisplay.textContent = '0%';
            
            // Handle class replacement safely
            if (totalAllocationDisplay.classList.contains('valid')) {
                totalAllocationDisplay.classList.remove('valid');
                totalAllocationDisplay.classList.add('invalid');
            }
        } else {
            noAssetsDiv.style.display = 'none';
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
                    
                    // Create allocation item with design-matching markup using edit.svg
                    allocationItem.innerHTML = `
                        <div class="allocation-asset">
                            <div class="asset-code">${asset.code}</div>
                        </div>
                        <div class="allocation-value" data-asset-code="${asset.code}">
                            <img src="${getStaticUrl('/static/icons/edit.svg')}" alt="Edit" class="edit-icon">
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
                <input type="number" min="0" max="100" value="${currentValue}" class="allocation-edit-input">
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
     * Show allocation slider UI
     */
    function showAllocationSlider(assetCode, currentValue) {
        // Create slider UI at bottom of screen
        const sliderContainer = document.createElement('div');
        sliderContainer.className = 'allocation-slider-container';
        sliderContainer.innerHTML = `
            <div class="allocation-slider-header">
                <div class="allocation-slider-label">${assetCode} Allocation</div>
                <div class="allocation-slider-value">${currentValue}%</div>
            </div>
            <div class="allocation-slider-bar">
                <input type="range" class="form-range" min="0" max="100" value="${currentValue}" step="1">
            </div>
            <div class="allocation-slider-actions">
                <button class="btn-cancel">Cancel</button>
                <button class="btn-save">Save</button>
            </div>
        `;
        
        document.body.appendChild(sliderContainer);
        
        // Add event listeners
        const rangeInput = sliderContainer.querySelector('input[type="range"]');
        const valueDisplay = sliderContainer.querySelector('.allocation-slider-value');
        
        rangeInput.addEventListener('input', function() {
            valueDisplay.textContent = `${this.value}%`;
        });
        
        // Cancel button
        sliderContainer.querySelector('.btn-cancel').addEventListener('click', function() {
            document.body.removeChild(sliderContainer);
        });
        
        // Save button
        sliderContainer.querySelector('.btn-save').addEventListener('click', function() {
            const newValue = parseInt(rangeInput.value);
            allocations[assetCode] = newValue;
            updateAllocationItems();
            document.body.removeChild(sliderContainer);
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
});