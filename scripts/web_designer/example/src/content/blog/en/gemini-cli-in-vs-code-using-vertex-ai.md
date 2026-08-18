---
title: "Gemini CLI in VS Code Using Vertex AI"
description: "Working with artificial intelligence inside the editor can greatly accelerate project analysis, code review, and technical planning."
pubDate: 2026-04-16
heroImage: "/assets/blog/covers/gemini-cli-in-vs-code-using-vertex-ai.svg"
---



                


<p>Working with artificial intelligence inside the editor can greatly accelerate project analysis, code review, and technical planning. However, when you start integrating tools like <strong>Gemini CLI in Visual Studio Code</strong>, things don't always work on the first try.</p>



<p>In my case, the goal was clear: use <strong>Gemini CLI in VS Code</strong> connected to <strong>Vertex AI</strong> within <strong>Google Cloud</strong>, instead of relying on a traditional API key. The idea was to leverage a more robust, more professional environment better aligned with a real development workflow.</p>



<p>The problem appeared when, even with part of the advanced configuration in place, Gemini CLI kept failing with authentication errors.</p>



<h2>The problem: Gemini CLI wasn't responding as expected</h2>



<p>When running Gemini CLI inside Visual Studio Code, the behavior was inconsistent. At times it seemed to start correctly, but when sending instructions it returned authentication errors. In other cases, the system kept asking for an API key, even when the goal was to use <strong>Vertex AI with Google Cloud</strong>.</p>



<p>That was the point that caused the most confusion.</p>



<p>At first glance, it seemed like everything was correctly configured. The terminal opened, Gemini CLI started, and part of the authentication appeared to be resolved. But when trying to work with the real project, credential-related errors kept appearing.</p>



<h2>What was really happening</h2>



<p>The root of the problem was a mix of previous configuration and inherited environment variables.</p>



<p>Although the intention was to use <strong>Vertex AI</strong>, the environment still retained traces of previous authentication via:</p>



<ul>
<li><code>GEMINI_API_KEY</code></li>



<li><code>GOOGLE_API_KEY</code></li>
</ul>



<p>As long as those variables remained present, Gemini CLI's behavior could conflict with the use of <strong>Google Cloud Application Default Credentials</strong>.</p>



<p>In other words, the editor and terminal were trying to work with two different authentication paths at the same time.</p>



<p>And that ended up breaking the execution.</p>



<h2>The solution: Clean the environment and force Vertex AI</h2>



<p>The solution was to completely clean the previous keys, leave those variables empty, explicitly define that I wanted to use Vertex AI, and set the correct project and location within the VS Code environment.</p>



<p>After that, the fundamental step was to authenticate with:</p>



<pre>gcloud auth application-default login</pre>



<p>That command was the turning point, because it allowed authentication to rely on Google Cloud's <strong>Application Default Credentials</strong>, which was exactly the right path for working with Vertex AI from the local environment.</p>



<h2>The commands I used in VS Code</h2>



<p>These are the commands I used in the Visual Studio Code terminal to resolve the problem:</p>



<pre><code>Remove-Item Env:\GEMINI_API_KEY -ErrorAction Ignore
Remove-Item Env:\GOOGLE_API_KEY -ErrorAction Ignore

$env:GEMINI_API_KEY=""
$env:GOOGLE_API_KEY=""

$env:GOOGLE_GENAI_USE_VERTEXAI="true"
$env:GOOGLE_CLOUD_PROJECT="project-66dd8011-b5ae-4e29-9e6"
$env:GOOGLE_CLOUD_LOCATION="global"

gcloud auth application-default login

gcloud auth application-default login</code></pre>



<h2>What each command does</h2>



<p>For those who want to understand the logic behind the solution, here's the role of each block.</p>



<h3>1. Remove old keys from the environment</h3>



<pre><code>Remove-Item Env:\GEMINI_API_KEY -ErrorAction Ignore<br>Remove-Item Env:\GOOGLE_API_KEY -ErrorAction Ignore</code></pre>



<p>This removed any active variables that were still forcing key-based authentication.</p>



<h3>2. Explicitly empty the API keys</h3>



<pre><code>$env:GEMINI_API_KEY=""<br>$env:GOOGLE_API_KEY=""</code></pre>



<p>This helped prevent the environment from continuing to inherit previous values in the current session.</p>



<h3>3. Force the use of Vertex AI</h3>



<pre><code>$env:GOOGLE_GENAI_USE_VERTEXAI="true"</code></pre>



<p>This line was key to explicitly indicate that Gemini should work with Vertex AI.</p>



<h3>4. Define project and location</h3>



<pre><code>$env:GOOGLE_CLOUD_PROJECT="project-09b11e05-e833-4306-ba7"
$env:GOOGLE_CLOUD_LOCATION="global"</code></pre>



<p>Here I set the correct project and a global location, which is especially useful when working with certain models and configurations within Vertex AI.</p>



<h3>5. Authentication with default credentials</h3>



<pre>gcloud auth application-default login</pre>



<p>This step allowed the local environment to authenticate correctly against Google Cloud using the proper credentials for working with Vertex AI.</p>



<h2>The result after applying the solution</h2>



<p>Once the environment was sorted out and properly authenticated with Google Cloud, Gemini CLI started behaving much more consistently within Visual Studio Code.</p>



<p>From that point on, the experience changed completely.</p>



<p>It was no longer about fighting credential errors or crossed authentication paths, but about using Gemini CLI the way I actually wanted to: inside the project, from the editor's terminal, with a much more professional workflow for technical analysis, structure review, and contextual assistance.</p>



<h2>What I learned from this experience</h2>



<p>The main takeaway was this: when an AI integration fails, the problem is often not just one thing.</p>



<p>It can be a combination of factors:</p>



<ul>
<li>old variables loaded in the environment,</li>



<li>a mix of API key and Vertex AI,</li>



<li>a VS Code terminal with inherited configuration,</li>



<li>or incomplete local authentication.</li>
</ul>



<p>That's why, before assuming the tool "doesn't work," it's worth patiently reviewing the environment and cleaning up everything that might be interfering.</p>



<p>In my case, the solution didn't require reinstalling everything from scratch, but rather understanding which authentication method I actually wanted to use and aligning the environment with that decision.</p>



<h2>My conclusion on Gemini CLI in VS Code</h2>



<p>After resolving it, my impression is very positive.</p>



<p>Using <strong>Gemini CLI in Visual Studio Code</strong> can add a lot of value when you want to analyze projects, review code, organize technical documentation, and work with AI assistance without leaving the editor.</p>



<p>But for that to work well, it helps to be very clear from the start whether you're going to work with an <strong>API key</strong> or with <strong>Vertex AI</strong>. Mixing both paths in the same environment only creates friction.</p>



<p>In my case, the definitive solution was to clean the previous keys, force the use of Vertex AI, and authenticate properly with Google Cloud from the terminal.</p>



<p>And once that was done, the workflow improved significantly.</p>



<h2>Conclusion</h2>



<p>If you're trying to use <strong>Gemini CLI in VS Code</strong> and running into authentication errors, my recommendation is to first check the environment variables and confirm that incompatible access methods aren't coexisting.</p>



<p>Sometimes the difference between everything failing and finally working comes down to a few well-applied commands.</p>



<p>In this case, those commands were enough to transform a confusing environment into a configuration ready to work with <strong>Vertex AI from Visual Studio Code</strong>.</p>
                                    
                        
                                                 
                    
                    
                    