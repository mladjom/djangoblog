# Django Blog Theme

This directory contains the theme assets (SCSS and JavaScript) for the Django blog project. It uses modern tooling to compile, optimize, and manage frontend assets.

## 📁 Directory Structure
```
theme/
├── src/
│   ├── scss/
│   │   ├── abstracts/         # Variables, mixins, functions
│   │   ├── base/             # Reset, typography, base styles
│   │   ├── components/       # Buttons, forms, cards
│   │   ├── layout/          # Grid, header, footer, nav
│   │   ├── pages/           # Page-specific styles
│   │   ├── themes/          # Light/dark theme variations
│   │   ├── vendors/         # Third-party styles
│   │   └── main.scss        # Main SCSS entry
│   └── js/
│       └── main.js          # JavaScript entry point
├── package.json             # Dependencies and scripts
├── postcss.config.js        # PostCSS configuration
└── README.md               # This file
```

## 🚀 Quick Start

1. Install dependencies:
```bash
npm install
```

2. Start development:
```bash
npm run watch
```

3. Build for production:
```bash
npm run build
```

## 📜 Available Commands

- `npm run css:dev` - Watch and compile SCSS with source maps
- `npm run css:build` - Compile and optimize CSS for production
- `npm run js:dev` - Watch and bundle JS with source maps
- `npm run js:build` - Bundle and minify JS for production
- `npm run watch` - Run both CSS and JS development watchers
- `npm run build` - Build both CSS and JS for production
- `npm run clean` - Clean output directories

## 🛠️ Technologies Used

- **SASS** - CSS preprocessor
- **PostCSS** - CSS postprocessor with features:
  - Autoprefixer
  - CSS Nesting
  - Media Query Optimization
  - CSS Minification
  - Custom Properties Support
- **esbuild** - JavaScript bundler and minifier

## 📝 Development Guidelines

### SCSS Structure
- Use the 7-1 pattern for SCSS organization
- Follow BEM methodology for class naming
- Keep components modular and reusable
- Use variables from `abstracts/_variables.scss`
- Implement mixins for repeated patterns

### JavaScript Structure
- Write modular JavaScript
- Use ES6+ features
- Keep functions pure when possible
- Comment complex logic
- Handle errors appropriately

## 🎨 Theming

The theme supports both light and dark modes:
- Light theme is the default
- Dark theme is triggered by `.dark-mode` class on `<html>`
- Theme variables are in `themes/_light.scss` and `themes/_dark.scss`

## 💻 Browser Support

Supports modern browsers as defined in `browserslist`:
- Latest Chrome, Firefox, Safari, Edge
- No IE11 support
- Mobile browsers

## 🔧 Customization

### Adding New SCSS Files
1. Create file in appropriate directory
2. Import in `main.scss`
3. Follow existing patterns

### Adding New JavaScript
1. Create modules in `src/js/`
2. Import in `main.js`
3. Use ES6 module syntax

## 📦 Build Output

Compiled assets are output to:
- CSS: `../static/css/main.css`
- JavaScript: `../static/js/main.js`

## ⚠️ Troubleshooting

Common issues and solutions:

1. **SCSS compilation errors**
   - Check syntax
   - Verify import paths
   - Check variable scope

2. **JavaScript bundling issues**
   - Verify module imports
   - Check for syntax errors
   - Ensure dependencies are installed

3. **Source maps not working**
   - Verify dev server configuration
   - Check browser developer tools settings

## 🤝 Contributing

1. Follow existing code style
2. Document changes
3. Test in development
4. Build before committing

## 📃 License

[License Type] - See LICENSE file for details

---

For more information about the Django project structure, see the main README.md in the project root.
