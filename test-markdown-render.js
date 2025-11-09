/**
 * Node.js test script for markdown rendering
 * Tests the markdown renderer without needing a browser
 */

const fs = require('fs');
const path = require('path');

// Mock browser globals for Node.js environment
global.window = global;
global.document = {
    createElement: () => ({ style: {}, select: () => {}, remove: () => {} }),
    body: { appendChild: () => {}, removeChild: () => {} },
    execCommand: () => true
};
global.navigator = {
    clipboard: null
};

// Load marked.js
const markedCode = fs.readFileSync(path.join(__dirname, 'static', 'lib', 'marked.min.js'), 'utf8');
eval(markedCode);

// Load highlight.js
const hlCode = fs.readFileSync(path.join(__dirname, 'static', 'lib', 'highlight.min.js'), 'utf8');
eval(hlCode);

// Load markdown-renderer.js
const rendererCode = fs.readFileSync(path.join(__dirname, 'static', 'js', 'markdown-renderer.js'), 'utf8');
eval(rendererCode);

// Test markdown content
const testMarkdown = `# Sample Response

Here's a **bold** statement with *italic* text.

## Code Example
\`\`\`python
def hello_world():
    print("Hello, World!")
\`\`\`

## Inline Code
You can use \`console.log()\` to debug JavaScript.

## Table
| Feature | Status |
|---------|--------|
| Upload  | ✅     |
| Query   | ✅     |

## List Example
1. First item
2. Second item
   - Nested bullet
   - Another bullet
3. Third item

## Blockquote
> This is a quote from someone important.
> It spans multiple lines.

## Links
Check out [Google](https://google.com) for more info.
`;

console.log('Testing Markdown Renderer...\n');

try {
    // Test if renderMarkdown function exists
    if (typeof renderMarkdown !== 'function') {
        throw new Error('renderMarkdown function not found');
    }
    console.log('✓ renderMarkdown function loaded successfully');

    // Render the markdown
    const rendered = renderMarkdown(testMarkdown);
    console.log('✓ Markdown rendered without errors');

    // Verify key features
    const tests = [
        { name: 'Headers (h1) rendered', check: () => rendered.includes('<h1>') },
        { name: 'Headers (h2) rendered', check: () => rendered.includes('<h2>') },
        { name: 'Bold text rendered', check: () => rendered.includes('<strong>') },
        { name: 'Italic text rendered', check: () => rendered.includes('<em>') },
        { name: 'Code blocks present', check: () => rendered.includes('<pre>') && rendered.includes('<code>') },
        { name: 'Code block wrapper present', check: () => rendered.includes('code-block-wrapper') },
        { name: 'Copy button present', check: () => rendered.includes('copy-button') },
        { name: 'Language label present', check: () => rendered.includes('code-language') },
        { name: 'Syntax highlighting applied', check: () => rendered.includes('class="hljs') },
        { name: 'Tables rendered', check: () => rendered.includes('<table>') },
        { name: 'Table wrapper present', check: () => rendered.includes('table-wrapper') },
        { name: 'Ordered lists rendered', check: () => rendered.includes('<ol>') },
        { name: 'Unordered lists rendered', check: () => rendered.includes('<ul>') },
        { name: 'Blockquotes rendered', check: () => rendered.includes('<blockquote>') },
        { name: 'Links rendered', check: () => rendered.includes('<a href') },
        { name: 'External links have target="_blank"', check: () => rendered.includes('target="_blank"') },
        { name: 'Inline code rendered', check: () => rendered.includes('class="inline-code"') }
    ];

    console.log('\nRunning Feature Tests:\n');

    let passedTests = 0;
    let failedTests = 0;

    tests.forEach(test => {
        try {
            const result = test.check();
            if (result) {
                console.log(`  ✓ ${test.name}`);
                passedTests++;
            } else {
                console.log(`  ✗ ${test.name}`);
                failedTests++;
            }
        } catch (error) {
            console.log(`  ✗ ${test.name} (error: ${error.message})`);
            failedTests++;
        }
    });

    console.log(`\n${'='.repeat(50)}`);
    console.log(`Test Results: ${passedTests}/${tests.length} passed`);
    console.log(`${'='.repeat(50)}`);

    if (failedTests === 0) {
        console.log('\n🎉 All tests passed! Markdown rendering working correctly.\n');

        // Write sample output to file
        const outputPath = path.join(__dirname, 'static', 'test-output.html');
        const htmlOutput = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Markdown Render Test Output</title>
    <link rel="stylesheet" href="lib/highlight-github.min.css">
    <link rel="stylesheet" href="css/components/markdown.css">
    <link rel="stylesheet" href="css/components/code-highlight.css">
    <style>
        body { max-width: 800px; margin: 40px auto; padding: 20px; font-family: sans-serif; }
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="color: #667eea; border-bottom: 2px solid #667eea; padding-bottom: 10px;">Markdown Render Test</h1>
        <div class="response-area show">
${rendered}
        </div>
    </div>
    <script src="lib/marked.min.js"></script>
    <script src="lib/highlight.min.js"></script>
    <script src="js/markdown-renderer.js"></script>
</body>
</html>`;

        fs.writeFileSync(outputPath, htmlOutput);
        console.log(`Sample output written to: ${outputPath}`);
        console.log('Open this file in a browser to see the rendered output.\n');

        process.exit(0);
    } else {
        console.log(`\n❌ ${failedTests} test(s) failed.\n`);
        process.exit(1);
    }

} catch (error) {
    console.error('\n❌ Error:', error.message);
    console.error(error.stack);
    process.exit(1);
}
