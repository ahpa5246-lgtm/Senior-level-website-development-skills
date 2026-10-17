# Design alternatives chosen from content and tasks

Basis: official GOV.UK, Carbon and Adobe Spectrum references in sources.md. Direction families and sample decisions are this framework's synthesis; those organizations do not endorse the proposed palettes or architecture.

## Choose a direction positively

Start with audience, primary task, content volume, reading length, language, brand evidence and device limits. Compare at least two suitable directions using the same real content and main task. Describe grid, hierarchy, type roles, surfaces, interaction patterns and motion. Explain which direction makes the task clearer. Avoid choosing from mood words alone (“premium,” “modern,” “beautiful”).

| Product need | Suitable direction | Concrete alternative to generic card/gradient pages | Reference principle |
| --- | --- | --- | --- |
| Application or public service | Task-led, quiet surfaces | Clear question pages, progress where useful, review-before-submit, confirmation with next steps | GOV.UK check-answers pattern |
| Administrative data tool | Dense but legible workspace | Tables for comparisons, filters, visible sorting, progressive detail, batch actions when needed | Carbon data tables |
| Publication or technical knowledge | Editorial reading layout | Strong type hierarchy, limited reading width, contents navigation and related material | Spectrum typography roles |
| Product catalog | Content-led browsing | Meaningful imagery, facet filters, comparison and clear availability/price | Synthesis; validate with user tasks |
| Portfolio or cultural project | Distinctive editorial composition | Project-led layouts and deliberate type/image relationships, restrained effects | Synthesis; brand-specific research required |

Do not copy a government site's branding into a travel product or a dense enterprise table into a short reading page. Transfer interaction principles, then validate the audience fit. Novelty does not excuse illegible text; consistency does not require every page to have identical composition.

## Color and typography selection

Create semantic roles: canvas, surface, text, muted text, border, action, focus, success, warning and danger. Choose brand accents from actual product context, then test every foreground/background pair in its real state. Purple is acceptable when justified; replacing it with blue changes no structural problem. Status must be understandable without color alone.

Start typography with readable body text in all required scripts, explicit heading roles and limited weights. Test Arabic glyph quality, line-height, punctuation and mixed-script baselines with real content. A restrained system stack minimizes transfer; a licensed Arabic family may be justified for readability or identity. Neither a named font nor a fashionable font guarantees quality. Check licenses and fallback metrics.

Record tokens and examples for spacing, radius, elevation and density. Use whitespace to group content; borders and headings often communicate structure more cheaply than shadows. Cards fit discrete items; tables fit repeated comparable attributes; lists fit scanning; full-width prose fits reading. Let content determine the component.

## Interaction and state design

Use anchors for destinations and buttons for actions. Labels describe outcomes. Distinguish initial empty data, no search results and unavailable data. Preserve input on retry. Give progress for long operations and clear confirmation only after the trusted operation succeeds. Destructive actions need risk-appropriate confirmation or undo.

A dialog requires initial focus, keyboard containment where appropriate, accessible naming, dismissal and focus return. Prefer maintained accessible primitives over handcrafted behavior where complexity warrants it. Ensure errors are associated with fields and announced when necessary. Test with keyboard and a screen reader; automated checks alone do not establish conformance.

## Responsive, Arabic and accessible verification

Target applicable WCAG 2.2 AA criteria. Normal text contrast is generally at least 4.5:1, large text 3:1; applicable non-text UI contrast is 3:1. Target-size requirements include exceptions: use 24x24 CSS pixels as the AA criterion baseline where applicable and consider larger touch targets for comfortable use. Do not claim every WCAG target must be 44 pixels.

Use semantic landmarks, meaningful headings, associated labels and appropriate alt text (empty for decorative images). Provide visible focus, zoom/reflow and reduced-motion behavior. Preserve logical reading and focus order; visual CSS reordering must not break comprehension.

For Arabic set language and direction at appropriate scope, use CSS logical properties, isolate user-generated mixed-direction content with appropriate `bdi`/direction handling, and test prices, dates, URLs and identifiers. Mirror directional navigation deliberately; do not mirror logos or every icon.

Inspect real short/long/empty/error content at narrow widths and zoom, including a 320 CSS-pixel reflow scenario where applicable, mobile touch, desktop keyboard, RTL and LTR. Test actual tasks, not only screenshots. Record manual checks separately from automated results.


## Comparative product evidence (mandatory for meaningful UI)
Start with two or more direct released product references and an aspirational visual system selected from official documentation and screenshots, not just unverified GitHub designs. Compare actual user journeys, not superficial page counts. At each UI milestone, revalidate primary-to-secondary navigation, whether unrelated features were stuffed into a single canvas, density and meaningful whitespace, fonts and Arabic glyph quality, semantic colors, purposeful 2D illustration, and explicit empty/loading/error/success states. Prefer a coherent composition over card wallpaper; avoid forcing multiple screens for a genuinely single-task interface. Record a real competitor-by-feature gap and follow-up changes, date all observations and use `scripts/visual_quality_gate.py` to block a missing evidence manifest. See [the Arabic full protocol](competitive-visual-qa-ar.md); an evidence-structure pass is never equivalent to aesthetic or usability certification.
