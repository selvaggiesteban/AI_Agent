---
title: "MercadoLibre and WooCommerce: How to Sync Shipments, Prices, and Stock Without Losing Sales"
description: "Complete guide to selling on MercadoLibre and your WooCommerce website with identical prices, integrated logistics, and no friction between channels. The solution to the shipping problem every multi-channel seller faces."
pubDate: "2026-06-14"
heroImage: "/assets/blog/covers/mercadolibre-and-woocommerce-how-to-sync-shipments-prices-and-stock-without-losing-sales.svg"
tags: ["WooCommerce", "MercadoLibre", "E-Commerce", "Logistics", "Shipping", "Integration", "Argentina"]
category: "E-Commerce"
---

## The dilemma of every seller who uses MercadoLibre and their own website

If you have a store on MercadoLibre and also sell through your own WooCommerce website, you already know the problem: **Mercado Envíos gives you labels, tracking, and integrated logistics with carriers**, but your website doesn't have that. WooCommerce's native shipping solutions fall short, and to make the website attractive despite not offering the same logistics, you end up inflating prices and applying artificial discounts.

This creates three serious problems:

<ol>
  <li><strong>Price inconsistency</strong> — the same product costs differently on ML than on your website.</li>
  <li><strong>Customer confusion</strong> — they don't understand why there are discounts on one channel but not the other.</li>
  <li><strong>Diluted commercial strategy</strong> — the discounts eat into your margin and create dependency on the channel with better logistics.</li>
</ol>

Every seller in this situation has a logical idea: **register the WooCommerce order in MercadoLibre as if it had been sold there**, to use Mercado Envíos as well. Identical prices on both sides, same logistics, no friction.

But there's a technical problem that makes this approach impossible.

## Why you can't "inject" WooCommerce orders into MercadoLibre

MercadoLibre's API has a design limitation that many people discover too late:

<blockquote>
  <strong>The MercadoLibre API only allows reading existing orders (via GET /orders), not creating them.</strong> There is no endpoint for creating orders from outside or for generating standalone shipments.</blockquote>

When someone buys on WooCommerce, <strong>there's no way to "register" that sale on ML as if it had occurred there</strong>. The shipment_id — which you need to generate Mercado Envíos labels — is only created when a buyer completes the purchase within MercadoLibre's checkout. Without that ID, the label cannot be generated.

This means that:

<ul>
  <li>Orders originating on ML <strong>can be imported</strong> into WooCommerce for centralized management.</li>
  <li>WooCommerce orders <strong>cannot be exported</strong> to ML.</li>
  <li>Order synchronization is <strong>one-directional</strong>: from ML to WooCommerce, never the other way around.</li>
</ul>

It's a design limitation of the API: orders and shipments are inseparable from MercadoLibre's internal checkout. The logistics part cannot be separated from the transactional part.

## The real solution: sync catalog + integrate external logistics

If you can't use Mercado Envíos for your website orders, the solution isn't to force the ML API. It's <strong>two things in parallel</strong>:

### 1. Sync products, stock, and prices (ML as the source of truth)

Your MercadoLibre catalog should be the source of truth. A synchronization plugin must:

<ul>
  <li><strong>Import products from ML to WooCommerce</strong> — descriptions, images, variants, prices.</li>
  <li><strong>Sync stock in real time</strong> — if something sells on ML, it deducts in WooCommerce, and vice versa.</li>
  <li><strong>Maintain identical prices</strong> — no artificial discounts or inconsistencies between channels.</li>
  <li><strong>Sync ML orders into WooCommerce</strong> — for centralized fulfillment management.</li>
</ul>

This eliminates the unequal pricing problem. The customer sees the same price on both channels, and you manage everything from a single place.

### 2. Integrate an external logistics API for website orders

For shipments originating in WooCommerce, you need a logistics solution that gives you what Mercado Envíos gives you on ML:

<ul>
  <li><strong>Shipping labels</strong> — to print and attach to packages.</li>
  <li><strong>Tracking</strong> — tracking numbers so customers can follow their purchase.</li>
  <li><strong>Carrier integration</strong> — OCA, Correo Argentino, Andreani, or any carrier you use.</li>
  <li><strong>Shipping cost calculation</strong> — in real time, based on destination and weight.</li>
</ul>

In Argentina, the most common options for this are:

<ul>
  <li><strong>OCA</strong> — with plugins like OCA Libre or API integration.</li>
  <li><strong>Correo Argentino</strong> — with its public API or plugins like Envíos Correo Argentino.</li>
  <li><strong>Andreani</strong> — for higher volume shipments.</li>
  <li><strong>Multi-carrier</strong> — plugins that manage multiple carriers from a single dashboard.</li>
