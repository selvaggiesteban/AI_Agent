---
title: "Free Claude Code"
description: "You need to download Ollama and register, then, when you're on your Windows computer running a web programming and development session in VS Code,"
pubDate: 2026-02-17
heroImage: "/assets/blog/covers/free-claude-code.svg"
---



                


<h2>Connect Claude Code to open-source AI models</h2>



<figure><img width="1024" height="576" src="/assets/blog/claude-code-gratis-1.webp" alt=""></figure>



<p>You need to download <a href="https://ollama.com/" target="_blank" rel="noopener">Ollama</a> and register, then, when you're on your <a href="https://lanuscomputacion.com/" target="_blank" rel="noreferrer noopener">Windows computer</a> running a <a href="https://selvaggiesteban.dev/" target="_blank" rel="noreferrer noopener">web programming and development</a> session in VS Code, run:</p>



<pre><code><strong>wsl</strong>
<strong>export ANTHROPIC_AUTH_TOKEN=ollama</strong>
<strong>export ANTHROPIC_API_KEY=""</strong>
<strong>export ANTHROPIC_BASE_URL=http://127.0.0.1:11434</strong>
<strong>claude -c --dangerously-skip-permissions --model kimi-k2.5:cloud</strong></code></pre>



<p>You should see: Skill(superpowers:subagent-driven-development)</p>



<figure><img width="1024" height="223" src="/assets/blog/claude-code-gratis-2.png" alt=""></figure>



<p>On the day this article is published, Ollama offers a limited free plan with concurrency restrictions and multiple <a href="https://ollama.com/search" target="_blank" rel="noopener">available models</a>.</p>



<p>Daily context usage limits for programming and development web sessions reset every 6 hours. Additionally, there is a weekly usage limit.</p>



<p>You might be interested in: <a href="https://selvaggiesteban.dev/kimi-k2-5-en-la-nube-la-proxima-frontera-de-la-ia-empresarial/">kimi-k2.5</a> and minimax-m2.1 from Moonshot AI, also Qwen3:4b for <a href="https://lanuscomputacion.com" target="_blank" rel="noopener">computers with 8 GB of RAM</a>.</p>



<p>It's essential to use the ralph-loop plugin and run /ralph-loop:ralph-loop to complete all pending tasks –max-iterations 5 –completion-promise 'I confirm there are no pending tasks to complete'.</p>
                                    
                        
                                                 
                    
                    
                    