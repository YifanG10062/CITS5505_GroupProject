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
    
    // Dynamic tooltip positioning
    // Positions tooltips based on available space in viewport
    function initTooltipPositioning() {
        // Get all info icons that can trigger tooltips
        const infoIcons = document.querySelectorAll('.share-info-icon');
        
        infoIcons.forEach(icon => {
            // Add mouseover event to position tooltip before showing
            icon.addEventListener('mouseover', function() {
                const wrapper = this.closest('.share-history-wrapper');
                const tooltip = wrapper.querySelector('.share-history-tooltip');
                
                if (!tooltip) return;
                
                // Get positions
                const iconRect = this.getBoundingClientRect();
                const viewportHeight = window.innerHeight;
                const viewportWidth = window.innerWidth;
                
                // Remove all positioning classes
                tooltip.classList.remove('tooltip-top', 'tooltip-bottom');
                
                // Calculate available space above and below
                const spaceAbove = iconRect.top;
                const spaceBelow = viewportHeight - iconRect.bottom;
                
                // Default tooltip width
                const tooltipWidth = 250;
                
                // Determine left position (keep tooltip within viewport)
                let leftPos = iconRect.left - 20; // align arrow with icon
                
                // Check if tooltip would go off-screen to the right
                if (leftPos + tooltipWidth > viewportWidth) {
                    leftPos = viewportWidth - tooltipWidth - 10;
                }
                
                // Check if tooltip would go off-screen to the left
                if (leftPos < 10) {
                    leftPos = 10;
                }
                
                // Position tooltip based on available space
                if (spaceAbove >= 200 || spaceAbove > spaceBelow) {
                    // Position above the icon
                    tooltip.style.bottom = (viewportHeight - iconRect.top + 10) + 'px';
                    tooltip.style.top = 'auto';
                    tooltip.classList.add('tooltip-top');
                } else {
                    // Position below the icon
                    tooltip.style.top = (iconRect.bottom + 10) + 'px';
                    tooltip.style.bottom = 'auto';
                    tooltip.classList.add('tooltip-bottom');
                }
                
                // Set horizontal position
                tooltip.style.left = leftPos + 'px';
            });
        });
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
        initTooltipPositioning(); // Initialize tooltip positioning
    }
    
    /**
     * Initialize portfolio creation features
     */
    function initPortfolioCreation() {
        // State variables
        let selectedAssets = [];
        let allocations = {};
        
        // Check if we're in edit mode and initialize current allocations
        function initEditMode() {
            // Check if currentAllocation is defined in the global scope (set by server-side template)
            if (typeof currentAllocation !== 'undefined' && currentAllocation) {
                console.log('Edit mode detected with current allocation:', currentAllocation);
                
                // For each asset in the current allocation, select it
                Object.keys(currentAllocation).forEach(assetCode => {
                    const percent = currentAllocation[assetCode] * 100;
                    
                    // Find the asset card for this code
                    const assetCard = document.querySelector(`.asset-card[data-asset-code="${assetCode}"]`);
                    if (assetCard) {
                        // Get asset details
                        const assetName = assetCard.querySelector('.asset-name').innerText;
                        const assetCompany = assetCard.querySelector('.asset-company').innerText;
                        const assetLogoSrc = assetCard.querySelector('.asset-icon img').src;
                        
                        // Select the asset card
                        assetCard.classList.add('selected');
                        
                        // Add to selected assets
                        selectedAssets.push({
                            code: assetCode,
                            name: assetName,
                            company: assetCompany,
                            logoSrc: assetLogoSrc
                        });
                        
                        // Set allocation
                        allocations[assetCode] = Math.round(percent);
                    }
                });
                
                // Update the UI
                updateAllocationItems();
                updateCardStates();
            }
        }
        
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
        
        // Check if we're in edit mode and initialize accordingly
        initEditMode();
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
        const sortableHeaders = document.querySelectorAll('.sortable');
        let currentSortColumn = null;
        let currentSortDirection = 'none';
        
        if (sortableHeaders.length > 0) {
            console.log('Found sortable headers, initializing sort functionality');
            
            sortableHeaders.forEach(header => {
                // Initialize sort icons
                const iconImg = header.querySelector('.sort-icon');
                if (iconImg) {
                    iconImg.src = "/static/icons/sort-neutral.svg";
                }
                
                header.addEventListener('click', function() {
                    const sortKey = this.dataset.sort;
                    console.log('Sort by:', sortKey);
                    
                    // Check if we're clicking the same column
                    if (currentSortColumn === sortKey) {
                        // Cycle through sort directions:
                        // none -> desc -> asc -> none (default/creation time)
                        if (currentSortDirection === 'none') {
                            currentSortDirection = 'desc'; // First click: largest first (descending)
                            const icon = this.querySelector('.sort-icon');
                            if (icon) icon.src = "/static/icons/sort-desc.svg";
                        } else if (currentSortDirection === 'desc') {
                            currentSortDirection = 'asc'; // Second click: smallest first (ascending)
                            const icon = this.querySelector('.sort-icon');
                            if (icon) icon.src = "/static/icons/sort-asc.svg";
                        } else {
                            // Third click: back to default sort
                            currentSortDirection = 'none';
                            currentSortColumn = null;
                            const icon = this.querySelector('.sort-icon');
                            if (icon) icon.src = "/static/icons/sort-neutral.svg";
                        }
                    } else {
                        // Reset all other headers
                        sortableHeaders.forEach(h => {
                            h.setAttribute('data-direction', 'none');
                            const icon = h.querySelector('.sort-icon');
                            if (icon) icon.src = "/static/icons/sort-neutral.svg";
                        });
                        
                        // New column, start with desc (largest first)
                        currentSortDirection = 'desc';
                        currentSortColumn = sortKey;
                        const icon = this.querySelector('.sort-icon');
                        if (icon) icon.src = "/static/icons/sort-desc.svg";
                    }
                    
                    // Set data attribute for visual indication
                    this.setAttribute('data-direction', currentSortDirection);
                    
                    // Sort the table based on current state
                    if (currentSortColumn === null || currentSortDirection === 'none') {
                        // Reset to default sort (by creation time, newest first)
                        sortByCreationTime();
                    } else {
                        // Sort by selected column and direction
                        sortPortfolioTable(currentSortColumn, currentSortDirection);
                    }
                });
            });
            
            // Initial sort by creation time
            sortByCreationTime();
        }
        
        /**
         * Sort portfolios by creation time (newest first)
         * This is the default sort order
         */
        function sortByCreationTime() {
            const table = document.querySelector('.portfolios-table');
            if (!table) {
                console.error('Portfolio table not found');
                return;
            }
            
            const tbody = table.querySelector('tbody');
            if (!tbody) {
                console.error('Table body not found');
                return;
            }
            
            // Get all rows except the "no data" row
            const rows = Array.from(tbody.querySelectorAll('tr:not(#noDataRow)'));
            
            // Sort rows by creation timestamp (newest first)
            // Using data attribute for creation time
            rows.sort((a, b) => {
                // Try to get timestamp from data attribute
                const timeA = parseInt(a.dataset.createdAt || '0');
                const timeB = parseInt(b.dataset.createdAt || '0');
                
                // Descending order (newest first)
                return timeB - timeA;
            });
            
            // Re-append rows in the sorted order
            rows.forEach(row => {
                tbody.appendChild(row);
            });
            
            console.log('Sorted table by creation time (newest first)');
        }
        
        /**
         * Sort the portfolio table based on column and direction
         * @param {string} column - The column identifier to sort by
         * @param {string} direction - The sort direction ('asc' or 'desc')
         */
        function sortPortfolioTable(column, direction) {
            const table = document.querySelector('.portfolios-table');
            if (!table) {
                console.error('Portfolio table not found');
                return;
            }
            
            const tbody = table.querySelector('tbody');
            if (!tbody) {
                console.error('Table body not found');
                return;
            }
            
            // Get all rows except the "no data" row
            const rows = Array.from(tbody.querySelectorAll('tr:not(#noDataRow)'));
            
            // Sort the rows
            rows.sort((a, b) => {
                let valueA, valueB;
                
                // Extract values based on the column being sorted
                switch(column) {
                    case 'current-value':
                        valueA = parseFloat(a.querySelector('.current-value').textContent.replace(/[^0-9.-]+/g, ''));
                        valueB = parseFloat(b.querySelector('.current-value').textContent.replace(/[^0-9.-]+/g, ''));
                        break;
                    case 'return-percent':
                        valueA = parseFloat(a.querySelector('.return-positive').textContent.replace(/[^0-9.-]+/g, ''));
                        valueB = parseFloat(b.querySelector('.return-positive').textContent.replace(/[^0-9.-]+/g, ''));
                        break;
                    case 'cagr':
                        // For CAGR, we need to target the second .return-positive cell in the row
                        const cagrCellsA = a.querySelectorAll('.return-positive');
                        const cagrCellsB = b.querySelectorAll('.return-positive');
                        valueA = parseFloat(cagrCellsA[1]?.textContent.replace(/[^0-9.-]+/g, '') || '0');
                        valueB = parseFloat(cagrCellsB[1]?.textContent.replace(/[^0-9.-]+/g, '') || '0');
                        break;
                    case 'volatility':
                        valueA = parseFloat(a.querySelector('.metric-value').textContent.replace(/[^0-9.-]+/g, ''));
                        valueB = parseFloat(b.querySelector('.metric-value').textContent.replace(/[^0-9.-]+/g, ''));
                        break;
                    case 'max-drawdown':
                        valueA = parseFloat(a.querySelector('.return-negative').textContent.replace(/[^0-9.-]+/g, ''));
                        valueB = parseFloat(b.querySelector('.return-negative').textContent.replace(/[^0-9.-]+/g, ''));
                        break;
                    default:
                        console.warn('Unsupported sort column:', column);
                        return 0;
                }
                
                // Handle NaN values
                if (isNaN(valueA)) valueA = 0;
                if (isNaN(valueB)) valueB = 0;
                
                // Sort based on direction
                if (direction === 'asc') {
                    return valueA - valueB; // Ascending: smallest first
                } else {
                    return valueB - valueA; // Descending: largest first
                }
            });
            
            // Re-append rows in the sorted order
            rows.forEach(row => {
                tbody.appendChild(row);
            });
            
            console.log(`Sorted table by ${column} in ${direction} order`);
        }
        
        // Portfolio filtering functionality
        const filterRadios = document.querySelectorAll('input[name="portfolioFilter"]');
        const portfolioRows = document.querySelectorAll('.portfolios-table tbody tr:not(#noDataRow)');
        const noDataRow = document.getElementById('noDataRow');
        const currentUsername = document.querySelector('meta[name="username"]')?.content;
        
        // Function to filter portfolios based on selection
        function filterPortfolios(filterValue) {
            let visibleCount = 0;
            
            portfolioRows.forEach(row => {
                const creatorCell = row.querySelector('.creator-cell');
                const creatorUsername = creatorCell.querySelector('span').textContent.trim();
                const isShared = creatorCell.querySelector('.shared-badge') !== null;
                
                let isVisible = false;
                
                switch(filterValue) {
                    case 'all':
                        isVisible = true;
                        break;
                    case 'mine':
                        isVisible = (creatorUsername === currentUsername);
                        break;
                    case 'shared':
                        isVisible = isShared;
                        break;
                }
                
                row.style.display = isVisible ? '' : 'none';
                
                if (isVisible) {
                    visibleCount++;
                }
            });
            
            // Show or hide the "no data" message based on visible rows count
            if (visibleCount === 0) {
                noDataRow.classList.remove('d-none');
            } else {
                noDataRow.classList.add('d-none');
            }
        }
        
        // Add event listeners to filter radio buttons
        filterRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                filterPortfolios(this.value);
            });
        });
        
        // Initialize with "All" filter
        filterPortfolios('all');
        
        // Portfolio filtering with tabs
        const filterTabs = document.querySelectorAll('.filter-tab');
        
        // Add event listeners to filter tabs
        filterTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // Remove active class from all tabs
                filterTabs.forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked tab
                this.classList.add('active');
                
                // Filter portfolios
                filterPortfolios(this.dataset.filter);
            });
        });
        
        // Initialize with "All" filter
        filterPortfolios('all');

        // Initialize delete portfolio functionality
        initDeletePortfolio();
    }

    /**
     * Initialize delete portfolio functionality
     * Handles delete button clicks and calls the delete API
     */
    function initDeletePortfolio() {
        console.log('Initializing delete portfolio functionality');
        
        // Find all delete buttons (both in list and card views)
        const deleteButtons = document.querySelectorAll('.action-link.delete, .delete-portfolio-btn');
        const deleteModal = new bootstrap.Modal(document.getElementById('deleteConfirmModal'));
        let portfolioToDelete = null;
        let buttonClicked = null;
        
        console.log(`Found ${deleteButtons.length} delete buttons`);
        
        deleteButtons.forEach(button => {
            // Replace with new button to remove any existing listeners
            const newButton = button.cloneNode(true);
            if (button.parentNode) {
                button.parentNode.replaceChild(newButton, button);
                
                // Add click event listener to the new button
                newButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // Get portfolio ID from data attribute
                    portfolioToDelete = this.dataset.portfolioId;
                    buttonClicked = this;
                    
                    if (!portfolioToDelete) {
                        console.error('No portfolio ID found for delete button');
                        return;
                    }
                    
                    console.log(`Delete button clicked for portfolio ID: ${portfolioToDelete}`);
                    
                    // Show delete confirmation modal
                    deleteModal.show();
                });
            }
        });

        // Handle confirm delete button click
        document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
            if (!portfolioToDelete || !buttonClicked) return;

            // Show loading state
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...';
            buttonClicked.disabled = true;
            
            // Send delete request to server
            fetch(`/portfolios/${portfolioToDelete}/delete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Delete response:', data);
                
                if (data.success) {
                    // Remove the portfolio element from the UI
                    const row = buttonClicked.closest('tr');
                    const card = buttonClicked.closest('.portfolio-card');
                    
                    // Handle removal from both views
                    if (row) {
                        row.remove();
                    }
                    
                    if (card) {
                        card.remove();
                    }
                    
                    // Show success message
                    const alertHTML = `
                        <div class="alert alert-success alert-dismissible fade show" role="alert">
                            Portfolio deleted successfully
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    `;
                    
                    // Create alert container that appears below navbar and centered
                    let alertContainer = document.getElementById('global-alert-container');
                    if (!alertContainer) {
                        alertContainer = document.createElement('div');
                        alertContainer.id = 'global-alert-container';
                        
                        // Style for centered positioning below navbar
                        alertContainer.style.position = 'fixed';
                        alertContainer.style.top = '80px'; // Position below navbar
                        alertContainer.style.left = '50%';
                        alertContainer.style.transform = 'translateX(-50%)';
                        alertContainer.style.zIndex = '9999';
                        alertContainer.style.width = '80%'; 
                        alertContainer.style.maxWidth = '800px'; 
                        
                        document.body.appendChild(alertContainer);
                    }
                    
                    // Add the alert to the container
                    alertContainer.innerHTML = alertHTML;
                    
                    // Auto-close the alert after 5 seconds
                    setTimeout(() => {
                        const alert = alertContainer.querySelector('.alert');
                        if (alert) {
                            // Try to close using Bootstrap API first
                            try {
                                const bsAlert = new bootstrap.Alert(alert);
                                bsAlert.close();
                            } catch (e) {
                                // Fallback: remove directly
                                alert.remove();
                            }
                        }
                    }, 5000);
                    
                    // Check if we need to show "no data" message
                    const tbody = document.querySelector('.portfolios-table tbody');
                    if (tbody && tbody.querySelectorAll('tr:not(#noDataRow)').length === 0) {
                        const noDataRow = document.getElementById('noDataRow');
                        if (noDataRow) {
                            noDataRow.classList.remove('d-none');
                        }
                    }
                    
                    // Check for card view
                    const cardContainer = document.getElementById('cardView');
                    if (cardContainer && cardContainer.querySelectorAll('.portfolio-card').length === 0) {
                        const noDataCards = document.getElementById('noDataCards');
                        if (noDataCards) {
                            noDataCards.classList.remove('d-none');
                        }
                    }

                    // Hide the modal
                    deleteModal.hide();
                } else {
                    // Show error message
                    alert(`Failed to delete portfolio: ${data.message || 'Unknown error'}`);
                }
            })
            .catch(error => {
                console.error('Error deleting portfolio:', error);
                alert('Failed to delete portfolio. Please try again.');
            })
            .finally(() => {
                // Reset button states
                this.disabled = false;
                this.innerHTML = 'Delete';
                if (buttonClicked) {
                    buttonClicked.disabled = false;
                }
            });
        });
    }

    // View switching functionality
    const listViewBtn = document.getElementById('listViewBtn');
    const cardViewBtn = document.getElementById('cardViewBtn');
    const listView = document.getElementById('listView');
    const cardView = document.getElementById('cardView');
    
    // Switch to list view
    listViewBtn.addEventListener('click', function() {
        listViewBtn.classList.add('active');
        cardViewBtn.classList.remove('active');
        listView.classList.remove('d-none');
        cardView.classList.add('d-none');
    });
    
    // Switch to card view
    cardViewBtn.addEventListener('click', function() {
        cardViewBtn.classList.add('active');
        listViewBtn.classList.remove('active');
        cardView.classList.remove('d-none');
        listView.classList.add('d-none');
    });
    
    // Portfolio filtering functionality for both views
    const filterAll = document.getElementById('filterAll');
    const filterMine = document.getElementById('filterMine');
    const filterShared = document.getElementById('filterShared');
    
    // Filter function that applies to both views
    function applyFilter(filter) {
        // Get all portfolio rows and cards
        const portfolioRows = document.querySelectorAll('#listView tbody tr:not(#noDataRow)');
        const portfolioCards = document.querySelectorAll('.portfolio-card');
        
        let visibleCount = 0;
        
        // Filter list view
        portfolioRows.forEach(row => {
            const isShared = row.querySelector('.shared-badge') !== null;
            
            if (filter === 'all' || 
                (filter === 'shared' && isShared) || 
                (filter === 'mine' && !isShared)) {
                row.classList.remove('d-none');
                visibleCount++;
            } else {
                row.classList.add('d-none');
            }
        });
        
        // Filter card view
        portfolioCards.forEach(card => {
            const isShared = card.querySelector('.shared-badge') !== null;
            
            if (filter === 'all' || 
                (filter === 'shared' && isShared) || 
                (filter === 'mine' && !isShared)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
        
        // Show/hide no data message for list view
        const noDataRow = document.getElementById('noDataRow');
        if (visibleCount === 0 && noDataRow) {
            noDataRow.classList.remove('d-none');
        } else if (noDataRow) {
            noDataRow.classList.add('d-none');
        }
        
        // Show/hide no data message for card view
        const noDataCards = document.getElementById('noDataCards');
        if (visibleCount === 0 && noDataCards) {
            noDataCards.classList.remove('d-none');
        } else if (noDataCards) {
            noDataCards.classList.add('d-none');
        }
    }
    
    // Add event listeners to radio buttons
    filterAll.addEventListener('change', () => applyFilter('all'));
    filterMine.addEventListener('change', () => applyFilter('mine'));
    filterShared.addEventListener('change', () => applyFilter('shared'));

    // Helper function to get CSRF token
    function getCsrfToken() {
        // Try to get from meta tag
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) return meta.getAttribute('content');
        
        // Try to get from hidden input
        const input = document.querySelector('input[name="csrf_token"]');
        if (input) return input.value;
        
        return '';
    }
    
    /**
     * Initialize the share portfolio modal
     * Only used on portfolio list pages
     */
    function initSharePortfolioModal() {
        console.log('Initializing share portfolio modal');

        const modalEl = document.getElementById('sharePortfolioModal');
        if (!modalEl) {
            console.warn('Share portfolio modal not found in the DOM, skipping initialization');
            return;
        }

        // First ensure all Edit links and portfolio title links keep their default behavior
        document.querySelectorAll('.action-link.edit, a[href*="edit"], a[href*="edit_portfolio"], .portfolio-name-cell a, a.portfolio-title').forEach(link => {
            // Ensure these links are not modified - they should follow their href normally
            link.addEventListener('click', function(e) {
                // Let default navigation happen - don't call preventDefault() 
                console.log('Navigation link clicked, allowing default navigation to:', this.href);
            });
        });

        // Find share links using MUCH more specific selectors to avoid capturing navigation links
        // First clear the links array
        let shareLinks = [];
        
        // Method 1: Find links with action-link class that have exact text content "Share"
        document.querySelectorAll('.action-link, .share-btn').forEach(link => {
            if (link.textContent.trim() === 'Share' && 
                !link.classList.contains('edit') && 
                !link.classList.contains('portfolio-title') &&
                !(link.href && link.href.includes('edit'))) {
                shareLinks.push(link);
                console.log('Found share link by text content:', link.outerHTML);
            }
        });
        
        // Method 2: Use very specific attribute selectors - exclude navigation links
        document.querySelectorAll('a.action-link:not(.delete):not(.edit):not(.portfolio-title), a.share-btn, button.share-btn, [data-action="share"]').forEach(link => {
            // Exclude any links in the portfolio name cell
            if (!link.closest('.portfolio-name-cell') && !shareLinks.includes(link)) {
                shareLinks.push(link);
                console.log('Found share link by class/attribute selector:', link.outerHTML);
            }
        });
        
        // Method 3: Target only links in the share action cell
        document.querySelectorAll('.action-cell a').forEach(link => {
            if (link.textContent.trim() === 'Share' && 
                !shareLinks.includes(link) && 
                !link.classList.contains('edit') &&
                !link.closest('.portfolio-name-cell')) {
                shareLinks.push(link);
                console.log('Found share link in action cell:', link.outerHTML);
            }
        });
        
        console.log(`Total found ${shareLinks.length} share links in the page`);
        
        if (shareLinks.length === 0) {
            console.warn('No share links found with standard selectors, trying with plain query');
            // Last attempt: Use more specific CSS selectors for share links only
            document.querySelectorAll('.action-cell a:not([class*="delete"]):not([class*="edit"])').forEach(link => {
                // Only process if it's definitely a share link and not a navigation link
                console.log('Checking link:', link.outerHTML, 'Text:', link.textContent.trim());
                if (link.textContent.trim() === 'Share' && 
                    !link.href.includes('edit') &&
                    !link.closest('.portfolio-name-cell')) {
                    shareLinks.push(link);
                    console.log('Added share link with direct selection:', link.outerHTML);
                }
            });
            
            console.log(`After final attempt: found ${shareLinks.length} share links`);
        }
        
        // Add click handler for each share link
        shareLinks.forEach(link => {
            // First clone the node to remove any existing event listeners
            const newLink = link.cloneNode(true);
            if (link.parentNode) {
                link.parentNode.replaceChild(newLink, link);
                
                // Add click event listener
                newLink.addEventListener('click', function(e) {
                    // Double check this is not a navigation link
                    if (this.classList.contains('edit') || 
                        this.classList.contains('portfolio-title') ||
                        this.closest('.portfolio-name-cell') ||
                        (this.href && this.href.includes('edit')) || 
                        this.textContent.trim() === 'Edit') {
                        // Let the default behavior happen for navigation links
                        console.log('Navigation link detected, allowing default navigation');
                        return;
                    }
                    
                    e.preventDefault();
                    console.log('Share link clicked');
                    
                    // Get portfolio ID and name
                    let portfolioId = this.dataset.portfolioId;
                    let portfolioName = '';
                    
                    // Try to get portfolio name from the table row first
                    const row = this.closest('tr');
                    if (row) {
                        const nameCell = row.querySelector('.portfolio-name-cell');
                        if (nameCell) {
                            // Fix: Get only the direct link text without tooltip content
                            const nameLink = nameCell.querySelector('a');
                            if (nameLink) {
                                portfolioName = nameLink.textContent.trim();
                            } else {
                                portfolioName = nameCell.textContent.trim();
                            }
                        }
                        
                        // Try to get ID from row if not in the link
                        if (!portfolioId) {
                            portfolioId = row.dataset.portfolioId;
                            
                            // If row doesn't have ID, try from other links in same row
                            if (!portfolioId) {
                                // Try to extract from "edit" link URL
                                const editLink = row.querySelector('a[href*="edit"]');
                                if (editLink && editLink.href) {
                                    const matches = editLink.href.match(/portfolio_id=(\d+)/);
                                    if (matches && matches[1]) {
                                        portfolioId = matches[1];
                                    }
                                }
                                
                                // Try to get from "delete" link's data attributes
                                if (!portfolioId) {
                                    const deleteLink = row.querySelector('.action-link.delete');
                                    if (deleteLink) {
                                        portfolioId = deleteLink.dataset.portfolioId;
                                    }
                                }
                            }
                        }
                    }
                    
                    // If name not found yet, try card view
                    if (!portfolioName) {
                        const card = this.closest('.portfolio-card');
                        if (card) {
                            const nameElement = card.querySelector('.portfolio-title, .card-title');
                            if (nameElement) {
                                portfolioName = nameElement.textContent.trim();
                            }
                        }
                    }
                    
                    console.log('Portfolio ID for sharing:', portfolioId, 'Name:', portfolioName);
                    
                    // Store portfolio ID and name in modal data attributes
                    modalEl.dataset.portfolioId = portfolioId;
                    modalEl.dataset.portfolioName = portfolioName;
                    
                    // Update modal title with more specific selector
                    const modalTitle = document.querySelector('#sharePortfolioModal .modal-title');
                    if (modalTitle) {
                        console.log('Setting modal title to:', portfolioName ? 
                            `Share Your Portfolio "${portfolioName}"` : 
                            `Share Your Portfolio`);
                        modalTitle.textContent = portfolioName ? 
                            `Share Your Portfolio "${portfolioName}"` : 
                            `Share Your Portfolio`;
                    }
                    
                    // Clear previous user selection
                    resetModalState();
                    
                    // Show modal - try multiple methods
                    try {
                        // Try using Bootstrap 5 API
                        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                            const modal = new bootstrap.Modal(modalEl);
                            modal.show();
                            console.log('Modal shown with Bootstrap 5 API');
                        } else if (typeof $ !== 'undefined') {
                            // Try using jQuery (Bootstrap 4)
                            $(modalEl).modal('show');
                            console.log('Modal shown with jQuery');
                        } else {
                            // Manual display
                            modalEl.style.display = 'block';
                            modalEl.classList.add('show');
                            document.body.classList.add('modal-open');
                            
                            // Add backdrop
                            const backdrop = document.createElement('div');
                            backdrop.className = 'modal-backdrop fade show';
                            document.body.appendChild(backdrop);
                            console.log('Modal shown manually');
                        }
                    } catch (error) {
                        console.error('Error showing modal:', error);
                        // Fall back to manual display on error
                        modalEl.style.display = 'block';
                        modalEl.classList.add('show');
                    }
                    
                    // Just before opening the modal
                    console.log('Modal Data Before Show:', {
                        portfolioId: modalEl.dataset.portfolioId,
                        portfolioName: modalEl.dataset.portfolioName,
                        titleElement: modalEl.querySelector('.modal-title')?.textContent
                    });
                });
            }
        });

        const userSearchInput = document.getElementById('userSearch');
        const userSearchResults = document.getElementById('userSearchResults');
        const sharePortfolioBtn = document.getElementById('sharePortfolioBtn');
        let selectedUserId = null; // State to store the selected user ID
        let allUsers = []; // Cache for all users

        // Load users when the modal is shown - use both Bootstrap 4 and 5 event syntax
        modalEl.addEventListener('shown.bs.modal', function () {
            // Load users in the background but don't show the dropdown
            loadUsers(false); 
            resetModalState();
        });
        
        // Also handle jQuery event for Bootstrap 4
        if (typeof $ !== 'undefined') {
            $(modalEl).on('shown.bs.modal', function() {
                // Load users in the background but don't show the dropdown
                loadUsers(false);
                resetModalState();
            });
        }

        // Handle input focus to show dropdown
        if (userSearchInput) {
            userSearchInput.addEventListener('focus', function() {
                console.log('User search input focused');
                // Show dropdown only when focused
                filterUsers(this.value.trim().toLowerCase());
                userSearchResults.style.display = 'block';
            });
            
            // Handle input for filtering users
            userSearchInput.addEventListener('input', function () {
                const searchTerm = userSearchInput.value.trim().toLowerCase();
                console.log('Filtering users with term:', searchTerm);
                filterUsers(searchTerm);
                userSearchResults.style.display = 'block';
            });
            
            // Also handle keyboard events to improve UX
            userSearchInput.addEventListener('keydown', function(e) {
                if (e.key === 'ArrowDown' && userSearchResults.children.length > 0) {
                    // Focus on first result when pressing down arrow
                    const firstSelectBtn = userSearchResults.querySelector('.select-user-btn');
                    if (firstSelectBtn) firstSelectBtn.focus();
                    e.preventDefault();
                } else if (e.key === 'Escape') {
                    userSearchResults.style.display = 'none';
                }
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!userSearchInput.contains(e.target) && !userSearchResults.contains(e.target)) {
                    userSearchResults.style.display = 'none';
                }
            });
        }

        // Set up the share button
        if (sharePortfolioBtn) {
            // Replace with new button to avoid duplicate listeners
            const newBtn = sharePortfolioBtn.cloneNode(true);
            if (sharePortfolioBtn.parentNode) {
                sharePortfolioBtn.parentNode.replaceChild(newBtn, sharePortfolioBtn);
                setupShareButton(newBtn, modalEl);
            }
        }

        /**
         * Reset modal state
         */
        function resetModalState() {
            if (userSearchInput) userSearchInput.value = '';
            if (userSearchResults) {
                userSearchResults.innerHTML = '';
                userSearchResults.style.display = 'none';
            }
            selectedUserId = null;
        }

        /**
         * Load users from the server
         * @param {boolean} showDropdown - Whether to show the dropdown after loading
         */
        function loadUsers(showDropdown = true) {
            console.log('Loading users...');
            
            // Only show loading state if we're going to show the dropdown
            if (showDropdown && userSearchResults) {
                userSearchResults.innerHTML = '<div class="text-center p-2">Loading users...</div>';
                userSearchResults.style.display = 'block';
            }
            
            fetch('/portfolios/api/users')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to fetch users');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Loaded users:', data);
                    allUsers = data.users || [];
                    
                    // Check if there are no other users to share with
                    if (allUsers.length === 0) {
                        if (showDropdown && userSearchResults) {
                            userSearchResults.innerHTML = '<div class="text-center p-2 text-info">No other users available to share with</div>';
                            userSearchResults.style.display = 'block';
                        }
                        return;
                    }
                    
                    // Only filter and show users if showDropdown is true
                    if (showDropdown) {
                        filterUsers(''); // Display all users initially
                    }
                })
                .catch(error => {
                    console.error('Error loading users:', error);
                    
                    // Only show error if we're showing the dropdown
                    if (showDropdown && userSearchResults) {
                        userSearchResults.innerHTML = '<div class="text-center p-2 text-danger">Failed to load users</div>';
                        userSearchResults.style.display = 'block';
                    }
                    
                    // If API fails, use sample data for testing
                    console.log('Using sample user data for testing');
                    allUsers = [
                        { id: 1, username: 'user1' },
                        { id: 2, username: 'user2' },
                        { id: 3, username: 'rich2' },
                        { id: 4, username: 'admin' }
                    ];
                    
                    // Only show results if showDropdown is true
                    if (showDropdown) {
                        filterUsers('');
                    }
                });
        }

        /**
         * Filter users based on the search term and update the results
         * @param {string} searchTerm - The term to filter users by
         */
        function filterUsers(searchTerm) {
            console.log('Filtering users with term:', searchTerm);
            
            if (!userSearchResults) {
                console.error('User search results element not found');
                return;
            }
            
            userSearchResults.innerHTML = '';

            // If we don't have users yet and we're trying to filter, load them first
            if (allUsers.length === 0) {
                loadUsers();
                return;
            }

            const filteredUsers = allUsers.filter(user =>
                user.username.toLowerCase().includes(searchTerm)
            );

            console.log(`Found ${filteredUsers.length} users matching "${searchTerm}"`);

            if (filteredUsers.length === 0) {
                userSearchResults.innerHTML = '<div class="user-item no-results">No users found</div>';
                return;
            }

            filteredUsers.forEach(user => {
                const userItem = document.createElement('div');
                userItem.className = 'user-item';
                userItem.dataset.userId = user.id;
                
                // Create HTML structure with username and "Select" text (no button)
                userItem.innerHTML = `
                    <span class="username">${user.username}</span>
                    <span class="select-text">Select</span>
                `;
                
                // Add click event to the entire user item
                userItem.addEventListener('click', function() {
                    selectUser(user.id, user.username);
                });

                userSearchResults.appendChild(userItem);
            });
            
            // Show the results
            userSearchResults.style.display = 'block';
        }

        /**
         * Select a user for sharing
         * @param {number} userId - The ID of the selected user
         * @param {string} username - The username of the selected user
         */
        function selectUser(userId, username) {
            console.log(`Selected user: ${username} (ID: ${userId})`);
            
            if (!userSearchInput || !userSearchResults) {
                console.error('User search elements not found');
                return;
            }
            
            selectedUserId = userId;

            // Update the input field to show the selected user
            userSearchInput.value = username;

            // Clear the search results
            userSearchResults.innerHTML = '';
            userSearchResults.style.display = 'none';
            
            // Enable share button if needed
            if (sharePortfolioBtn && sharePortfolioBtn.disabled) {
                sharePortfolioBtn.disabled = false;
            }
        }

        /**
         * Set up the share button click handler
         * @param {HTMLElement} shareButton - The share button element
         * @param {HTMLElement} modalEl - The modal element
         */
        function setupShareButton(shareButton, modalEl) {
            shareButton.addEventListener('click', function () {
                if (!selectedUserId) {
                    alert('Please select a user to share with.');
                    return;
                }

                const portfolioId = modalEl.dataset.portfolioId;
                if (!portfolioId) {
                    console.error('Portfolio ID not found in modal data');
                    alert('Error: Could not determine which portfolio to share.');
                    return;
                }

                // Disable button during request to prevent multiple clicks
                shareButton.disabled = true;
                shareButton.innerText = 'Sharing...';

                fetch('/portfolios/api/portfolios/share', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify({
                        portfolio_id: portfolioId,
                        user_ids: [selectedUserId]
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        // Get portfolio name - directly from modal dataset first
                        let portfolioName = modalEl.dataset.portfolioName;
                        console.log('Initial portfolio name from dataset:', portfolioName);
                        
                        // If name is not available, try to extract from modal title
                        if (!portfolioName) {
                            const modalTitle = modalEl.querySelector('.modal-title');
                            if (modalTitle) {
                                const titleText = modalTitle.textContent;
                                console.log('Modal title text:', titleText);
                                const matches = titleText.match(/Share Your Portfolio "([^"]+)"/);
                                if (matches && matches[1]) {
                                    portfolioName = matches[1];
                                    console.log('Extracted name from title:', portfolioName);
                                }
                            }
                        }
                        
                        // Final fallback
                        if (!portfolioName) {
                            portfolioName = 'portfolio';
                            console.log('Using fallback portfolio name');
                        }
                        
                        // Now use the determined portfolio name in the alert
                        // Create success alert with portfolio name
                        const alertHTML = `
                            <div class="alert alert-success alert-dismissible fade show" role="alert">
                                Portfolio "${portfolioName}" shared successfully with user ${data.shared_with.join(', ')}
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            </div>
                        `;
                        
                        // Create alert container that appears below navbar and centered
                        let alertContainer = document.getElementById('global-alert-container');
                        if (!alertContainer) {
                            alertContainer = document.createElement('div');
                            alertContainer.id = 'global-alert-container';
                            
                            // Style for centered positioning below navbar
                            alertContainer.style.position = 'fixed';
                            alertContainer.style.top = '80px'; // Position below navbar
                            alertContainer.style.left = '50%';
                            alertContainer.style.transform = 'translateX(-50%)';
                            alertContainer.style.zIndex = '9999';
                            alertContainer.style.width = '80%'; // Use percentage width
                            alertContainer.style.maxWidth = '800px'; // Maximum width
                            
                            document.body.appendChild(alertContainer);
                        }
                        
                        // Add the alert to the container
                        alertContainer.innerHTML = alertHTML;
                        
                        // Auto-close the alert after 5 seconds
                        setTimeout(() => {
                            const alert = alertContainer.querySelector('.alert');
                            if (alert) {
                                // Try to close using Bootstrap API first
                                try {
                                    const bsAlert = new bootstrap.Alert(alert);
                                    bsAlert.close();
                                } catch (e) {
                                    // Fallback: remove directly
                                    alert.remove();
                                }
                            }
                        }, 5000);
                        
                        // Close the modal - try multiple methods
                        try {
                            const bootstrapModal = bootstrap.Modal.getInstance(modalEl);
                            if (bootstrapModal) {
                                bootstrapModal.hide();
                            } else if (typeof $ !== 'undefined') {
                                $(modalEl).modal('hide');
                            } else {
                                modalEl.style.display = 'none';
                                modalEl.classList.remove('show');
                                document.body.classList.remove('modal-open');
                                const backdrop = document.querySelector('.modal-backdrop');
                                if (backdrop) backdrop.remove();
                            }
                        } catch (error) {
                            console.error('Error hiding modal:', error);
                            modalEl.style.display = 'none';
                        }
                    } else {
                        alert(`Failed to share portfolio: ${data.message || 'Unknown error'}`);
                    }
                })
                .catch(error => {
                    console.error('Error sharing portfolio:', error);
                    alert('Failed to share portfolio. Please try again.');
                })
                .finally(() => {
                    // Re-enable button
                    shareButton.disabled = false;
                    shareButton.innerText = 'Share';
                });
            });
        }
    }
});

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
    
    // Set up user search functionality
    const userSearchInput = document.getElementById('userSearch');
    const userSearchResults = document.getElementById('userSearchResults');
    const selectedUsersList = document.querySelector('.selected-user-list');
    const selectedUserHeading = document.querySelector('.selected-user-heading');
    let selectedUserId = null;
    
    // Show user list when input field gets focus
    if (userSearchInput) {
        userSearchInput.addEventListener('focus', function() {
            loadAndShowUserDropdown();
        });
        
        // Filter users when typing
        userSearchInput.addEventListener('input', function() {
            const searchTerm = this.value.trim().toLowerCase();
            filterUsers(searchTerm);
        });
        
        // Handle clicking outside to close dropdown menu
        document.addEventListener('click', function(e) {
            if (!userSearchInput.contains(e.target) && 
                !userSearchResults.contains(e.target)) {
                userSearchResults.style.display = 'none';
            }
        });
    }
    
    // Add click handler for share button
    const newShareBtn = shareBtn.cloneNode(true);
    shareBtn.parentNode.replaceChild(newShareBtn, shareBtn);
    
    newShareBtn.addEventListener('click', function() {
        if (!selectedUserId) {
            alert('Please select a user to share with');
            return;
        }
        
        // Disable button and show loading state
        this.disabled = true;
        const originalText = this.textContent;
        this.textContent = 'Sharing...';
        
        // Send share request
        console.log(`Sharing portfolio ${portfolioId} with user ID: ${selectedUserId}`);
        
        // Add actual sharing API call here
        // Example code, should use fetch to send request to backend
        setTimeout(() => {
            console.log('Share successful!');
            alert('Portfolio shared successfully!');
            
            // Reset state
            this.disabled = false;
            this.textContent = originalText;
            
            // Close modal
            const modalEl = document.getElementById('sharePortfolioModal');
            try {
                const bootstrapModal = bootstrap.Modal.getInstance(modalEl);
                if (bootstrapModal) {
                    bootstrapModal.hide();
                }
            } catch (err) {
                console.error('Error hiding modal:', err);
                modalEl.style.display = 'none';
            }
            
            // Clear selection
            selectedUserId = null;
            userSearchInput.value = '';
            selectedUsersList.innerHTML = '';
            selectedUserHeading.classList.add('d-none');
        }, 1000);
    });
    
    // Load and show user dropdown list
    function loadAndShowUserDropdown() {
        // Show loading state
        userSearchResults.style.display = 'block';
        userSearchResults.innerHTML = '<div class="p-2 text-center">Loading users...</div>';
        
        // Simulate API call to get user list
        // Should call backend API in real application
        setTimeout(() => {
            // Sample user data
            const users = [
                { id: 1, username: 'user1' },
                { id: 2, username: 'user2' },
                { id: 3, username: 'rich3' },
                { id: 4, username: 'lililili' }
            ];
            
            displayUserList(users);
        }, 500);
    }
    
    // Filter users based on search term
    function filterUsers(searchTerm) {
        if (searchTerm === '') {
            loadAndShowUserDropdown();
            return;
        }
        
        // Simulate filtering users by search term
        // Should call backend API for search in real application
        setTimeout(() => {
            const users = [
                { id: 1, username: 'user1' },
                { id: 2, username: 'user2' },
                { id: 3, username: 'rich3' },
                { id: 4, username: 'lililili' }
            ].filter(user => user.username.toLowerCase().includes(searchTerm));
            
            displayUserList(users);
        }, 300);
    }
    
    // Display user list in dropdown
    function displayUserList(users) {
        userSearchResults.innerHTML = '';
        
        if (users.length === 0) {
            userSearchResults.innerHTML = '<div class="p-2 text-center">No users found</div>';
            return;
        }
        
        users.forEach(user => {
            const userItem = document.createElement('div');
            userItem.className = 'user-dropdown-item p-2 border-bottom d-flex justify-content-between align-items-center';
            userItem.innerHTML = `
                <span>${user.username}</span>
                <button class="btn btn-sm btn-outline-primary">Select</button>
            `;
            
            // Click to select user
            userItem.querySelector('button').addEventListener('click', function() {
                selectUser(user.id, user.username);
                userSearchResults.style.display = 'none';
            });
            
            // Clicking entire row can also select user
            userItem.addEventListener('click', function(e) {
                if (e.target !== userItem.querySelector('button')) {
                    selectUser(user.id, user.username);
                    userSearchResults.style.display = 'none';
                }
            });
            
            userSearchResults.appendChild(userItem);
        });
    }
    
    // Select a user
    function selectUser(userId, username) {
        selectedUserId = userId;
        userSearchInput.value = username;
        
        // Show selected user
        selectedUsersList.innerHTML = `
            <div class="selected-user p-2 bg-light rounded d-flex justify-content-between align-items-center">
                <span>@${username}</span>
                <button class="btn btn-sm btn-outline-danger" title="Remove">×</button>
            </div>
        `;
        
        // Show heading
        selectedUserHeading.classList.remove('d-none');
        
        // Add event handler for remove button
        selectedUsersList.querySelector('button').addEventListener('click', function() {
            selectedUserId = null;
            userSearchInput.value = '';
            selectedUsersList.innerHTML = '';
            selectedUserHeading.classList.add('d-none');
        });
    }
}

// Portfolio Comparison Functionality
document.addEventListener('DOMContentLoaded', () => {
    const compareBtn = document.getElementById('compareBtn');
    
    if (compareBtn) {
        compareBtn.addEventListener('click', () => {
            initComparisonModal();
            const modalEl = document.getElementById('comparisonModal');
            const comparisonModal = new bootstrap.Modal(modalEl);
            comparisonModal.show();
        });
    }
});

// Initialize the comparison modal
function initComparisonModal() {
    console.log('Initializing comparison modal');
    
    const modalEl = document.getElementById('comparisonModal');
    if (!modalEl) {
        console.warn('Comparison modal not found in the DOM, skipping initialization');
        return;
    }
    
    const portfolioListEl = document.getElementById('portfolioListForComparison');
    const compareBtn = document.getElementById('comparePortfoliosBtn');
    
    // Clear previous content
    portfolioListEl.innerHTML = '';
    
    // Initialize slots and compare button
    const portfolioSlotA = document.getElementById('portfolioSlotA');
    const portfolioSlotB = document.getElementById('portfolioSlotB');
    
    let selectedPortfolios = {
        a: null,
        b: null
    };
    
    // Update the status of the compare button
    function updateCompareButton() {
        compareBtn.disabled = !(selectedPortfolios.a && selectedPortfolios.b);
    }
    
    // Remove portfolio from slot
    function removePortfolio(slot) {
        const slotEl = document.getElementById(`portfolioSlot${slot.toUpperCase()}`);
        if (slotEl) {
            const emptySlot = slotEl.querySelector('.empty-slot');
            const selectedSlot = slotEl.querySelector('.selected-portfolio');
            const removedId = selectedPortfolios[slot.toLowerCase()];
            
            // Reset slot state
            emptySlot.classList.remove('d-none');
            selectedSlot.classList.add('d-none');
            selectedPortfolios[slot.toLowerCase()] = null;
            
            // Update the status of the compare button
            updateCompareButton();
            
            // Re-enable the item in the list
            const listItem = portfolioListEl.querySelector(`[data-portfolio-id="${removedId}"]`);
            if (listItem) {
                listItem.classList.remove('disabled');
                listItem.style.pointerEvents = '';
                listItem.style.opacity = '';
            }
        }
    }
    
    // Select portfolio to specified slot
    function selectPortfolio(portfolioId, portfolioName, slot) {
        const slotEl = document.getElementById(`portfolioSlot${slot.toUpperCase()}`);
        if (slotEl) {
            const emptySlot = slotEl.querySelector('.empty-slot');
            const selectedSlot = slotEl.querySelector('.selected-portfolio');
            const nameSpan = selectedSlot.querySelector('.portfolio-name');
            
            nameSpan.textContent = portfolioName;
            selectedPortfolios[slot.toLowerCase()] = portfolioId;
            
            emptySlot.classList.add('d-none');
            selectedSlot.classList.remove('d-none');
            
            updateCompareButton();
        }
    }
    
    // Load portfolio list
    function loadPortfolios() {
        // Clear existing list
        portfolioListEl.innerHTML = '';
        
        // Get all portfolio data from table
        const portfolios = [];
        const tableRows = document.querySelectorAll('.portfolios-table tbody tr:not(.no-data-row)');
        
        tableRows.forEach(row => {
            // Try to get ID from multiple possible attributes
            const portfolioId = row.dataset.portfolioId || row.dataset.id || 
                                row.getAttribute('data-portfolio-id') || 
                                row.getAttribute('data-id');
            
            if (!portfolioId) return;
            
            const portfolioNameEl = row.querySelector('.portfolio-name-cell a');
            const portfolioName = portfolioNameEl ? portfolioNameEl.textContent.trim() : 'Unknown Portfolio';
            
            portfolios.push({
                id: portfolioId,
                name: portfolioName
            });
        });
        
        // If it's card view, try to get data from cards
        if (portfolios.length === 0) {
            const cards = document.querySelectorAll('.portfolio-card');
            cards.forEach(card => {
                // Try to get ID from multiple possible attributes
                const portfolioId = card.dataset.portfolioId || card.dataset.id || 
                                   card.getAttribute('data-portfolio-id') || 
                                   card.getAttribute('data-id');
                
                if (!portfolioId) return;
                
                const portfolioNameEl = card.querySelector('.portfolio-title-link');
                const portfolioName = portfolioNameEl ? portfolioNameEl.textContent.trim() : 'Unknown Portfolio';
                
                portfolios.push({
                    id: portfolioId,
                    name: portfolioName
                });
            });
        }
        
        // Check if any portfolios were found
        if (portfolios.length === 0) {
            portfolioListEl.innerHTML = '<div class="list-group-item text-center">No portfolios found</div>';
            return;
        }
        
        // Create portfolio list in modal
        portfolios.forEach(portfolio => {
            const item = document.createElement('a');
            item.href = '#';
            item.className = 'list-group-item list-group-item-action';
            item.setAttribute('data-portfolio-id', portfolio.id);
            item.textContent = portfolio.name;
            
            // Check if it's already selected, if so, disable it
            if (selectedPortfolios.a === portfolio.id || selectedPortfolios.b === portfolio.id) {
                item.classList.add('disabled');
                item.style.pointerEvents = 'none';
                item.style.opacity = '0.6';
            }
            
            item.addEventListener('click', function(e) {
                e.preventDefault();
                
                // If item is disabled, do nothing
                if (this.classList.contains('disabled')) {
                    return;
                }
                
                // Determine which slot to use
                let targetSlot;
                if (!selectedPortfolios.a) {
                    targetSlot = 'a';
                } else if (!selectedPortfolios.b) {
                    targetSlot = 'b';
                } else {
                    // If both slots are full, need to remove one first
                    alert('Please remove one of the selected portfolios before adding a new one');
                    return;
                }
                
                // Select portfolio and update UI
                selectPortfolio(portfolio.id, portfolio.name, targetSlot);
                
                // Disable already selected item
                this.classList.add('disabled');
                this.style.pointerEvents = 'none';
                this.style.opacity = '0.6';
            });
            
            portfolioListEl.appendChild(item);
        });
    }
    
    // Load portfolios
    loadPortfolios();
    
    // Add event listener to Remove buttons
    document.querySelectorAll('.remove-portfolio').forEach(button => {
        button.addEventListener('click', function() {
            const slotEl = this.closest('.portfolio-slot');
            const slot = slotEl.id.replace('portfolioSlot', '').toLowerCase();
            removePortfolio(slot);
        });
    });
    
    // Click event for compare button
    compareBtn.addEventListener('click', function() {
        if (selectedPortfolios.a && selectedPortfolios.b) {
            window.location.href = `/comparison/?a=${selectedPortfolios.a}&b=${selectedPortfolios.b}`;
        }
    });
}