</ul>

## How the final architecture looks

The solution for a seller like Juan looks like this:

```
┌─────────────────────────────────────────────────────────┐
│                    MERCADOLIBRE                          │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────────┐ │
│  │ Sales    │  │ Stock    │  │ Mercado Envíos        │ │
│  │ (source) │  │ (sync)   │  │ (labels + tracking)   │ │
│  └────┬─────┘  └────┬─────┘  └───────────────────────┘ │
│       │              │                                   │
└───────┼──────────────┼───────────────────────────────────┘
        │              │
   ┌────▼──────────────▼────┐
   │   SYNC PLUGIN          │
   │   (ML ↔ WooCommerce)   │
   └────┬──────────────┬────┘
        │              │
┌───────┼──────────────┼───────────────────────────────────┐
│       │              │                                   │
│  ┌────▼─────┐  ┌─────▼────┐  ┌───────────────────────┐ │
│  │ Products │  │ Stock    │  │ External Logistics    │ │
│  │ (catalog)│  │ (unified)│  │ (OCA / CA / Andreani) │ │
│  └──────────┘  └──────────┘  └───────────────────────┘ │
│                    WOOCOMMERCE                           │
└─────────────────────────────────────────────────────────┘
```

The catalog and stock are synchronized. Prices are identical. Each channel manages its shipments with its own logistics solution. And you centralize everything in WooCommerce.

## Concrete benefits of this approach

<ul>
  <li><strong>Consistent pricing</strong> — the customer pays the same on ML and your website. No confusion, no artificial discounts.</li>
  <li><strong>Equivalent logistics</strong> — both channels have labels and tracking. The website isn't at a disadvantage.</li>
  <li><strong>Centralized management</strong> — all orders, from any channel, are managed from WooCommerce.</li>
  <li><strong>Unified stock</strong> — you don't oversell on one channel due to lack of synchronization.</li>
  <li><strong>Protected margin</strong> — you don't need to inflate prices to compensate for the lack of logistics on the website.</li>
  <li><strong>SEO for your website</strong> — with competitive prices, your website can rank on Google and attract organic traffic.</li>
</ul>

## Common mistakes when trying to solve this

<ol>
  <li><strong>Using one-directional sync plugins</strong> — if you only import from ML to WooCommerce, you still don't have logistics on the website. You need bidirectional sync for stock and prices, and separate logistics for shipments.</li>
  <li><strong>Creating "phantom orders" on ML</strong> — trying to simulate purchases to generate shipment_id. This violates ML's terms of service and can result in account suspension.</li>
  <li><strong>Ignoring stock synchronization</strong> — if a product sells on ML and doesn't deduct from the website, you'll oversell. Stock synchronization is critical.</li>
  <li><strong>Not accounting for ML commissions</strong> — ML charges a commission per sale. Your website price should be the same, but your real margin differs on each channel. Calculate it carefully.</li>
</ol>

## Frequently asked questions

### Can WooCommerce orders be synced to MercadoLibre?

Not directly. The ML API doesn't allow creating external orders. What you can do is import ML orders into WooCommerce for centralized management, and use external logistics for website orders.

### What plugins work for syncing ML with WooCommerce?

Some popular options are MercadoLibre for WooCommerce (by various developers), and custom solutions via ML's official API. The important thing is that they support bidirectional stock and price synchronization.

### How much does it cost to integrate external logistics in WooCommerce?

It depends on the carrier. OCA and Correo Argentino have free plugins with shipping plans. API integration can cost between USD 50 and 200 depending on complexity.

### Is it better to sell only on ML or also have your own website?

Ideally both. ML gives you traffic and trust. Your website gives you margin and control. The key is that the experience is consistent across both channels.

### Can I use Mercado Envíos for my website shipments?

No. Mercado Envíos only works for orders that originate within MercadoLibre's checkout. It's a design limitation of the API.

## Conclusion

The problem of inconsistent pricing and unequal logistics between MercadoLibre and WooCommerce has no magic solution or API shortcuts. The ML API doesn't allow creating external orders, and that's not going to change.

But it can be solved with the right architecture: **sync catalog and stock (ML as source of truth) + integrate external logistics for the website**. This way you maintain identical prices, manage everything from a single place, and each channel has the logistics it needs.

If you're facing this problem, the first thing to understand is that you don't have to choose between ML and your website. You can have both, working in synergy, with the right tool for each part of the process.