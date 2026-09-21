# Gerko Schrieken — portfolio

Static personal portfolio and Book RPG engineering case study, with links to the Amsterdam 750 project.

## Pages

- `index.html`: personal portfolio
- `book-rpg/index.html`: Book RPG case study
- `styles.css`: shared responsive styling
- `favicon.svg`: site icon
- `.nojekyll`: serve static files without Jekyll

No dependencies or build step are required. All internal links work on GitHub Pages and a custom domain.

## Preview locally

Serve the repository root with a local static web server of your choice, then open
its local address in your browser. No build step, package installation or
project-specific server script is needed.

## Portfolio positioning and contact

The homepage introduces Gerko as a senior software engineer with a background in
.NET, React, TypeScript and Azure. Amsterdam 750 remains the first project;
Book RPG is explicitly described as experimental. Availability for new roles is
stated in the introduction and contact section.

Both pages link to `/#contact`. The contact button opens the existing public
LinkedIn profile at https://nl.linkedin.com/in/gerko-schrieken-b1853246.
No private/account email, contact form, analytics or placeholder CV link is added.
Update the availability text when the job search changes.

## Enable GitHub Pages

In Settings → Pages:

1. Select **Deploy from a branch**.
2. Select **main** and **/(root)**.
3. Click **Save**.

The default address is https://gozzy82.github.io/.

## Connect gerko.amsterdam

First add `gerko.amsterdam` under **Settings → Pages → Custom domain** and save.
GitHub will create the CNAME file for branch publishing. Then replace existing
apex A records with these four GitHub Pages targets:

| Type | Name | Value |
| --- | --- | --- |
| A | gerko.amsterdam | 185.199.108.153 |
| A | gerko.amsterdam | 185.199.109.153 |
| A | gerko.amsterdam | 185.199.110.153 |
| A | gerko.amsterdam | 185.199.111.153 |

For IPv6, replace old apex AAAA records with these GitHub Pages targets:

| Type | Name | Value |
| --- | --- | --- |
| AAAA | gerko.amsterdam | 2606:50c0:8000::153 |
| AAAA | gerko.amsterdam | 2606:50c0:8001::153 |
| AAAA | gerko.amsterdam | 2606:50c0:8002::153 |
| AAAA | gerko.amsterdam | 2606:50c0:8003::153 |

Leave mail-related MX, SPF, DKIM and DMARC records intact.
Do not point wildcard records at GitHub Pages.
For www, add a dedicated CNAME from `www.gerko.amsterdam` to `gozzy82.github.io.`.
Once GitHub provisions the certificate, enable **Enforce HTTPS**.

The previous ChatGPT Sites A targets and verification records are not used by this deployment.
DNS propagation and certificate issuance can take time.

Official instructions:
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site

## Content sources

The Amsterdam 750 figures refer to the published five-minute load test with 250 virtual users,
not a general scalability guarantee. Book RPG describes the documented implementation
as reviewed in September 2026; it does not claim an aggregate reliability benchmark.

- https://github.com/Gozzy82/amsterdam750-public
- https://github.com/Gozzy82/book-rpg-public (sanitized source snapshot)
