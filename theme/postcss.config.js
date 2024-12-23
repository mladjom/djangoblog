module.exports = {
    plugins: [
      require('postcss-import'),
      require('postcss-preset-env')({
        stage: 1,
        features: {
          'nesting-rules': true,
          'custom-properties': true,
          'custom-media-queries': true,
        },
        autoprefixer: {
          grid: true,
          flexbox: 'no-2009'
        }
      }),
      require('postcss-combine-media-query'),
      require('postcss-sort-media-queries')({
        sort: 'mobile-first'
      }),
      require('cssnano')({
        preset: ['default', {
          discardComments: {
            removeAll: true,
          },
          normalizeWhitespace: false,
          colormin: true,
          minifyFontValues: true,
          minifyGradients: true,
          minifyParams: true,
          minifySelectors: true,
          mergeLonghand: true,
          mergeRules: true,
        }]
      })
    ]
  };