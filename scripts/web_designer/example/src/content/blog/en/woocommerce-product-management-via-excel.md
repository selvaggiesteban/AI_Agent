---
title: "WooCommerce Product Management via Excel"
description: "Goal: this guide explains how to export WooCommerce products to a CSV file, bulk edit them in Excel or Google Sheets, and import them back to update the catalog."
pubDate: 2025-12-05
heroImage: "/assets/blog/covers/woocommerce-product-management-via-excel.svg"
---




<p><strong>Goal:</strong> this guide explains how to export WooCommerce products to a CSV file, bulk edit them in Excel or Google Sheets, and import them back to update the catalog.</p>



<h2>1. General workflow</h2>



<ol>
<li>Export WooCommerce products to a CSV file.</li>



<li>Open and edit the CSV in Excel or Google Sheets.</li>



<li>Save the edited file as CSV again.</li>



<li>Import the updated CSV into WooCommerce.</li>



<li>Verify that changes have been applied correctly.</li>
</ol>



<p>{{IMG: WordPress admin menu showing All Products option}}</p>



<h2>2. Export products from WooCommerce</h2>



<h3>2.1 Access the product listing</h3>



<ol>
<li>In the WordPress dashboard, go to <strong>Products > All Products</strong>.</li>



<li>Verify that the full product listing is displayed.</li>
</ol>



<h3>2.2 Use the export tool</h3>



<ol>
<li>At the top of the page, click the <strong>Export</strong> button.</li>



<li>On the export screen, choose whether you want to export all products or just a specific type.</li>



<li>Leave all columns selected if you want to be able to edit any data later.</li>



<li>Click <strong>Generate CSV</strong>.</li>
</ol>



<p>{{IMG: WooCommerce product export screenshot}}</p>



<p>The browser will download a file with the <code>.csv</code> extension containing the current catalog.</p>



<h2>3. Edit the CSV in Microsoft Excel</h2>



<h3>3.1 Open the CSV file</h3>



<ol>
<li>Open <strong>Microsoft Excel</strong>.</li>



<li>Go to <strong>File > Open</strong> and select the downloaded CSV file.</li>



<li>Verify that each piece of data appears in its own column.</li>
</ol>



<p>{{IMG: CSV file opened in Excel screenshot}}</p>



<h3>3.2 Most important columns</h3>



<ul>
<li><strong>ID</strong>: internal product identifier.</li>



<li><strong>name</strong>: product name.</li>



<li><strong>regular_price</strong>: regular price.</li>



<li><strong>sale_price</strong>: sale price (if applicable).</li>



<li><strong>sku</strong>: product code.</li>



<li><strong>stock_quantity</strong>: stock quantity.</li>



<li><strong>categories</strong>: assigned categories.</li>



<li><strong>images</strong>: associated images.</li>
</ul>



<h3>3.3 Modify catalog data</h3>



<p>In Excel you can:</p>



<ul>
<li>Update prices in the <code>regular_price</code> column.</li>



<li>Review or change sale prices in <code>sale_price</code>.</li>



<li>Adjust stock in <code>stock_quantity</code>.</li>



<li>Correct names in the <code>name</code> column.</li>



<li>Add new rows to create additional products.</li>
</ul>



<p><strong>Important:</strong> don't change column names or delete columns unless you know exactly what you're doing.</p>



<h3>3.4 Save the file as CSV</h3>



<ol>
<li>When you finish editing, go to <strong>File > Save As</strong>.</li>



<li>Choose a folder to save the file.</li>



<li>Select the file type <strong>CSV (Comma delimited)</strong>.</li>



<li>Accept Excel's compatibility warnings.</li>
</ol>



<p>{{IMG: Save as CSV in Excel screenshot}}</p>



<h2>4. Edit the CSV in Google Sheets</h2>



<h3>4.1 Import the file to Google Sheets</h3>



<ol>
<li>Open <strong>Google Drive</strong> and create a new spreadsheet in Google Sheets.</li>



<li>Go to <strong>File > Import</strong> and upload the CSV file.</li>



<li>Choose whether you want to replace the current sheet or create a new tab.</li>
</ol>



<p>{{IMG: Import CSV in Google Sheets screenshot}}</p>



<h3>4.2 Edit data in Google Sheets</h3>



<p>The logic is the same as in Excel: modify prices, stock, names, and other fields, always respecting the column headers.</p>



<h3>4.3 Download the updated CSV</h3>



<ol>
<li>When you're done, go to <strong>File > Download</strong>.</li>



<li>Choose the <strong>Comma-separated values (.csv)</strong> option.</li>



<li>A new CSV file with your changes will be downloaded.</li>
</ol>



<p>{{IMG: Download CSV from Google Sheets screenshot}}</p>



<h2>5. Import the updated CSV into WooCommerce</h2>



<h3>5.1 Access the import tool</h3>



<ol>
<li>In the WordPress dashboard, go to <strong>Products > All Products</strong>.</li>



<li>At the top of the page, click <strong>Import</strong>.</li>
</ol>



<p>{{IMG: WooCommerce product import screenshot}}</p>



<h3>5.2 Select the file and update options</h3>



<ol>
<li>Click <strong>Choose File</strong> and select the edited CSV.</li>



<li>Check the <strong>Update existing products</strong> checkbox if you want existing products to be updated.</li>



<li>Click <strong>Continue</strong>.</li>
</ol>



<h3>5.3 Review the column mapping</h3>



<p>WooCommerce will show a screen where each CSV column is mapped to a product field. Verify that:</p>



<ul>
<li><code>name</code> is mapped to <strong>Product Name</strong>.</li>



<li><code>regular_price</code> to <strong>Regular Price</strong>.</li>



<li><code>sale_price</code> to <strong>Sale Price</strong>.</li>



<li><code>sku</code> to <strong>SKU</strong>.</li>



<li><code>stock_quantity</code> to <strong>Stock Quantity</strong>.</li>



<li><code>categories</code> to <strong>Categories</strong>.</li>



<li><code>images</code> to <strong>Product Images</strong>.</li>
</ul>



<h3>5.4 Run the importer</h3>



<ol>
<li>When you're satisfied with the mapping, click <strong>Run the importer</strong>.</li>



<li>Wait for the process to finish. WooCommerce will show how many products were created or updated.</li>
</ol>



<h2>6. Verify changes in the catalog</h2>



<ol>
<li>Go back to <strong>Products > All Products</strong>.</li>



<li>Check a few random products to verify prices, stock, and categories.</li>



<li>Open the store on the public side of the website to validate that everything looks correct.</li>
</ol>



<p>{{IMG: WordPress admin menu showing All Products option}}</p>



<h2>7. Recommendations and best practices</h2>



<ul>
<li>Before making bulk changes, download an original CSV and save it as a backup.</li>



<li>Avoid deleting columns; if you don't need a column, simply don't edit it.</li>



<li>Use filters in Excel or Google Sheets to review product series (by category, price range, etc.).</li>



<li>Make bulk changes during low-activity hours to minimize risks.</li>