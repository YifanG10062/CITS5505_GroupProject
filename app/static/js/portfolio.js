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
            // Reset to 33/33/34
            const keys = Object.keys(allocations);
            keys.forEach((key, index) => {
                allocations[key] = index === 2 ? 34 : 33;
            });
            allocations[assetCode] = 33;
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
            // Clear existing items (except the no-assets div)
            const existingItems = allocationContainer.querySelectorAll('.allocation-item');
            existingItems.forEach(item => item.remove());
            
            // Create items for each selected asset
            selectedAssets.forEach(asset => {
                const allocation = allocations[asset.code];
                
                const allocationItem = document.createElement('div');
                allocationItem.className = 'allocation-item';
                allocationItem.dataset.assetCode = asset.code;
                
                allocationItem.innerHTML = `
                    <div class="allocation-asset">
                        <img src="${asset.logoSrc}" class="asset-icon-sm" alt="${asset.name}">
                        <div class="allocation-name">${asset.name}</div>
                    </div>
                    <div class="allocation-control">
                        <div class="allocation-input">
                            <input type="range" class="form-range" min="0" max="100" step="1" 
                                value="${allocation}" data-asset-code="${asset.code}">
                            <input type="number" class="form-control" min="0" max="100" 
                                name="allocation[${asset.code}]" value="${allocation}" required>
                            <span class="percentage">%</span>
                        </div>
                    </div>
                `;
                
                allocationContainer.appendChild(allocationItem);
                
                // Add event listeners to the new controls
                const rangeInput = allocationItem.querySelector('.form-range');
                const numberInput = allocationItem.querySelector('.form-control');
                
                if (rangeInput && numberInput) {
                    rangeInput.addEventListener('input', function() {
                        numberInput.value = this.value;
                        allocations[asset.code] = parseInt(this.value);
                        updateAllocationUI();
                    });
                    
                    numberInput.addEventListener('input', function() {
                        rangeInput.value = this.value;
                        allocations[asset.code] = parseInt(this.value);
                        updateAllocationUI();
                    });
                }
            });
            
            updateAllocationUI();
        } catch (error) {
            console.error('Error updating allocation items:', error);
        }
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