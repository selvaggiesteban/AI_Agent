---
title: "Wholesale Pricing Guide"
description: "The idea would look like this:"
pubDate: 2025-12-11
heroImage: "/assets/blog/covers/wholesale-pricing-guide.svg"
---




<p>The idea would look like this:</p>



<blockquote class="is-layout-flow">
<p>The entire store is visible to anyone (guests + regular WooCommerce customers)<br><strong>EXCEPT</strong> the <code>Wholesale</code> category, which only the special role you create with Ultimate Member can see.</p>
</blockquote>



<p>I'll explain how to set it up step by step.</p>



<h2>1. Create a "wholesale" role in Ultimate Member</h2>



<ol>
<li>In your admin:<br><strong>Ultimate Member → User Roles → Add New</strong>.</li>



<li>Give it a name like:
<ul>
<li><em>Role Title</em>: <code>Wholesale</code></li>



<li><em>Role ID</em>: <code>wholesale</code> (or something similar).</li>
</ul>
</li>



<li>Check the basic capabilities (it can inherit from "Subscriber" or "Customer", depending on your configuration).</li>



<li>Save.</li>
</ol>



<p>With this, you now have a role that you'll only use for people who register through the Ultimate Member form.</p>



<blockquote class="is-layout-flow">
<p>Later on, if you want, you can use the UM–WooCommerce extension to automatically assign roles when they make a purchase, but for your case it's not required. <a href="https://docs.ultimatemember.com/article/1590-how-to-use-user-roles?utm_source=chatgpt.com" target="_blank" rel="noreferrer noopener">docs.ultimatemember.com+1</a></p>
</blockquote>



<h2>2. Make your Ultimate Member form assign that role</h2>



<ol>
<li>Go to <strong>Ultimate Member → Forms</strong>.</li>



<li>Edit the registration form you use for your "wholesale list".</li>



<li>In the form options, look for something like <strong>"Assign role to form" / "Default role"</strong> and select the <code>Wholesale</code> role you created.</li>



<li>Save the form.</li>
</ol>



<p>Result:</p>



<ul>
<li>Users who register via <strong>WooCommerce checkout</strong> → will keep the normal <code>customer</code> role.</li>



<li>Users who register via <strong>UM form</strong> → receive the <code>wholesale</code> role (the "special" ones who will see the Wholesale category).</li>
</ul>



<h2>3. Enable content restriction for products and categories</h2>



<p>Ultimate Member allows you to apply restrictions by <strong>post type</strong> and by <strong>taxonomy (categories, tags, etc.)</strong>.<a href="https://docs.ultimatemember.com/article/1623-post-term-restriction-content-settings" target="_blank" rel="noreferrer noopener">docs.ultimatemember.com+1</a></p>



<ol>
<li>Go to <strong>Ultimate Member → Settings → Access → Content Restriction</strong>.</li>



<li>In the section <strong>"Enable the Content Restriction settings for post types"</strong>, check the <code>product</code> post type. <a href="https://docs.ultimatemember.com/article/1623-post-term-restriction-content-settings" target="_blank" rel="noreferrer noopener">docs.ultimatemember.com</a></li>



<li>Further down, in <strong>"Enable the Content Restriction settings for taxonomies"</strong>, check the <code>product_cat</code> taxonomy (product categories). <a href="https://docs.ultimatemember.com/article/1623-post-term-restriction-content-settings" target="_blank" rel="noreferrer noopener">docs.ultimatemember.com</a></li>



<li>Save changes.</li>
</ol>



<p>This makes it so that in:</p>



<ul>
<li>each <strong>product</strong>, and</li>



<li>each <strong>product category</strong></li>
</ul>



<p>an "Ultimate Member: Content Restriction" box appears to define who can see it. <a href="https://docs.ultimatemember.com/article/1623-post-term-restriction-content-settings" target="_blank" rel="noreferrer noopener">docs.ultimatemember.com+1</a></p>



<h2>4. Restrict only the "wholesale" category</h2>



<p>Now comes the key part:</p>



<ol>
<li>Go to <strong>Products → Categories</strong>.</li>



<li>Edit the <code>Wholesale</code> category.</li>



<li>Below the category description you should see the block:<br><strong>"Ultimate Member: Content Restriction"</strong>.</li>



<li>Enable <strong>"Restrict access to this term and its posts?"</strong> (or similar text). <a href="https://docs.ultimatemember.com/article/1623-post-term-restriction-content-settings" target="_blank" rel="noreferrer noopener">docs.ultimatemember.com</a></li>



<li>In <strong>"Who can access this term and its posts?"</strong> select:
<ul>
<li><strong>Logged in users</strong> → and the option <strong>"Select which roles can access this term and its posts"</strong> will open.</li>



<li>Select <strong>only</strong> the <code>wholesale</code> role. <a href="https://docs.ultimatemember.com/article/1623-post-term-restriction-content-settings" target="_blank" rel="noreferrer noopener">docs.ultimatemember.com</a></li>
</ul>
</li>



<li>Highly recommended: enable the option<br><strong>"Display 404 page for users who do not have access to this term on the term's archive page and terms' posts single pages"</strong>.
<ul>
<li>With this, <strong>the Wholesale category and all products under it are securely hidden</strong> — they don't appear in listings and can't be viewed if someone tries to access them directly via URL. <a href="https://docs.ultimatemember.com/article/1623-post-term-restriction-content-settings" target="_blank" rel="noreferrer noopener">docs.ultimatemember.com</a></li>
</ul>
</li>



<li>Save the category.</li>
</ol>



<h2>5. What each user type will see</h2>



<ul>
<li><strong>Visitor (not logged in)</strong>
<ul>
<li>Sees all categories and products <strong>except</strong> <code>Wholesale</code>.</li>
</ul>
</li>



<li><strong>Regular WooCommerce customer (role <code>customer</code>, created at purchase)</strong>
<ul>
<li>Same as a visitor: sees everything except <code>Wholesale</code>.</li>
</ul>
</li>



<li><strong>Ultimate Member list user (role <code>wholesale</code>)</strong>
<ul>
<li>Sees <strong>all categories</strong>, including <code>Wholesale</code>, and can access products in that category.</li>
</ul>
</li>
</ul>



<p>This fulfills exactly what you wanted:</p>



<blockquote class="is-layout-flow">
<p>"Wholesale" category only visible to users with the Ultimate Member role, and hidden from the public and standard customers.</p>
</blockquote>



<h2>6. Useful things to test that everything works</h2>



<ol>
<li><strong>Create 3 test users</strong>:
<ul>
<li>One without an account (use incognito mode).</li>



<li>One who creates an account by purchasing something normally in WooCommerce (role <code>customer</code>).</li>



<li>One who registers via the UM form (role <code>wholesale</code>).</li>
</ul>
</li>



<li>Verify:
<ul>
<li>In incognito mode → <code>Wholesale</code> does not appear.</li>



<li>Logged in as <code>customer</code> → <code>Wholesale</code> also does not appear.</li>



<li>Logged in as <code>wholesale</code> → <code>Wholesale</code> does appear + products inside.</li>
</ul>
</li>
</ol>



<p>If you want, in the next message I can write you a <strong>short checklist</strong> in "technical manual" format like:</p>



<ul>
<li>Exact path of each screen in the admin panel.</li>



<li>Phrases that should appear (so you can compare).</li>



<li>How to force a 404 vs. a "restricted access" message on those pages.</li>